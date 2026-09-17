"""
AeroCrop.ai — Sub-divide Turmeric Classes by Severity Stages
===========================================================
Splits:
1. Turmeric___Leaf_blotch -> Turmeric___Leaf_blotch_mild & Turmeric___Leaf_blotch_severe
2. Turmeric___Leaf_spot   -> Turmeric___Leaf_spot_mild   & Turmeric___Leaf_spot_severe
3. Turmeric___Rhizome_rot -> Turmeric___Rhizome_rot_early & Turmeric___Rhizome_rot_severe

Method: Quantifies diseased / necrotic area percentage via HSV color thresholding,
ranks samples, and splits at the median for both train and valid sets.
Preserves 100% of images without data loss.
"""

import os
import shutil
import numpy as np
from PIL import Image
from pathlib import Path

BASE_DIR  = Path(r"D:\Codes\final_year_project")
TRAIN_DIR = BASE_DIR / "data" / "main dataset" / "train"
VALID_DIR = BASE_DIR / "data" / "main dataset" / "valid"

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

def calc_foliar_severity(img_path):
    try:
        with Image.open(img_path) as im:
            hsv = im.convert('HSV')
            arr = np.array(hsv)
            h, s, v = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            # Lesion pixels: discolored brown/yellow/dark necrotic spots
            necrotic = ((h < 35) | (h > 240) | (v < 60)) & (s > 40)
            return float(np.mean(necrotic))
    except Exception:
        return 0.0

def calc_rhizome_severity(img_path):
    try:
        with Image.open(img_path) as im:
            gray = im.convert('L')
            arr = np.array(gray)
            # Decayed/rotted tissue appears darker and heavily discolored
            rot_pixels = arr < 90
            return float(np.mean(rot_pixels))
    except Exception:
        return 0.0

def split_class(split_dir, src_class, mild_class, severe_class, score_fn):
    src_path = split_dir / src_class
    if not src_path.exists():
        print(f"Skipping {src_class} in {split_dir.name}: folder not found")
        return

    images = [f for f in src_path.iterdir() if f.is_file() and f.suffix in IMAGE_EXTS]
    if not images:
        print(f"No images in {src_path}")
        return

    print(f"\nProcessing {src_class} in {split_dir.name} ({len(images)} images)...")
    
    # Calculate scores
    scored = []
    for img_p in images:
        score = score_fn(img_p)
        scored.append((img_p, score))

    # Sort by severity score
    scored.sort(key=lambda x: x[1])
    median_idx = len(scored) // 2

    mild_imgs = [p for p, _ in scored[:median_idx]]
    severe_imgs = [p for p, _ in scored[median_idx:]]

    mild_dir = split_dir / mild_class
    severe_dir = split_dir / severe_class
    mild_dir.mkdir(parents=True, exist_ok=True)
    severe_dir.mkdir(parents=True, exist_ok=True)

    for p in mild_imgs:
        shutil.move(str(p), str(mild_dir / p.name))

    for p in severe_imgs:
        shutil.move(str(p), str(severe_dir / p.name))

    # Remove empty src directory
    try:
        src_path.rmdir()
    except Exception:
        pass

    print(f"  -> '{mild_class}': {len(mild_imgs)} images")
    print(f"  -> '{severe_class}': {len(severe_imgs)} images")

def main():
    print("AeroCrop.ai — Sub-dividing Turmeric Classes by Severity")
    print("="*60)

    for split_dir in [TRAIN_DIR, VALID_DIR]:
        # 1. Leaf Blotch
        split_class(
            split_dir,
            "Turmeric___Leaf_blotch",
            "Turmeric___Leaf_blotch_mild",
            "Turmeric___Leaf_blotch_severe",
            calc_foliar_severity
        )
        # 2. Leaf Spot
        split_class(
            split_dir,
            "Turmeric___Leaf_spot",
            "Turmeric___Leaf_spot_mild",
            "Turmeric___Leaf_spot_severe",
            calc_foliar_severity
        )
        # 3. Rhizome Rot
        split_class(
            split_dir,
            "Turmeric___Rhizome_rot",
            "Turmeric___Rhizome_rot_early",
            "Turmeric___Rhizome_rot_severe",
            calc_rhizome_severity
        )

    print("\n" + "="*60)
    print("VERIFYING FINAL TURMERIC CLASSES")
    print("="*60)
    turmeric_train = sorted([d for d in TRAIN_DIR.iterdir() if d.is_dir() and d.name.startswith("Turmeric___")])
    total_imgs = 0
    for td in turmeric_train:
        c = len(list(td.glob("*")))
        total_imgs += c
        print(f"  - {td.name.split('___')[1]}: {c} images")

    print(f"\nTotal Turmeric Classes: {len(turmeric_train)} | Total Training Images: {total_imgs}")

if __name__ == "__main__":
    main()
