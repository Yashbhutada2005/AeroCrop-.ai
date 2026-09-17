"""
AeroCrop.ai — Model Training Pipeline (Model Layer)

Trains MultiModalAeroCropNet using:
  - Disease images:  Multi-Source Agricultural Pathology Dataset — 166,630 images, 134 classes across 11 crops
  - Yield tabular:   yield_df.csv — FAO yield + meteorological telemetry

Features & Optimizations:
  - Automatic Mixed Precision (AMP) for 2.5x speedup and reduced VRAM on NVIDIA GPUs
  - Robust dataset auto-discovery (handles single and double nested directories)
  - Huber / SmoothL1 loss for stable yield regression
  - Transfer learning enabled by default (ImageNet ResNet-18 backbone)
  - Safe interruption handling (preserves best model on Ctrl+C)
  - Saves best weights to model/aerocrop_weights.pth and latest checkpoint

Usage:
    python model/train.py --epochs 15 --batch_size 32
"""

from __future__ import annotations
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from model.architecture import MultiModalAeroCropNet
from model.dataset import (
    MultiModalDataset,
    PlantDiseaseDataset,
    TRAIN_TRANSFORM,
    VAL_TRANSFORM,
)


# ── Argument Parser ────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="Train AeroCrop.ai MultiModalAeroCropNet on GPU/CPU"
    )
    parser.add_argument(
        "--image_dir",
        type=str,
        default=r"data\main dataset\train",
        help="Path to training image directory",
    )
    parser.add_argument(
        "--val_dir",
        type=str,
        default=r"data\main dataset\valid",
        help="Path to validation image directory",
    )
    parser.add_argument(
        "--yield_csv",
        type=str,
        default=r"data\crop_yield.csv" if os.path.exists(r"data\crop_yield.csv") or os.path.exists(os.path.join(config.DATA_DIR, "crop_yield.csv")) else r"data\yield_df.csv",
        help="Path to crop_yield.csv or yield_df.csv",
    )
    parser.add_argument(
        "--num_classes",
        type=int,
        default=None,
        help="Number of disease classes (default: auto-detect from dataset)",
    )
    parser.add_argument("--epochs",       type=int,   default=15,
                        help="Number of training epochs")
    parser.add_argument("--batch_size",   type=int,   default=64,
                        help="Batch size (64 recommended for RTX 3050 6GB GPU)")
    parser.add_argument("--lr",           type=float, default=1e-4,
                        help="Peak learning rate for AdamW")
    parser.add_argument("--alpha",        type=float, default=1.0,
                        help="Weight for disease classification loss")
    parser.add_argument("--beta",         type=float, default=0.20,
                        help="Weight for yield regression loss (0.20 gives balanced gradient signal)")
    parser.add_argument("--workers",      type=int,   default=min(os.cpu_count() or 4, 4),
                        help="DataLoader num_workers (4 recommended for multi-worker async prefetch)")
    parser.add_argument("--no_pretrained", action="store_true",
                        help="Disable ImageNet pretraining (train from scratch)")
    parser.add_argument("--no_amp",       action="store_true",
                        help="Disable Automatic Mixed Precision (AMP)")
    parser.add_argument("--max_per_class", type=int,  default=None,
                        help="Limit images per class (for rapid validation runs)")
    parser.add_argument("--resume",       type=str,   default=None,
                        help="Path to checkpoint .pth to resume training from")
    parser.add_argument("--output_weights", type=str, default=None,
                        help="Path to save best weights (defaults to config.WEIGHTS_PATH)")
    return parser.parse_args()


