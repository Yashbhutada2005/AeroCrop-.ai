"""
AeroCrop.ai — Ingest MH-SoyaHealthVision Soybean Dataset
=========================================================
Integrates:
mendeley_dataset.zip (MH-SoyaHealthVision: An Indian UAV and Leaf Image Dataset)

Leaf classes mapped:
- Soyabean_Frog_Leaf_Eye.zip                   -> Soybean___Frogeye_leaf_spot (NEW)
- Soyabean_Mosaic.zip                          -> Soybean___Mosaic_virus (NEW)
- Caterpillar and Semilooper Pest Attack.zip   -> Soybean___Caterpillar (NEW)

Rules:
- 80% train, 20% validation split (random seed 42)
- Prefixed filenames ('mhsoya_') to prevent collisions
- Fast extraction via temporary disk stage with automatic cleanup
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

OUTER_ZIP = DL_DIR / "mendeley_dataset.zip"
TEMP_DIR  = BASE_DIR / "data" / "raw_extracted" / "soya_mh"

VALID_RATIO = 0.20
random.seed(42)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

TARGET_ZIPS = {
    "Soyabean_Frog_Leaf_Eye.zip":                 "Soybean___Frogeye_leaf_spot",
    "Soyabean_Mosaic.zip":                        "Soybean___Mosaic_virus",
    "Caterpillar and Semilooper Pest Attack.zip": "Soybean___Caterpillar",
}


def copy_split(zf, members, target_class, prefix="mhsoya"):
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


def ingest_mh_soya():
    print("\n--- Ingesting MH-SoyaHealthVision Leaf Dataset ---")
    if not OUTER_ZIP.exists():
        print(f"Error: {OUTER_ZIP} not found")
        return

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Opening outer archive: {OUTER_ZIP.name} (9.75 GB)...")
    with zipfile.ZipFile(OUTER_ZIP, 'r') as outer_zf:
        namelist = outer_zf.namelist()
        
        for inner_zip_name, target_class in TARGET_ZIPS.items():
            matching = [n for n in namelist if n.endswith(inner_zip_name) and "Soyabean_Leaf_Image_Dataset" in n]
            if not matching:
                print(f"Warning: {inner_zip_name} not found in archive")
                continue
            
            full_inner_path = matching[0]
            print(f"\nExtracting {inner_zip_name} to disk...")
            outer_zf.extract(full_inner_path, TEMP_DIR)
            extracted_zip_path = TEMP_DIR / full_inner_path
            
            print(f"Reading {inner_zip_name}...")
            with zipfile.ZipFile(extracted_zip_path, 'r') as inner_zf:
                members = [
                    n for n in inner_zf.namelist()
                    if Path(n).suffix in IMAGE_EXTS
                    and not Path(n).name.startswith("._")
                    and not n.startswith("__MACOSX")
                ]
                if members:
                    n_train, n_valid = copy_split(inner_zf, members, target_class, prefix="mhsoya")
                    print(f"  [{inner_zip_name}] -> {target_class}: +{n_train} train, +{n_valid} valid (total {len(members)})")
                else:
                    print(f"  Warning: No images found in {inner_zip_name}")


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


def cleanup():
    if TEMP_DIR.exists():
        print(f"\nCleaning up temporary folder: {TEMP_DIR}...")
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        print("Cleanup completed.")


if __name__ == "__main__":
    print("Starting MH-SoyaHealthVision dataset ingestion...")
    ingest_mh_soya()
    print_soybean_summary()
    cleanup()
    print("\nMH-Soya ingestion finished successfully!")
