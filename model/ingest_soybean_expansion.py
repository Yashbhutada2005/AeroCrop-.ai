"""
AeroCrop.ai — Ingest Multi-Class Soybean Dataset
================================================
Integrates:
Multi-Class Soybean Leaf Disease Dataset Healthy a.zip

Classes mapped:
- Cercospora Leaf Blight -> Soybean___Cercospora_leaf_blight (NEW)
- Rust                   -> Soybean___Rust (NEW)
- Sudden Death Syndrome  -> Soybean___Sudden_death_syndrome (NEW)
- Bacterial Blight       -> Soybean___Bacterial_blight (merge)
- Healthy                -> Soybean___healthy (merge)

Rules:
- 80% train, 20% validation split (random seed 42)
- Prefixed filenames ('sb2_') to prevent collisions
- Direct streaming from zip
"""

import os
import shutil
import zipfile
import random
from pathlib import Path

BASE_DIR  = Path(r"D:\Codes\final_year_project")
TRAIN_DIR = BASE_DIR / "data" / "main dataset" / "train"
VALID_DIR = BASE_DIR / "data" / "main dataset" / "valid"
DL_DIR    = Path(r"C:\Users\devan\Downloads")

SOYBEAN_ZIP = DL_DIR / "Multi-Class Soybean Leaf Disease Dataset Healthy a.zip"

VALID_RATIO = 0.20
random.seed(42)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

CLASS_MAP = {
    "Cercospora Leaf Blight": "Soybean___Cercospora_leaf_blight",
    "Rust":                   "Soybean___Rust",
    "Sudden Death Syndrome":  "Soybean___Sudden_death_syndrome",
    "Bacterial Blight":       "Soybean___Bacterial_blight",
    "Healthy":                "Soybean___healthy",
}


def copy_split(zf, members, target_class, prefix="sb2"):
    random.shuffle(members)
    n_valid = max(1, int(len(members) * VALID_RATIO))
    valid_members = members[:n_valid]
    train_members = members[n_valid:]

    train_target = TRAIN_DIR / target_class
    valid_target = VALID_DIR / target_class
    train_target.mkdir(parents=True, exist_ok=True)
    valid_target.mkdir(parents=True, exist_ok=True)

    for m in train_members:
        fname = Path(m).name
        dest = train_target / f"{prefix}_{fname}"
        with zf.open(m) as src, open(dest, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    for m in valid_members:
        fname = Path(m).name
        dest = valid_target / f"{prefix}_{fname}"
        with zf.open(m) as src, open(dest, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    return len(train_members), len(valid_members)


def ingest_soybean():
    print("\n--- Ingesting Multi-Class Soybean Dataset ---")
    if not SOYBEAN_ZIP.exists():
        print(f"Error: {SOYBEAN_ZIP} not found")
        return

    with zipfile.ZipFile(SOYBEAN_ZIP, 'r') as zf:
        namelist = zf.namelist()
        print(f"Total entries in archive: {len(namelist)}")
        
        for folder_name, target_class in CLASS_MAP.items():
            members = [
                n for n in namelist
                if f"/{folder_name}/" in n
                and Path(n).suffix in IMAGE_EXTS
                and not Path(n).name.startswith("._")
                and not n.startswith("__MACOSX")
            ]
            if not members:
                members = [
                    n for n in namelist
                    if folder_name in n
                    and Path(n).suffix in IMAGE_EXTS
                    and not Path(n).name.startswith("._")
                    and not n.startswith("__MACOSX")
                ]
            if members:
                n_train, n_valid = copy_split(zf, members, target_class, prefix="sb2")
                print(f"  [{folder_name}] -> {target_class}: +{n_train} train, +{n_valid} valid (total {len(members)})")
            else:
                print(f"  Warning: No images found for {folder_name}")


def print_soybean_summary():
    print("\n==========================================")
    print("Soybean Classes Summary in main dataset:")
    print("==========================================")
    soybean_train_classes = sorted([d.name for d in TRAIN_DIR.iterdir() if d.is_dir() and d.name.startswith("Soybean___")])
    total_train = 0
    total_valid = 0
    for c in soybean_train_classes:
        train_count = len(list((TRAIN_DIR / c).glob("*.*")))
        valid_count = len(list((VALID_DIR / c).glob("*.*"))) if (VALID_DIR / c).exists() else 0
        total_train += train_count
        total_valid += valid_count
        print(f"  {c:<36}: {train_count:>5} train | {valid_count:>5} valid")
    print(f"\nTotal Soybean classes: {len(soybean_train_classes)}")
    print(f"Total Soybean train images: {total_train} | valid: {total_valid}")


if __name__ == "__main__":
    print("Starting Soybean expansion ingestion...")
    ingest_soybean()
    print_soybean_summary()
    print("\nSoybean ingestion finished successfully!")