# ── Path Resolution Helper ─────────────────────────────────────────────────
def resolve_dir(provided_path: str, fallback_subfolder: str) -> str:
    """Resolve directory checking absolute, relative, and standard candidate paths."""
    p = Path(provided_path)
    if p.is_absolute() and p.exists():
        return str(p)

    rel_base = Path(config.BASE_DIR) / provided_path
    if rel_base.exists():
        return str(rel_base)

    candidates = [
        Path(config.DATA_DIR) / "main dataset" / fallback_subfolder,
        Path(config.DATA_DIR) / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / fallback_subfolder,
        Path(config.DATA_DIR) / "New Plant Diseases Dataset(Augmented)" / fallback_subfolder,
        Path(config.DATA_DIR) / fallback_subfolder,
    ]
    for c in candidates:
        if c.exists() and any(c.iterdir()):
            return str(c)

    return str(rel_base)


def resolve_file(provided_path: str, fallback_filename: str) -> str:
    p = Path(provided_path)
    if p.is_absolute() and p.exists():
        return str(p)

    rel_base = Path(config.BASE_DIR) / provided_path
    if rel_base.exists():
        return str(rel_base)

    alt = Path(config.DATA_DIR) / fallback_filename
    if alt.exists():
        return str(alt)

    return str(rel_base)


def safe_torch_save(obj, target_path: str):
    """Safely saves PyTorch artifacts on Windows using an atomic temporary file replacement with retry."""
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.with_name(f"{target.stem}_tmp_{int(time.time() * 1000)}{target.suffix}")
    try:
        torch.save(obj, str(tmp_path))
    except Exception:
        torch.save(obj, str(target))
        return

    for _ in range(5):
        try:
            os.replace(str(tmp_path), str(target))
            return
        except (PermissionError, OSError):
            time.sleep(0.3)

    try:
        import shutil
        shutil.copy2(str(tmp_path), str(target))
        if tmp_path.exists():
            tmp_path.unlink()
    except Exception as e:
        print(f"  [Warning] Failed to replace {target}: {e}")


# ── Metrics Tracking ───────────────────────────────────────────────────────
class MetricsTracker:
    def __init__(self, num_classes: int = 134):
        self.num_classes = num_classes
        self.reset()

    def reset(self):
        self.total, self.correct, self.loss_sum = 0, 0, 0.0
        self.loss_cls_sum, self.loss_reg_sum = 0.0, 0.0
        self.yield_mse_sum, self.yield_mae_sum, self.n_batches = 0.0, 0.0, 0
        self.confusion_matrix = torch.zeros((self.num_classes, self.num_classes), dtype=torch.int64)

    def update(self, logits, labels, yield_pred, yield_true, loss, loss_cls=None, loss_reg=None):
        preds = logits.argmax(dim=1)
        self.correct     += (preds == labels).sum().item()
        self.total       += labels.size(0)
        self.loss_sum    += loss.item()
        if loss_cls is not None:
            self.loss_cls_sum += loss_cls.item()
        if loss_reg is not None:
            self.loss_reg_sum += loss_reg.item()
        self.n_batches   += 1
        if yield_pred is not None and yield_true is not None:
            diff = yield_pred - yield_true
            mse = (diff ** 2).mean().item()
            mae = diff.abs().mean().item()
            self.yield_mse_sum += mse
            self.yield_mae_sum += mae

        # Update confusion matrix for precision & F1 computation
        p_cpu = preds.detach().cpu()
        l_cpu = labels.detach().cpu()
        mask = (l_cpu >= 0) & (l_cpu < self.num_classes) & (p_cpu >= 0) & (p_cpu < self.num_classes)
        indices = l_cpu[mask] * self.num_classes + p_cpu[mask]
        bincount = torch.bincount(indices, minlength=self.num_classes * self.num_classes)
        self.confusion_matrix += bincount.reshape(self.num_classes, self.num_classes)

    @property
    def accuracy(self):
        return 100.0 * self.correct / self.total if self.total else 0.0

    @property
    def avg_loss(self):
        return self.loss_sum / self.n_batches if self.n_batches else 0.0

    @property
    def avg_loss_cls(self):
        return self.loss_cls_sum / self.n_batches if self.n_batches else 0.0

    @property
    def avg_loss_reg(self):
        return self.loss_reg_sum / self.n_batches if self.n_batches else 0.0

    @property
    def avg_yield_rmse(self):
        if self.n_batches == 0 or self.yield_mse_sum == 0.0:
            return None
        mse = self.yield_mse_sum / self.n_batches
        return mse ** 0.5

    @property
    def avg_yield_mae(self):
        if self.n_batches == 0 or self.yield_mae_sum == 0.0:
            return None
        return self.yield_mae_sum / self.n_batches

    @property
    def precision_macro(self):
        """Macro Precision (%) across active predicted classes."""
        tp = self.confusion_matrix.diag().float()
        pred_pos = self.confusion_matrix.sum(dim=0).float()
        active = pred_pos > 0
        if not active.any():
            return 0.0
        prec = tp[active] / pred_pos[active]
        return float(prec.mean().item()) * 100.0

    @property
    def recall_macro(self):
        """Macro Recall (%) across active ground truth classes."""
        tp = self.confusion_matrix.diag().float()
        actual_pos = self.confusion_matrix.sum(dim=1).float()
        active = actual_pos > 0
        if not active.any():
            return 0.0
        rec = tp[active] / actual_pos[active]
        return float(rec.mean().item()) * 100.0

    @property
    def f1_macro(self):
        """Macro F1-score (%) across classes."""
        tp = self.confusion_matrix.diag().float()
        pred_pos = self.confusion_matrix.sum(dim=0).float()
        actual_pos = self.confusion_matrix.sum(dim=1).float()
        active = (pred_pos + actual_pos) > 0
        if not active.any():
            return 0.0
        prec = torch.zeros_like(tp)
        rec = torch.zeros_like(tp)
        prec[pred_pos > 0] = tp[pred_pos > 0] / pred_pos[pred_pos > 0]
        rec[actual_pos > 0] = tp[actual_pos > 0] / actual_pos[actual_pos > 0]
        denom = prec + rec
        f1 = torch.zeros_like(tp)
        f1[denom > 0] = 2.0 * (prec[denom > 0] * rec[denom > 0]) / denom[denom > 0]
        return float(f1[active].mean().item()) * 100.0


