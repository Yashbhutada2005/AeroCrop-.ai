"""
AeroCrop.ai — Inference Service (Model Layer)

Responsibilities:
  - Load model weights from disk (WEIGHTS_PATH from config)
  - Preprocess input image and tabular tensor
  - Run forward pass on GPU/CPU
  - If weights are absent → fall back to deterministic mock inference
    (ensures the web application works immediately without training)
"""

from __future__ import annotations
import os
import sys
import logging
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from torchvision import transforms

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from model.architecture import MultiModalAeroCropNet

logger = logging.getLogger(__name__)

# ─── Image preprocessing pipeline (matches ResNet-18 training config) ────────
IMAGE_TRANSFORM = transforms.Compose([
    transforms.Resize((config.IMAGE_SIZE, config.IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


# ─── Crop to Disease Class Mapping (Aligned with model/classes.json — 134 classes) ───
CROP_TO_CLASSES: dict[str, list[int]] = {
    "banana":    list(range(0, 12)),     # 0..11   (12 classes)
    "corn":      list(range(12, 23)),    # 12..22  (11 classes)
    "maize":     list(range(12, 23)),    # 12..22  (11 classes)
    "cotton":    list(range(23, 38)),    # 23..37  (15 classes)
    "citrus":    list(range(38, 51)),    # 38..50  (13 classes)
    "orange":    list(range(38, 51)),    # 38..50  (13 classes)
    "potato":    list(range(51, 69)),    # 51..68  (18 classes)
    "rice":      list(range(69, 80)),    # 69..79  (11 classes)
    "paddy":     list(range(69, 80)),    # 69..79  (11 classes)
    "soybean":   list(range(80, 91)),    # 80..90  (11 classes)
    "sugarcane": list(range(91, 103)),   # 91..102 (12 classes)
    "tomato":    list(range(103, 113)),  # 103..112 (10 classes)
    "turmeric":  list(range(113, 123)),  # 113..122 (10 classes)
    "haldi":     list(range(113, 123)),  # 113..122 (10 classes)
    "wheat":     list(range(123, 134)),  # 123..133 (11 classes)
}

# ─── Supported Agricultural Crops in Active Scope (All 134 classes) ──────────
SUPPORTED_CROP_CLASSES: list[int] = list(range(134))



class InferenceService:
    """
    Singleton inference service loaded once at application startup.
    """

    _instance: "InferenceService | None" = None

    def __new__(cls) -> "InferenceService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return
        self.device = torch.device(config.DEVICE)
        self.model: MultiModalAeroCropNet | None = None
        self.mock_mode: bool = True
        self.classes: list[str] = []
        self._load_model()
        self._initialised = True

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_model(self, weights_path: str | None = None):
        """Attempt to load saved weights; fall back to mock mode if unavailable."""
        resolved_path = weights_path or os.environ.get("AEROCROP_WEIGHTS_PATH") or config.WEIGHTS_PATH
        if not os.path.exists(resolved_path):
            alt = os.path.join(config.MODEL_DIR, str(resolved_path))
            if os.path.exists(alt):
                resolved_path = alt

        # Load class names from model/classes.json if present
        classes_path = os.path.join(config.MODEL_DIR, "classes.json")
        if os.path.exists(classes_path):
            try:
                import json
                with open(classes_path, "r", encoding="utf-8") as f:
                    self.classes = json.load(f)
            except Exception:
                self.classes = []

        num_classes = len(self.classes) if self.classes else getattr(config, "NUM_DISEASE_CLASSES", 134)

        if os.path.exists(resolved_path):
            try:
                state = torch.load(
                    resolved_path,
                    map_location=self.device,
                    weights_only=False,
                )
                if "disease_head.weight" in state:
                    num_classes = state["disease_head.weight"].shape[0]

                self.model = MultiModalAeroCropNet(
                    num_classes=num_classes,
                    tabular_input_dim=config.TABULAR_INPUT_DIM,
                    pretrained=False,
                ).to(self.device)

                self.model.load_state_dict(state)
                self.model.eval()
                self.mock_mode = False
                self.num_classes = num_classes
                self.active_weights_path = str(resolved_path)
                logger.info("[InferenceService] Loaded weights from %s (%d classes)", resolved_path, num_classes)
            except Exception as exc:
                logger.warning("[InferenceService] Failed to load weights: %s — using mock mode", exc)
                self.mock_mode = True
                self.model = MultiModalAeroCropNet(
                    num_classes=num_classes,
                    tabular_input_dim=config.TABULAR_INPUT_DIM,
                    pretrained=False,
                ).to(self.device)
        else:
            logger.info(
                "[InferenceService] No weights at %s — running in mock inference mode.",
                resolved_path,
            )
            self.mock_mode = True
            self.model = MultiModalAeroCropNet(
                num_classes=num_classes,
                tabular_input_dim=config.TABULAR_INPUT_DIM,
                pretrained=False,
            ).to(self.device)

    @staticmethod
    def _normalise_tabular(
        temperature: float,
        humidity: float,
        rainfall: float,
    ) -> torch.Tensor:
        """Z-score normalise raw weather tabular inputs using constants from config."""
        norm = config.TABULAR_NORM
        raw = [
            (temperature - norm["temperature"]["mean"]) / norm["temperature"]["std"],
            (humidity   - norm["humidity"]["mean"])    / norm["humidity"]["std"],
            (rainfall   - norm["rainfall"]["mean"])    / norm["rainfall"]["std"],
        ]
        return torch.tensor(raw, dtype=torch.float32).unsqueeze(0)  # (1, 3)

    # ── Public API ───────────────────────────────────────────────────────────

    def predict(
        self,
        image_bytes: bytes,
        temperature: float,
        humidity: float,
        rainfall: float,
        crop: str,
    ) -> dict[str, Any]:
        """
        Run full multi-modal inference (leaf photograph + weather telemetry).
        """
        if self.mock_mode:
            return self._mock_predict(temperature, humidity, rainfall, crop)

        # ── Real inference ────────────────────────────────────────────────
        from io import BytesIO
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img_tensor = IMAGE_TRANSFORM(img).unsqueeze(0).to(self.device)       # (1,3,224,224)
        tab_tensor = self._normalise_tabular(temperature, humidity, rainfall).to(self.device)

        with torch.no_grad():
            logits, yield_raw = self.model(img_tensor, tab_tensor)

        # Calibrated temperature scaling (T=0.70) to produce realistic, sharp confidence estimates
        T = 0.70
        global_probs = F.softmax(logits / T, dim=1).squeeze(0).cpu().tolist()
        crop_lower = crop.lower().strip() if crop else "auto"

        num_logits = logits.size(1)
        if crop_lower != "auto" and crop_lower in CROP_TO_CLASSES:
            candidates = [c for c in CROP_TO_CLASSES[crop_lower] if c < num_logits]
            if not candidates:
                candidates = list(range(num_logits))
            cand_tensor = torch.tensor(candidates, device=logits.device)
            sub_logits = logits[0, cand_tensor]
            sub_probs = F.softmax(sub_logits / T, dim=0).cpu().tolist()
            best_sub_idx = int(torch.argmax(sub_logits).item())
            cls_idx = candidates[best_sub_idx]
            conf = float(sub_probs[best_sub_idx])
            probs = global_probs
        elif crop_lower == "auto":
            # In auto-detect mode, constrain prediction to supported agricultural project crops
            candidates = [c for c in SUPPORTED_CROP_CLASSES if c < num_logits]
            if not candidates:
                candidates = list(range(num_logits))
            cand_tensor = torch.tensor(candidates, device=logits.device)
            sub_logits = logits[0, cand_tensor]
            sub_probs = F.softmax(sub_logits / T, dim=0).cpu().tolist()
            best_sub_idx = int(torch.argmax(sub_logits).item())
            cls_idx = candidates[best_sub_idx]
            conf = float(sub_probs[best_sub_idx])
            probs = global_probs
        else:
            # Fallback direct multi-class prediction
            direct_cls = int(torch.argmax(logits, dim=1).item())
            cls_idx = direct_cls
            conf = float(global_probs[cls_idx]) if cls_idx < len(global_probs) else 0.0
            probs = global_probs

        yield_val = float(yield_raw.squeeze().item())

        # Agronomic safety bounds per crop (t/ha) to prevent anomalous regression outputs
        MAX_CROP_YIELDS = {
            "sugarcane": 140.0,
            "banana": 90.0,
            "potato": 45.0,
            "tomato": 50.0,
            "onion": 40.0,
            "maize": 15.0,
            "rice": 12.0,
            "wheat": 8.0,
            "cotton": 6.0,
            "soybean": 5.0,
            "turmeric": 15.0,
        }
        effective_crop = crop_lower
        if effective_crop not in MAX_CROP_YIELDS and self.classes and cls_idx < len(self.classes):
            cls_name = self.classes[cls_idx]
            prefix = cls_name.split("___")[0].lower()
            if "corn" in prefix:
                prefix = "maize"
            effective_crop = prefix

        max_cap = MAX_CROP_YIELDS.get(effective_crop, 50.0)
        yield_val = max(0.1, min(yield_val, max_cap))

        return {
            "disease_class":  cls_idx,
            "probabilities":  probs,
            "confidence":     conf,
            "yield_t_ha":     round(yield_val, 2),
            "mock":           False,
            "low_confidence": conf < 0.40,
        }

    @staticmethod
    def _mock_predict(
        temperature: float = 25.0,
        humidity: float = 60.0,
        rainfall: float = 0.0,
        crop: str = "tomato",
    ) -> dict[str, Any]:
        """
        Deterministic, agronomically-aware mock inference used when weights
        are not available. Results vary meaningfully based on weather inputs.
        """
        crop_lower = crop.lower().strip() if crop else "auto"
        fingerprint = int(abs(temperature * 7.3 + humidity * 3.7 + rainfall * 5.1))

        num_classes = getattr(config, "NUM_DISEASE_CLASSES", 134)
        if crop_lower != "auto" and crop_lower in CROP_TO_CLASSES:
            candidates = CROP_TO_CLASSES[crop_lower]
            seed_val = candidates[fingerprint % len(candidates)]
        else:
            seed_val = fingerprint % num_classes

        seed_val = seed_val % num_classes
        np.random.seed(seed_val)
        probs_raw = np.random.dirichlet(np.ones(num_classes) * 0.5)
        # Boost the seeded class to simulate a confident prediction
        probs_raw[seed_val] += 1.5
        probs_raw /= probs_raw.sum()
        probs = probs_raw.tolist()
        conf  = float(probs_raw[seed_val])

        # Agronomic yield estimate: base yield scaled by weather suitability
        base_yield = {
            "tomato": 32.0, "orange": 24.0, "apple": 22.0, "grape": 20.0,
            "pepper": 18.0, "strawberry": 16.0, "peach": 16.0, "squash": 22.0,
            "cherry": 12.0, "blueberry": 9.0, "raspberry": 8.0, "soybean": 2.2,
            "maize": 4.5, "potato": 20.0, "cotton": 2.0, "wheat": 3.2, "rice": 4.0,
            "sugarcane": 85.0, "banana": 48.0, "turmeric": 6.5, "onion": 18.0,
        }
        base = base_yield.get(crop_lower, 25.0)
        weather_pen  = 1.0 - abs(temperature - 28) * 0.01 - max(0, rainfall - 15) * 0.005 - max(0, abs(humidity - 65) - 20) * 0.003
        weather_pen  = max(0.4, min(1.0, weather_pen))
        yield_val    = round(base * weather_pen, 2)

        return {
            "disease_class":  seed_val,
            "probabilities":  probs,
            "confidence":     round(conf, 4),
            "yield_t_ha":     yield_val,
            "mock":           True,
            "low_confidence": conf < 0.35,
        }
