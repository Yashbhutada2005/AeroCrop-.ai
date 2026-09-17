"""
tests/test_no_npk_verification.py — Zero-NPK Architectural Guarantee Tests

Ensures that the entire AeroCrop.ai platform has zero dependency on:
- Nitrogen (N), Phosphorus (P), Potassium (K), NPK
- Soil nutrient values, calculations, or deficit models
- Fertilizer dosage calculations (Urea, DAP, MOP, SSP)
- ICAR NPK targets and bag math
"""

import os
import io
import pytest
import torch
from PIL import Image
from fastapi.testclient import TestClient

import config
from main import app
from model.architecture import MultiModalAeroCropNet
from model.inference import InferenceService

client = TestClient(app)


def test_config_tabular_dimensions():
    """Config must specify strictly 3 tabular features (weather only)."""
    assert config.TABULAR_INPUT_DIM == 3
    assert config.WEATHER_FEATURES == ["temperature", "humidity", "rainfall"]
    assert set(config.TABULAR_NORM.keys()) == {"temperature", "humidity", "rainfall"}


def test_config_no_fertilizer_or_npk_constants():
    """No NPK targets, fertilizer compositions, or bag prices in config."""
    assert not hasattr(config, "CROP_NPK_TARGETS")
    assert not hasattr(config, "FERTILIZER_COMPOSITION")
    assert not hasattr(config, "FERTILIZER_BAG_PRICES")


def test_fertilizer_service_file_deleted():
    """backend/services/fertilizer_service.py must not exist."""
    path = os.path.join(config.BASE_DIR, "services", "fertilizer_service.py")
    assert not os.path.exists(path), f"Found unwanted file: {path}"


def test_model_tabular_encoder_dimension():
    """MultiModalAeroCropNet TabularEncoder must strictly accept 3 features."""
    net = MultiModalAeroCropNet(num_classes=134, tabular_input_dim=3)
    assert net.tabular_encoder.network[0].in_features == 3

    # Valid 3-feature input forward pass
    img = torch.randn(2, 3, 224, 224)
    weather = torch.randn(2, 3)
    disease_logits, yield_pred = net(img, weather)

    assert disease_logits.shape == (2, 134)
    assert yield_pred.shape == (2, 1)

    # 6-feature input must fail
    old_tensor = torch.randn(2, 6)
    with pytest.raises(RuntimeError):
        net(img, old_tensor)


def test_inference_service_no_npk():
    """InferenceService must process weather-only inputs and return no fertilizer data."""
    svc = InferenceService()

    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    result = svc.predict(
        image_bytes=buf.getvalue(),
        temperature=28.0,
        humidity=70.0,
        rainfall=50.0,
        crop="Tomato",
    )

    assert "disease_class" in result
    assert "yield_t_ha" in result
    assert "fertilizer" not in result
    assert "npk" not in result


def test_api_predict_has_no_fertilizer_data():
    """POST /api/predict must succeed with weather only and output zero fertilizer fields."""
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    res = client.post(
        "/api/predict",
        data={
            "crop": "tomato",
            "district": "pune",
        },
        files={"image": ("leaf.jpg", buf, "image/jpeg")},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "disease" in data
    assert "yield_t_ha" in data
    assert "fertilizer" not in data
    assert "soil" not in data


def test_plot_model_schema_no_npk():
    """FarmPlot and DiagnosisRecord schemas must not contain baseline NPK or fertilizer fields."""
    from backend.database.models import FarmPlot, DiagnosisRecord

    plot_fields = FarmPlot.model_fields
    assert "baseline_N" not in plot_fields
    assert "baseline_P" not in plot_fields
    assert "baseline_K" not in plot_fields
    assert "soil_n" not in plot_fields

    diag_fields = DiagnosisRecord.model_fields
    assert "fertilizer" not in diag_fields
    assert "soil" not in diag_fields
