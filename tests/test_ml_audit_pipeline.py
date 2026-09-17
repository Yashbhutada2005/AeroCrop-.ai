"""
AeroCrop.ai — Comprehensive ML Audit & Multi-Task Synchronization Test Suite
Validates model architecture, tensor shapes, gradient synchronization across parameter groups,
dying ReLU prevention in yield regression head, deterministic validation pairing, and preprocessing parity.
"""

import os
import sys
import pytest
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from model.architecture import MultiModalAeroCropNet, TabularEncoder
from model.dataset import MultiModalDataset, TRAIN_TRANSFORM, VAL_TRANSFORM
from model.inference import InferenceService, IMAGE_TRANSFORM


class TestModelArchitectureAndShapes:
    """Audit Section 2 & 14: Verify exact tensor dimensions at all network stages."""

    @pytest.fixture
    def model(self):
        return MultiModalAeroCropNet(
            num_classes=134,
            tabular_input_dim=config.TABULAR_INPUT_DIM,
            pretrained=False,
        )

    def test_tensor_shapes_at_all_stages(self, model):
        batch_size = 4
        img = torch.randn(batch_size, 3, config.IMAGE_SIZE, config.IMAGE_SIZE)
        tab = torch.randn(batch_size, config.TABULAR_INPUT_DIM)

        # Stage 1: Visual Encoder
        v = model.visual_encoder(img)
        assert v.shape == (batch_size, 512, 1, 1), f"Unexpected visual encoder output: {v.shape}"
        v_flat = v.view(v.size(0), -1)
        assert v_flat.shape == (batch_size, 512)

        # Stage 2: Tabular Encoder
        t = model.tabular_encoder(tab)
        assert t.shape == (batch_size, 64), f"Unexpected tabular encoder output: {t.shape}"

        # Stage 3: Fusion
        fused = torch.cat([v_flat, t], dim=1)
        assert fused.shape == (batch_size, 576), f"Unexpected concat shape: {fused.shape}"
        shared = model.fusion(fused)
        assert shared.shape == (batch_size, 128), f"Unexpected fusion embedding shape: {shared.shape}"

        # Stage 4: Task Heads
        disease_logits = model.disease_head(shared)
        yield_pred = model.yield_head(shared)
        assert disease_logits.shape == (batch_size, 134), f"Disease logits shape mismatch: {disease_logits.shape}"
        assert yield_pred.shape == (batch_size, 1), f"Yield output shape mismatch: {yield_pred.shape}"

    def test_forward_pass_returns_raw_logits_and_non_negative_yield(self, model):
        img = torch.randn(2, 3, 224, 224)
        tab = torch.randn(2, 3)
        logits, yield_pred = model(img, tab)

        # Check raw logits (should have both positive and negative unbounded values)
        assert logits.shape == (2, 134)
        assert not torch.all(logits >= 0), "Logits should be raw unbounded values, not softmax probabilities"

        # Check non-negativity of yield output (via Softplus)
        assert yield_pred.shape == (2, 1)
        assert torch.all(yield_pred >= 0), "Yield prediction must be non-negative"


class TestYieldHeadDyingReLUPrevention:
    """Audit Section 6: Ensure yield regression head does not suffer from dying ReLU gradient freeze."""

    def test_softplus_activation_ensures_strictly_positive_gradients(self):
        model = MultiModalAeroCropNet(num_classes=134, tabular_input_dim=3, pretrained=False)
        model.train()

        img = torch.randn(4, 3, 224, 224)
        tab = torch.randn(4, 3)
        yield_true = torch.tensor([[15.0], [25.0], [35.0], [45.0]], dtype=torch.float32)

        crit_reg = nn.SmoothL1Loss(beta=1.0)
        model.zero_grad()
        _, yield_pred = model(img, tab)
        loss = crit_reg(yield_pred, yield_true)
        loss.backward()

        # Check terminal linear layer gradients in yield head
        terminal_weight_grad = model.yield_head[2].weight.grad
        assert terminal_weight_grad is not None, "Yield head terminal weight gradient must not be None"
        assert terminal_weight_grad.norm().item() > 1e-6, (
            f"Yield head gradient norm is zero ({terminal_weight_grad.norm().item()}). Dying ReLU bug detected!"
        )

        # Check pre-terminal linear layer gradients in yield head
        hidden_weight_grad = model.yield_head[0].weight.grad
        assert hidden_weight_grad is not None
        assert hidden_weight_grad.norm().item() > 1e-6

    def test_bias_initialization_prevents_zero_prediction_collapse(self):
        model = MultiModalAeroCropNet(num_classes=134, tabular_input_dim=3, pretrained=False)
        model.eval()

        img = torch.randn(4, 3, 224, 224)
        tab = torch.randn(4, 3)
        _, yield_pred = model(img, tab)

        # Pre-initialized bias ensures predictions start in realistic positive territory
        assert torch.all(yield_pred > 0.5), (
            f"Initial yield predictions are near zero ({yield_pred.squeeze().tolist()}), indicating cold collapse."
        )