# ── Training & Validation Loops ───────────────────────────────────────────
def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion_cls: nn.Module,
    criterion_reg: nn.Module,
    scaler: torch.amp.GradScaler | None,
    device: torch.device,
    alpha: float,
    beta: float,
    use_amp: bool,
    epoch: int = 1,
    total_epochs: int = 15,
    num_classes: int = 134,
) -> MetricsTracker:
    model.train()
    tracker = MetricsTracker(num_classes=num_classes)
    total_batches = len(loader)
    report_interval = max(1, min(50, total_batches // 5)) if total_batches > 10 else max(1, total_batches // 2)
    t_start = time.time()

    for step, batch in enumerate(loader, start=1):
        if len(batch) == 4:
            images, tabular, labels, yield_true = batch
            images     = images.to(device, non_blocking=True)
            tabular    = tabular.to(device, non_blocking=True)
            labels     = labels.to(device, non_blocking=True)
            yield_true = yield_true.to(device, non_blocking=True)
        else:
            images, labels = batch
            images     = images.to(device, non_blocking=True)
            tabular    = torch.zeros(images.size(0), config.TABULAR_INPUT_DIM, device=device)
            labels     = labels.to(device, non_blocking=True)
            yield_true = None

        optimizer.zero_grad(set_to_none=True)

        with torch.amp.autocast(device_type=device.type, enabled=(device.type == "cuda" and use_amp)):
            disease_logits, yield_pred = model(images, tabular)
            loss_cls = criterion_cls(disease_logits, labels)
            if yield_true is not None:
                loss_reg = criterion_reg(yield_pred, yield_true)
                loss = alpha * loss_cls + beta * loss_reg
            else:
                loss = loss_cls

        if scaler is not None and scaler.is_enabled():
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()

        loss_reg_val = loss_reg if yield_true is not None else None
        tracker.update(disease_logits, labels, yield_pred, yield_true, loss, loss_cls=loss_cls, loss_reg=loss_reg_val)

        if step % report_interval == 0 or step == total_batches:
            elapsed = time.time() - t_start
            imgs_done = step * loader.batch_size
            speed = imgs_done / max(elapsed, 0.001)
            sys.stdout.write(
                f"\r    [Ep {epoch}/{total_epochs}] Batch {step:>4}/{total_batches} "
                f"| Loss: {tracker.avg_loss:.4f} | Acc: {tracker.accuracy:.1f}% "
                f"| Prec: {tracker.precision_macro:.1f}% | Speed: {speed:.1f} img/s"
            )
            sys.stdout.flush()

    sys.stdout.write("\n")
    return tracker


@torch.no_grad()
def validate(
    model: nn.Module,
    loader: DataLoader,
    criterion_cls: nn.Module,
    criterion_reg: nn.Module,
    device: torch.device,
    alpha: float,
    beta: float,
    use_amp: bool,
    num_classes: int = 134,
) -> MetricsTracker:
    model.eval()
    tracker = MetricsTracker(num_classes=num_classes)

    for batch in loader:
        if len(batch) == 4:
            images, tabular, labels, yield_true = batch
            images     = images.to(device, non_blocking=True)
            tabular    = tabular.to(device, non_blocking=True)
            labels     = labels.to(device, non_blocking=True)
            yield_true = yield_true.to(device, non_blocking=True)
        else:
            images, labels = batch
            images     = images.to(device, non_blocking=True)
            tabular    = torch.zeros(images.size(0), config.TABULAR_INPUT_DIM, device=device)
            labels     = labels.to(device, non_blocking=True)
            yield_true = None

        with torch.amp.autocast(device_type=device.type, enabled=(device.type == "cuda" and use_amp)):
            disease_logits, yield_pred = model(images, tabular)
            loss_cls = criterion_cls(disease_logits, labels)
            if yield_true is not None:
                loss_reg = criterion_reg(yield_pred, yield_true)
                loss = alpha * loss_cls + beta * loss_reg
            else:
                loss = loss_cls

        loss_reg_val = loss_reg if yield_true is not None else None
        tracker.update(disease_logits, labels, yield_pred, yield_true, loss, loss_cls=loss_cls, loss_reg=loss_reg_val)

    return tracker


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    args   = parse_args()
    device = torch.device(config.DEVICE)
    use_amp = (device.type == "cuda" and not args.no_amp)
    pretrained = not args.no_pretrained

    save_weights_path = resolve_file(args.output_weights, "aerocrop_weights.pth") if args.output_weights else config.WEIGHTS_PATH

    print("\n" + "=" * 68)
    print("  [AeroCrop.ai] High-Performance Neural Training Pipeline")
    print("=" * 68)
    print(f"  Device              : {device} ({torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'})")
    print(f"  Mixed Precision AMP : {'Enabled (FP16/FP32)' if use_amp else 'Disabled'}")
    print(f"  Epochs              : {args.epochs}")
    print(f"  Batch size          : {args.batch_size}")
    print(f"  Learning rate       : {args.lr}")
    print(f"  Target Weights File : {save_weights_path}")
    print(f"  Pretrained backbone : {pretrained}")
    print(f"  Loss balance        : alpha={args.alpha} (cls) + beta={args.beta} (SmoothL1 yield)")
    print("=" * 68 + "\n")

    # ── Hardware Acceleration Optimizations ──────────────────────────────
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass

    # ── Dataset Auto-Resolution ───────────────────────────────────────────
    img_train_abs = resolve_dir(args.image_dir, "train")
    img_val_abs   = resolve_dir(args.val_dir, "valid")
    yield_fallback = "crop_yield.csv" if os.path.exists(os.path.join(config.DATA_DIR, "crop_yield.csv")) else "yield_df.csv"
    yield_csv_abs = resolve_file(args.yield_csv, yield_fallback)

    if not os.path.exists(img_train_abs):
        print(f"[ERROR] Image training directory not found: {img_train_abs}")
        print("  Please ensure data directory is set up or run: python model/extract_data.py")
        sys.exit(1)

    use_multimodal = os.path.exists(yield_csv_abs)

    if use_multimodal:
        print("[Dataset] Mode: MultiModal (RGB Leaf + Tabular Agro-Meteorological Fusion)")
        print(f"  Train images: {img_train_abs}")
        print(f"  Val images  : {img_val_abs}")
        print(f"  Yield table : {yield_csv_abs}")
        train_dataset = MultiModalDataset(
            image_root=img_train_abs,
            yield_csv=yield_csv_abs,
            split="train",
            transform=TRAIN_TRANSFORM,
            max_per_class=args.max_per_class,
        )
        val_dataset = MultiModalDataset(
            image_root=img_val_abs,
            yield_csv=yield_csv_abs,
            split="val",
            transform=VAL_TRANSFORM,
            max_per_class=args.max_per_class,
            classes=train_dataset.classes,
        )
    else:
        print("[Dataset] Mode: Vision-Only (PlantDiseaseDataset)")
        print(f"  Train images: {img_train_abs}")
        train_dataset = PlantDiseaseDataset(
            img_train_abs, transform=TRAIN_TRANSFORM, max_per_class=args.max_per_class
        )
        val_dataset = PlantDiseaseDataset(
            img_val_abs, transform=VAL_TRANSFORM, max_per_class=args.max_per_class,
            classes=train_dataset.classes,
        )

    # Multi-worker async prefetching to saturate GPU
    num_workers = max(0, args.workers)
    loader_kwargs = {
        "num_workers": num_workers,
        "pin_memory": (device.type == "cuda"),
    }
    if num_workers > 0:
        loader_kwargs["persistent_workers"] = True
        loader_kwargs["prefetch_factor"] = 2

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=True,  # Prevent BatchNorm1d error on odd leftover batch
        **loader_kwargs,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        drop_last=False,
        **loader_kwargs,
    )

    num_classes = (
        args.num_classes
        or getattr(train_dataset, "num_classes", None)
        or config.NUM_DISEASE_CLASSES
    )

    print(f"\n  Dataset Size  : {len(train_dataset):,} train samples, {len(val_dataset):,} val samples")
    print(f"  Target Classes: {num_classes} classes")
    print(f"  Batch Batches : {len(train_loader):,} steps per epoch (workers={num_workers})")

    if hasattr(train_dataset, "classes") and train_dataset.classes:
        classes_json_path = os.path.join(config.MODEL_DIR, "classes.json")
        with open(classes_json_path, "w", encoding="utf-8") as f:
            json.dump(train_dataset.classes, f, indent=2)
        print(f"  Class Mapping : Saved {len(train_dataset.classes)} classes to {classes_json_path}")

    # ── Model Initialization ───────────────────────────────────────────────
    model = MultiModalAeroCropNet(
        num_classes=num_classes,
        tabular_input_dim=config.TABULAR_INPUT_DIM,
        pretrained=pretrained,
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Model Params  : {total_params:,} parameters")

    # ── Optimizer, Scheduler & Scaler ──────────────────────────────────────
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    criterion_cls = nn.CrossEntropyLoss(label_smoothing=0.1)
    criterion_reg = nn.SmoothL1Loss(beta=1.0)  # Robust Huber loss for yield

    start_epoch = 1
    best_val_acc = 0.0
    best_val_loss = float("inf")
    best_val_rmse = float("inf")

    # Resume from checkpoint if requested, or warm-start from baseline weights
    if args.resume and os.path.exists(args.resume):
        checkpoint = torch.load(args.resume, map_location=device, weights_only=True)
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
            if "epoch" in checkpoint:
                start_epoch = int(checkpoint["epoch"]) + 1
            if "best_val_acc" in checkpoint:
                best_val_acc = float(checkpoint["best_val_acc"])
            if "best_val_loss" in checkpoint:
                best_val_loss = float(checkpoint["best_val_loss"])
            if "best_val_rmse" in checkpoint:
                best_val_rmse = float(checkpoint["best_val_rmse"])
            if "optimizer_state_dict" in checkpoint:
                try:
                    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
                except Exception as e:
                    print(f"  [Resume Warning] Could not load optimizer state: {e}")
            for pg in optimizer.param_groups:
                pg["lr"] = args.lr
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)
            for _ in range(checkpoint.get("epoch", 0)):
                scheduler.step()
            print(f"\n  [Resume] Loaded checkpoint from {args.resume}")
            print(f"  [Resume] Resuming at Epoch {start_epoch} of {args.epochs} | Best Val Acc: {best_val_acc:.2f}% | Best Loss: {best_val_loss:.4f} | Best Yield RMSE: {best_val_rmse:.4f}")
        else:
            model.load_state_dict(checkpoint)
            print(f"\n  [Resume] Loaded model weights from {args.resume}")

    # ── Metrics CSV Log ────────────────────────────────────────────────────
    output_stem = Path(save_weights_path).stem
    log_filename = f"training_log_{output_stem}.csv" if output_stem != "aerocrop_weights" else "training_log.csv"
    log_path = os.path.join(config.MODEL_DIR, log_filename)
    is_resuming = bool(args.resume and os.path.exists(log_path) and start_epoch > 1)
    log_file = open(log_path, "a" if is_resuming else "w", newline="")
    log_writer = csv.writer(log_file)
    if not is_resuming:
        log_writer.writerow([
            "epoch", "train_loss", "train_loss_cls", "train_loss_reg", "train_acc", "train_prec", "train_f1", "train_yield_rmse", "train_yield_mae",
            "val_loss", "val_loss_cls", "val_loss_reg", "val_acc", "val_prec", "val_f1", "val_yield_rmse", "val_yield_mae", "lr", "elapsed_s", "gpu_mem_mb"
        ])
    else:
        print(f"  Metrics Log   : Appending to existing {log_path} from epoch {start_epoch}")

    t0 = time.time()

    print("\n" + "-" * 118)
    print(f"  {'Ep':>3} | {'TrLoss (Cls/Reg)':>17} | {'TrAcc%':>6} | "
          f"{'VaLoss (Cls/Reg)':>17} | {'VaAcc%':>6} | {'VaPrec%':>7} | {'VaF1%':>6} | {'YldRMSE':>7} | {'YldMAE':>7} | {'Mem(MB)':>7} | {'LR':>8}")
    print("-" * 118)

    try:
        for epoch in range(start_epoch, args.epochs + 1):
            ep_start = time.time()

            tr = train_one_epoch(
                model=model,
                loader=train_loader,
                optimizer=optimizer,
                criterion_cls=criterion_cls,
                criterion_reg=criterion_reg,
                scaler=scaler,
                device=device,
                alpha=args.alpha,
                beta=args.beta,
                use_amp=use_amp,
                epoch=epoch,
                total_epochs=args.epochs,
                num_classes=num_classes,
            )
            va = validate(
                model=model,
                loader=val_loader,
                criterion_cls=criterion_cls,
                criterion_reg=criterion_reg,
                device=device,
                alpha=args.alpha,
                beta=args.beta,
                use_amp=use_amp,
                num_classes=num_classes,
            )
            scheduler.step()

            elapsed = time.time() - ep_start
            lr_now  = scheduler.get_last_lr()[0]
            gpu_mem = round(torch.cuda.memory_reserved() / (1024**2), 1) if device.type == "cuda" else 0.0

            tr_loss_str = f"{tr.avg_loss:.3f} ({tr.avg_loss_cls:.2f}/{tr.avg_loss_reg:.2f})"
            va_loss_str = f"{va.avg_loss:.3f} ({va.avg_loss_cls:.2f}/{va.avg_loss_reg:.2f})"
            rmse_str = f"{va.avg_yield_rmse:>7.4f}" if va.avg_yield_rmse is not None else "    N/A"
            mae_str  = f"{va.avg_yield_mae:>7.4f}"  if va.avg_yield_mae is not None else "    N/A"

            print(f"  {epoch:>3} | {tr_loss_str:>17} | {tr.accuracy:>5.1f}% | "
                  f"{va_loss_str:>17} | {va.accuracy:>5.1f}% | {va.precision_macro:>6.1f}% | {va.f1_macro:>5.1f}% | "
                  f"{rmse_str} | {mae_str} | {gpu_mem:>7.1f} | {lr_now:>8.2e}")

            log_writer.writerow([
                epoch,
                round(tr.avg_loss, 5), round(tr.avg_loss_cls, 5), round(tr.avg_loss_reg, 5),
                round(tr.accuracy, 3), round(tr.precision_macro, 3), round(tr.f1_macro, 3),
                round(tr.avg_yield_rmse, 4) if tr.avg_yield_rmse is not None else "",
                round(tr.avg_yield_mae, 4)  if tr.avg_yield_mae is not None else "",
                round(va.avg_loss, 5), round(va.avg_loss_cls, 5), round(va.avg_loss_reg, 5),
                round(va.accuracy, 3), round(va.precision_macro, 3), round(va.f1_macro, 3),
                round(va.avg_yield_rmse, 4) if va.avg_yield_rmse is not None else "",
                round(va.avg_yield_mae, 4)  if va.avg_yield_mae is not None else "",
                f"{lr_now:.2e}", round(elapsed, 1), gpu_mem,
            ])
            log_file.flush()

            # Save best disease accuracy checkpoint
            if va.accuracy > best_val_acc:
                best_val_acc = va.accuracy
                safe_torch_save(model.state_dict(), save_weights_path)
                print(f"         [BEST ACC] New best val acc: {best_val_acc:.2f}% -> saved to {save_weights_path}")

            # Save best yield RMSE checkpoint
            if va.avg_yield_rmse is not None and va.avg_yield_rmse < best_val_rmse:
                best_val_rmse = va.avg_yield_rmse
                best_yield_path = str(Path(save_weights_path).with_name(f"{Path(save_weights_path).stem}_best_yield.pth"))
                safe_torch_save(model.state_dict(), best_yield_path)
                print(f"         [BEST YIELD] New best val RMSE: {best_val_rmse:.4f} t/ha -> saved to {best_yield_path}")

            # Save best overall multi-task loss checkpoint
            if va.avg_loss < best_val_loss:
                best_val_loss = va.avg_loss
                best_loss_path = str(Path(save_weights_path).with_name(f"{Path(save_weights_path).stem}_best_loss.pth"))
                safe_torch_save(model.state_dict(), best_loss_path)

            # Save latest checkpoint for resumption
            latest_path = os.path.join(config.MODEL_DIR, "checkpoint_latest.pth")
            safe_torch_save({
                "epoch": epoch,
                "best_val_acc": best_val_acc,
                "best_val_loss": best_val_loss,
                "best_val_rmse": best_val_rmse,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
            }, latest_path)

    except KeyboardInterrupt:
        print("\n\n  [Interrupted] Training interrupted by user. Preserving best weights...")
        if best_val_acc > 0 and not os.path.exists(save_weights_path):
            safe_torch_save(model.state_dict(), save_weights_path)
            print(f"  Saved best weights to {save_weights_path}")

    finally:
        total_time = time.time() - t0
        log_file.close()

    print("\n" + "=" * 68)
    print(f"  Training finished in {total_time/60:.1f} minutes")
    print(f"  Best Validation Accuracy : {best_val_acc:.2f}%")
    if os.path.exists(save_weights_path):
        print(f"  Model Weights saved to   : {save_weights_path}")
    print(f"  Metrics Log saved to     : {log_path}")
    print("=" * 68 + "\n")


if __name__ == "__main__":
    main()

