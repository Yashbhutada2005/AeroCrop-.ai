"""
AeroCrop.ai — Ingest Cotton Datasets
=====================================
Integrates:
1. Cotton Leaf Image Dataset for Disease Classification (Cotton_Original_Dataset.zip)
   - Alternaria Leaf Spot -> Cotton___Alternaria_leaf_spot (NEW)
   - Verticillium Wilt    -> Cotton___Verticillium_wilt (NEW)
   - Fusarium Wilt        -> Cotton___Fusarium_wilt (merge)
   - Bacterial Blight     -> Cotton___Bacterial_blight (merge)
   - Healthy Leaf         -> Cotton___healthy (merge)

2. SAR-CLD-2024: A Comprehensive Dataset for Cotton Leaf Disease Detection (Original Dataset.zip)
   - Leaf Hopper Jassids    -> Cotton___Jassid (NEW)
   - Leaf Redding           -> Cotton___Leaf_reddening (NEW)
   - Herbicide Growth Damage -> Cotton___Herbicide_damage (NEW)
   - Leaf Variegation       -> Cotton___Leaf_variegation (NEW)
   - Curl Virus             -> Cotton___Curl_virus (merge)
   - Bacterial Blight       -> Cotton___Bacterial_blight (merge)
   - Healthy Leaf           -> Cotton___healthy (merge)

Rules:
- 80% train, 20% validation split (random seed 42)
- Prefixed filenames to avoid overwrite collisions
- Stream directly from inner zip in memory to target directory
"""

import os
import io
import shutil
import zipfile
import random
from pathlib import Path

BASE_DIR  = Path(r"D:\Codes\final_year_project")
TRAIN_DIR = BASE_DIR / "data" / "main dataset" / "train"
VALID_DIR = BASE_DIR / "data" / "main dataset" / "valid"
DL_DIR    = Path(r"C:\Users\devan\Downloads")

COTTON_ZIP1 = DL_DIR / "Cotton Leaf Image Dataset for Disease Classificati.zip"
COTTON_ZIP1_INNER = "Cotton Leaf Image Dataset for Disease Classificati/Cotton_Original_Dataset.zip"

COTTON_ZIP2 = DL_DIR / "SAR-CLD-2024 A Comprehensive Dataset for Cotton Leaf Disease Detection.zip"
COTTON_ZIP2_INNER = "SAR-CLD-2024 A Comprehensive Dataset for Cotton Leaf Disease Detection/Original Dataset.zip"

VALID_RATIO = 0.20
random.seed(42)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

MAP_ZIP1 = {
    "Alternaria Leaf Spot": "Cotton___Alternaria_leaf_spot",
    "Verticillium Wilt":    "Cotton___Verticillium_wilt",
    "Fusarium Wilt":        "Cotton___Fusarium_wilt",
    "Bacterial Blight":     "Cotton___Bacterial_blight",
    "Healthy Leaf":         "Cotton___healthy",
}

MAP_ZIP2 = {
    "Leaf Hopper Jassids":     "Cotton___Jassid",
    "Leaf Redding":            "Cotton___Leaf_reddening",
    "Herbicide Growth Damage": "Cotton___Herbicide_damage",
    "Leaf Variegation":        "Cotton___Leaf_variegation",
    "Curl Virus":              "Cotton___Curl_virus",
    "Bacterial Blight":        "Cotton___Bacterial_blight",
    "Healthy Leaf":            "Cotton___healthy",
}


def copy_split(inner_zf, members, target_class, prefix=""):
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
        with inner_zf.open(m) as src, open(dest, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    for m in valid_members:
        fname = Path(m).name
        dest = valid_target / f"{prefix}_{fname}"
        with inner_zf.open(m) as src, open(dest, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    return len(train_members), len(valid_members)


def ingest_cotton_dataset1():
    print("\n--- 1. Ingesting Cotton Leaf Image Dataset for Disease Classification ---")
    if not COTTON_ZIP1.exists():
        print(f"Skipping: {COTTON_ZIP1} not found")
        return

    with zipfile.ZipFile(COTTON_ZIP1, 'r') as outer_zf:
        inner_bytes = outer_zf.read(COTTON_ZIP1_INNER)
        with zipfile.ZipFile(io.BytesIO(inner_bytes), 'r') as inner_zf:
            namelist = inner_zf.namelist()
            for folder_name, target_class in MAP_ZIP1.items():
                members = [
                    n for n in namelist
                    if f"/{folder_name}/" in n and Path(n).suffix in IMAGE_EXTS and not Path(n).name.startswith("._")
                ]
                if not members:
                    members = [
                        n for n in namelist
                        if folder_name in n and Path(n).suffix in IMAGE_EXTS and not Path(n).name.startswith("._")
                    ]
                if members:
                    n_train, n_valid = copy_split(inner_zf, members, target_class, prefix="clid")
                    print(f"  [{folder_name}] -> {target_class}: +{n_train} train, +{n_valid} valid (total {len(members)})")
                else:
                    print(f"  Warning: No images found for {folder_name}")


def ingest_cotton_dataset2():
    print("\n--- 2. Ingesting SAR-CLD-2024 Comprehensive Dataset ---")
    if not COTTON_ZIP2.exists():
        print(f"Skipping: {COTTON_ZIP2} not found")
        return

    with zipfile.ZipFile(COTTON_ZIP2, 'r') as outer_zf:
        inner_bytes = outer_zf.read(COTTON_ZIP2_INNER)
        with zipfile.ZipFile(io.BytesIO(inner_bytes), 'r') as inner_zf:
            namelist = inner_zf.namelist()
            for folder_name, target_class in MAP_ZIP2.items():
                members = [
                    n for n in namelist
                    if f"/{folder_name}/" in n and Path(n).suffix in IMAGE_EXTS and not Path(n).name.startswith("._")
                ]
                if not members:
                    members = [
                        n for n in namelist
                        if folder_name in n and Path(n).suffix in IMAGE_EXTS and not Path(n).name.startswith("._")
                    ]
                if members:
                    n_train, n_valid = copy_split(inner_zf, members, target_class, prefix="sarcld")
                    print(f"  [{folder_name}] -> {target_class}: +{n_train} train, +{n_valid} valid (total {len(members)})")
                else:
                    print(f"  Warning: No images found for {folder_name}")


def print_cotton_summary():
    print("\n==========================================")
    print("Cotton Classes Summary in main dataset:")
    print("==========================================")
    cotton_train_classes = sorted([d.name for d in TRAIN_DIR.iterdir() if d.is_dir() and d.name.startswith("Cotton___")])
    total_train = 0
    total_valid = 0
    for c in cotton_train_classes:
        train_count = len(list((TRAIN_DIR / c).glob("*.*")))
        valid_count = len(list((VALID_DIR / c).glob("*.*"))) if (VALID_DIR / c).exists() else 0
        total_train += train_count
        total_valid += valid_count
        print(f"  {c:<32}: {train_count:>5} train | {valid_count:>5} valid")
    print(f"\nTotal Cotton classes: {len(cotton_train_classes)}")
    print(f"Total Cotton train images: {total_train} | valid: {total_valid}")


if __name__ == "__main__":
    print("Starting Cotton dataset ingestion...")
    ingest_cotton_dataset1()
    ingest_cotton_dataset2()
    print_cotton_summary()
    print("\nCotton ingestion finished successfully!")