class TestGradientSynchronizationAcrossParameterGroups:
    """Audit Section 3 & 15: Verify multi-task gradient propagation across parameter groups."""

    @pytest.fixture
    def setup_model_and_batch(self):
        torch.manual_seed(42)
        model = MultiModalAeroCropNet(num_classes=134, tabular_input_dim=3, pretrained=False)
        model.eval()  # Eval mode to disable dropout for strict determinism

        img = torch.randn(4, 3, 224, 224)
        tab = torch.randn(4, 3)
        labels = torch.tensor([0, 1, 2, 3], dtype=torch.long)
        yield_true = torch.tensor([[10.0], [20.0], [30.0], [40.0]], dtype=torch.float32)

        crit_cls = nn.CrossEntropyLoss()
        crit_reg = nn.SmoothL1Loss(beta=1.0)
        return model, img, tab, labels, yield_true, crit_cls, crit_reg

    def test_disease_loss_only_gradient_flow(self, setup_model_and_batch):
        model, img, tab, labels, _, crit_cls, _ = setup_model_and_batch
        model.zero_grad()

        logits, _ = model(img, tab)
        loss_cls = crit_cls(logits, labels)
        loss_cls.backward()

        # ResNet, MLP, Fusion, and Disease Head MUST receive gradients
        assert model.visual_encoder[0].weight.grad.norm().item() > 0
        assert model.tabular_encoder.network[0].weight.grad.norm().item() > 0
        assert model.fusion[0].weight.grad.norm().item() > 0
        assert model.disease_head.weight.grad.norm().item() > 0

        # Yield Head MUST NOT receive gradients from disease loss alone
        assert model.yield_head[0].weight.grad is None
        assert model.yield_head[2].weight.grad is None

    def test_yield_loss_only_gradient_flow(self, setup_model_and_batch):
        model, img, tab, _, yield_true, _, crit_reg = setup_model_and_batch
        model.zero_grad()

        _, yield_pred = model(img, tab)
        loss_reg = crit_reg(yield_pred, yield_true)
        loss_reg.backward()

        # ResNet, MLP, Fusion, and Yield Head MUST receive gradients
        assert model.visual_encoder[0].weight.grad.norm().item() > 0
        assert model.tabular_encoder.network[0].weight.grad.norm().item() > 0
        assert model.fusion[0].weight.grad.norm().item() > 0
        assert model.yield_head[0].weight.grad.norm().item() > 0
        assert model.yield_head[2].weight.grad.norm().item() > 0

        # Disease Head MUST NOT receive gradients from yield loss alone
        assert model.disease_head.weight.grad is None

    def test_combined_loss_synchronization(self, setup_model_and_batch):
        model, img, tab, labels, yield_true, crit_cls, crit_reg = setup_model_and_batch
        model.zero_grad()

        logits, yield_pred = model(img, tab)
        loss_total = 1.0 * crit_cls(logits, labels) + 0.2 * crit_reg(yield_pred, yield_true)
        loss_total.backward()

        # ALL 5 groups MUST receive non-zero gradients under joint training
        assert model.visual_encoder[0].weight.grad.norm().item() > 0, "ResNet backbone failed to receive joint gradient"
        assert model.tabular_encoder.network[0].weight.grad.norm().item() > 0, "Tabular encoder failed to receive joint gradient"
        assert model.fusion[0].weight.grad.norm().item() > 0, "Fusion layer failed to receive joint gradient"
        assert model.disease_head.weight.grad.norm().item() > 0, "Disease head failed to receive joint gradient"
        assert model.yield_head[2].weight.grad.norm().item() > 0, "Yield head failed to receive joint gradient"


