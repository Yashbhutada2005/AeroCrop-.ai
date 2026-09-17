"""
AeroCrop.ai — Ingest Potato Datasets
====================================
Integrates:
1. Potato Leaf Disease Dataset (Potato Leaf Disease Dataset-20260521T130709Z-3-001.zip)
   - Bacterial Soft Rot -> Potato___Bacterial_soft_rot (NEW)
   - Viral Leaf Roll    -> Potato___Leaf_roll_virus (NEW)
   - Viral PVX          -> Potato___Potato_virus_X (NEW)
   - Viral PVY          -> Potato___Potato_virus_Y (NEW)
   - Fungal Late Blight -> Potato___Late_blight (merge)
   - Healthy            -> Potato___healthy (merge)

2. PotatoCare Deep Learning Dataset (Potato Disease Dataset-20250303T183921Z-001.zip)
   - Black Scurf        -> Potato___Black_scurf (NEW)
   - Blackleg           -> Potato___Blackleg (NEW)
   - Common Scab        -> Potato___Common_scab (NEW)
   - Dry Rot            -> Potato___Dry_rot (NEW)
   - Pink Rot           -> Potato___Pink_rot (NEW)
   - Blackspot Bruising -> Potato___Blackspot_bruising (NEW)
   - Brown Rot          -> Potato___Bacterial_wilt (merge - Ralstonia solanacearum)
   - Soft Rot           -> Potato___Bacterial_soft_rot (merge)
   - Healthy Potatoes   -> Potato___healthy (merge)

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

POTATO_ZIP1 = DL_DIR / "Potato Leaf Disease Dataset.zip"
POTATO_ZIP1_INNER = "Potato Leaf Disease Dataset/Potato Leaf Disease Dataset-20260521T130709Z-3-001.zip"

POTATO_ZIP2 = DL_DIR / "PotatoCare Deep learning based potato disease  dataset.zip"
POTATO_ZIP2_INNER = "PotatoCare Deep learning based potato disease  dataset/Potato Disease Dataset-20250303T183921Z-001.zip"

VALID_RATIO = 0.20
random.seed(42)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

MAP_ZIP1 = {
    "Bacterial Soft Rot": "Potato___Bacterial_soft_rot",
    "Viral Leaf Roll":    "Potato___Leaf_roll_virus",
    "Viral PVX":          "Potato___Potato_virus_X",
    "Viral PVY":          "Potato___Potato_virus_Y",
    "Fungal Late Blight": "Potato___Late_blight",
    "Healthy":            "Potato___healthy",
}

MAP_ZIP2 = {
    "Black Scurf":        "Potato___Black_scurf",
    "Blackleg":           "Potato___Blackleg",
    "Common Scab":        "Potato___Common_scab",
    "Dry Rot":            "Potato___Dry_rot",
    "Pink Rot":           "Potato___Pink_rot",
    "Blackspot Bruising": "Potato___Blackspot_bruising",
    "Brown Rot":          "Potato___Bacterial_wilt",
    "Soft Rot":           "Potato___Bacterial_soft_rot",
    "Healthy Potatoes":   "Potato___healthy",
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


def ingest_potato_dataset1():
    print("\n--- 1. Ingesting Potato Leaf Disease Dataset ---")
    if not POTATO_ZIP1.exists():
        print(f"Skipping: {POTATO_ZIP1} not found")
        return

    with zipfile.ZipFile(POTATO_ZIP1, 'r') as outer_zf:
        inner_bytes = outer_zf.read(POTATO_ZIP1_INNER)
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
                    n_train, n_valid = copy_split(inner_zf, members, target_class, prefix="pldd")
                    print(f"  [{folder_name}] -> {target_class}: +{n_train} train, +{n_valid} valid (total {len(members)})")
                else:
                    print(f"  Warning: No images found for {folder_name}")


def ingest_potato_dataset2():
    print("\n--- 2. Ingesting PotatoCare Deep Learning Dataset ---")
    if not POTATO_ZIP2.exists():
        print(f"Skipping: {POTATO_ZIP2} not found")
        return

    with zipfile.ZipFile(POTATO_ZIP2, 'r') as outer_zf:
        inner_bytes = outer_zf.read(POTATO_ZIP2_INNER)
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
                    n_train, n_valid = copy_split(inner_zf, members, target_class, prefix="ptcare")
                    print(f"  [{folder_name}] -> {target_class}: +{n_train} train, +{n_valid} valid (total {len(members)})")
                else:
                    print(f"  Warning: No images found for {folder_name}")


def print_potato_summary():
    print("\n==========================================")
    print("Potato Classes Summary in main dataset:")
    print("==========================================")
    potato_train_classes = sorted([d.name for d in TRAIN_DIR.iterdir() if d.is_dir() and d.name.startswith("Potato___")])
    total_train = 0
    total_valid = 0
    for c in potato_train_classes:
        train_count = len(list((TRAIN_DIR / c).glob("*.*")))
        valid_count = len(list((VALID_DIR / c).glob("*.*"))) if (VALID_DIR / c).exists() else 0
        total_train += train_count
        total_valid += valid_count
        print(f"  {c:<32}: {train_count:>5} train | {valid_count:>5} valid")
    print(f"\nTotal Potato classes: {len(potato_train_classes)}")
    print(f"Total Potato train images: {total_train} | valid: {total_valid}")


if __name__ == "__main__":
    print("Starting Potato dataset ingestion...")
    ingest_potato_dataset1()
    ingest_potato_dataset2()
    print_potato_summary()
    print("\nPotato ingestion finished successfully!")
