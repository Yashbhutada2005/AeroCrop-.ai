"""
AeroCrop.ai — Ingest India Soybean Leaf Dataset
==============================================
Extracts categorized folders from 'An India soyabean leaf dataset.zip',
maps them to AeroCrop classes (80/20 train/valid split), and merges.
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
SOY_ZIP   = Path(r"C:\Users\devan\Downloads\An India soyabean leaf dataset.zip")

VALID_RATIO = 0.20
random.seed(42)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

SOY_MAP = {
    "1.Healthy":              "Soybean___healthy",
    "2.Vein Necrosis":        "Soybean___Vein_necrosis",
    "3.Dry_leaf":             "Soybean___Dry_leaf",
    "4.Septoria_Brown_Spot":  "Soybean___Brown_spot",
    "6.Bacterial leaf Blight":"Soybean___Bacterial_blight",
}

def main():
    if not SOY_ZIP.exists():
        print(f"ERROR: {SOY_ZIP} not found!")
        sys.exit(1)

    print(f"Opening: {SOY_ZIP.name} ({round(SOY_ZIP.stat().st_size / (1024**3), 2)} GB)")

    with zipfile.ZipFile(SOY_ZIP, 'r') as zf:
        all_members = zf.namelist()
        
        # Group categorized images
        class_files = {}
        for m in all_members:
            if m.endswith('/') or not any(m.endswith(ext) for ext in IMAGE_EXTS):
                continue
            for cat_key in SOY_MAP:
                if f"Soyabean leaf/{cat_key}/" in m:
                    class_files.setdefault(cat_key, []).append(m)
                    break

        print(f"Found {len(class_files)} distinct categories to ingest.\n")

        total_train_added = 0
        total_valid_added = 0

        for cat_key, members in sorted(class_files.items()):
            aerocrop_class = SOY_MAP[cat_key]
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
                dest = train_target_dir / f"sb_india_{fname}"
                with zf.open(m) as src, open(dest, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            total_train_added += len(train_members)

            # Extract valid
            for m in valid_members:
                fname = Path(m).name
                dest = valid_target_dir / f"sb_india_{fname}"
                with zf.open(m) as src, open(dest, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            total_valid_added += len(valid_members)

            existing_train = len([f for f in train_target_dir.iterdir() if f.is_file()])
            existing_valid = len([f for f in valid_target_dir.iterdir() if f.is_file()])
            print(f"  OK  '{cat_key}' -> '{aerocrop_class}' | +{len(train_members)} train / +{len(valid_members)} val (total: {existing_train} train, {existing_valid} val)")

        print("\n" + "="*60)
        print(f"Soybean Ingestion Complete!")
        print(f"Added {total_train_added} train images and {total_valid_added} val images.")
        print("="*60)

    # Print summary of Soybean classes
    print("\nCurrent Soybean Classes Summary in Train:")
    soy_dirs = [d for d in TRAIN_DIR.iterdir() if d.is_dir() and d.name.startswith("Soybean___")]
    for sd in sorted(soy_dirs):
        c = len(list(sd.glob("*")))
        print(f"  - {sd.name.split('___')[1]}: {c} images")
    print(f"\nTotal Soybean Classes: {len(soy_dirs)}")

if __name__ == "__main__":
    main()