class TestDatasetAndPreprocessingParity:
    """Audit Section 4, 8 & 9: Verify dataset pairing, deterministic validation, and preprocessing consistency."""

    def test_validation_pairing_is_strictly_deterministic(self):
        val_dir = os.path.join(config.DATA_DIR, "main dataset", "valid")
        yield_csv = os.path.join(config.DATA_DIR, "crop_yield.csv")
        if not os.path.exists(val_dir) or not os.path.exists(yield_csv):
            pytest.skip("Dataset files not available for local dataset pairing test")

        val_ds = MultiModalDataset(
            image_root=val_dir,
            yield_csv=yield_csv,
            split="val",
            transform=VAL_TRANSFORM,
            max_per_class=2,
        )

        # Accessing the same validation index twice MUST return the exact same tabular row and yield
        img1, tab1, lbl1, y1 = val_ds[0]
        img2, tab2, lbl2, y2 = val_ds[0]

        assert torch.allclose(tab1, tab2), "Validation tabular record varied across accesses! Must be deterministic."
        assert torch.allclose(y1, y2), "Validation yield target varied across accesses! Must be deterministic."
        assert lbl1 == lbl2

    def test_image_transform_parity_between_training_val_and_inference(self):
        # Create a synthetic PIL RGB image
        img = Image.new("RGB", (300, 300), color=(100, 150, 200))
        t_val = VAL_TRANSFORM(img)
        t_inf = IMAGE_TRANSFORM(img)

        assert t_val.shape == t_inf.shape == (3, config.IMAGE_SIZE, config.IMAGE_SIZE)
        assert torch.allclose(t_val, t_inf, atol=1e-5), (
            "Preprocessing mismatch between VAL_TRANSFORM and IMAGE_TRANSFORM!"
        )


class TestCheckpointAndInferenceIntegration:
    """Audit Section 12 & 13: Verify checkpoint loading and inference service."""

    def test_checkpoint_state_dict_matches_architecture(self):
        weights_path = config.WEIGHTS_PATH
        if not os.path.exists(weights_path):
            pytest.skip("Production weights file not present")

        model = MultiModalAeroCropNet(num_classes=134, tabular_input_dim=3, pretrained=False)
        checkpoint = torch.load(weights_path, map_location="cpu", weights_only=True)
        state_dict = checkpoint.get("model_state_dict", checkpoint)

        # Filter out old mismatched final layer if present, or load compatible keys
        incompatible = model.load_state_dict(state_dict, strict=False)
        # Verify ResNet and tabular encoders loaded without missing backbone weights
        missing_backbone = [k for k in incompatible.missing_keys if "visual_encoder" in k or "tabular_encoder" in k]
        assert len(missing_backbone) == 0, f"Backbone missing keys: {missing_backbone}"

    def test_inference_service_single_forward_pass(self):
        svc = InferenceService()
        assert svc is not None
        assert svc.model is not None

        # Simulate synthetic image bytes
        from io import BytesIO
        img = Image.new("RGB", (224, 224), color=(50, 120, 60))
        buf = BytesIO()
        img.save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        res = svc.predict(
            image_bytes=raw_bytes,
            temperature=26.0,
            humidity=65.0,
            rainfall=5.0,
            crop="auto",
        )

        assert "disease_class" in res
        assert "confidence" in res
        assert "yield_t_ha" in res
        assert "probabilities" in res
        assert 0 <= res["disease_class"] < 134
        assert res["yield_t_ha"] >= 0.1
        assert res["confidence"] >= 0.0
