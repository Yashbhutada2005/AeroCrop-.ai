"""
AeroCrop.ai — Ingest Paddy Doctor Dataset
========================================
Extracts train_images from paddy-disease-classification (1).zip,
maps them to AeroCrop Rice classes, performs 80/20 train/valid split,
and merges them with existing Rice data.
"""

import os
import sys
import shutil
import zipfile
import random
from pathlib import Path

BASE_DIR  = Path(r"D:\Codes\final_year_project")
TRAIN_DIR = BASE_DIR / "data" / "main dataset" / "train"
VALID_DIR = BASE_DIR / "data" / "main dataset" / "valid"
PADDY_ZIP = Path(r"C:\Users\devan\Downloads\paddy-disease-classification (1).zip")

VALID_RATIO = 0.20
random.seed(42)

PADDY_MAP = {
    "bacterial_leaf_blight":   "Rice___Bacterial_leaf_blight",
    "bacterial_leaf_streak":   "Rice___Bacterial_leaf_streak",
    "bacterial_panicle_blight": "Rice___Bacterial_panicle_blight",
    "blast":                   "Rice___Leaf_blast",
    "brown_spot":              "Rice___Brown_spot",
    "dead_heart":              "Rice___Dead_heart",
    "downy_mildew":            "Rice___Downy_mildew",
    "hispa":                   "Rice___Hispa",
    "normal":                  "Rice___healthy",
    "tungro":                  "Rice___Tungro",
}

def main():
    if not PADDY_ZIP.exists():
        print(f"ERROR: {PADDY_ZIP} not found!")
        sys.exit(1)

    print(f"Opening: {PADDY_ZIP.name} ({round(PADDY_ZIP.stat().st_size / (1024*1024), 1)} MB)")

    with zipfile.ZipFile(PADDY_ZIP, 'r') as zf:
        all_members = zf.namelist()
        
        # Group train_images by subfolder
        class_files = {}
        for m in all_members:
            if m.startswith("train_images/") and not m.endswith("/"):
                parts = m.split("/")
                if len(parts) >= 3:
                    src_class = parts[1]
                    if src_class in PADDY_MAP:
                        class_files.setdefault(src_class, []).append(m)

        print(f"Found {len(class_files)} classes to process.\n")

        total_train_added = 0
        total_valid_added = 0

        for src_class, members in sorted(class_files.items()):
            aerocrop_class = PADDY_MAP[src_class]
            random.shuffle(members)
            
            n_valid = max(1, int(len(members) * VALID_RATIO))
            valid_members = members[:n_valid]
            train_members = members[n_valid:]

            train_target_dir = TRAIN_DIR / aerocrop_class
            valid_target_dir = VALID_DIR / aerocrop_class
            train_target_dir.mkdir(parents=True, exist_ok=True)
            valid_target_dir.mkdir(parents=True, exist_ok=True)

            # Extract train
            for m in train_members:
                fname = Path(m).name
                dest = train_target_dir / f"paddy_{fname}"
                with zf.open(m) as src, open(dest, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            total_train_added += len(train_members)

            # Extract valid
            for m in valid_members:
                fname = Path(m).name
                dest = valid_target_dir / f"paddy_{fname}"
                with zf.open(m) as src, open(dest, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            total_valid_added += len(valid_members)

            existing_train = len([f for f in train_target_dir.iterdir() if f.is_file()])
            existing_valid = len([f for f in valid_target_dir.iterdir() if f.is_file()])
            print(f"  OK  '{src_class}' -> '{aerocrop_class}' | +{len(train_members)} train / +{len(valid_members)} val (total: {existing_train} train, {existing_valid} val)")

        print("\n" + "="*60)
        print(f"Paddy Doctor Ingestion Complete!")
        print(f"Added {total_train_added} train images and {total_valid_added} val images.")
        print("="*60)

    # Print summary of Rice classes
    print("\nCurrent Rice Classes Summary in Train:")
    rice_dirs = [d for d in TRAIN_DIR.iterdir() if d.is_dir() and d.name.startswith("Rice___")]
    for rd in sorted(rice_dirs):
        c = len(list(rd.glob("*")))
        print(f"  - {rd.name.split('___')[1]}: {c} images")
    print(f"\nTotal Rice Classes: {len(rice_dirs)}")

if __name__ == "__main__":
    main()
