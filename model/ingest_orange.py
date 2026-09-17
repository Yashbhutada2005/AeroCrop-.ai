"""
AeroCrop.ai — Ingest Sweet Orange Dataset
==========================================
Integrates:
Multi-format open-source sweet orange leaf dataset for disease detection, classification, and analysis
From extracted: D:\\Codes\\final_year_project\\data\\raw_extracted\\orange\\...\\Sweetorange.zip

Classes mapped:
- Citrus mealybugs -> Orange___Citrus_mealybug (NEW)
- Die back         -> Orange___Die_back (NEW)
- Foliage damaged  -> Orange___Foliage_damage (NEW)
- Powdery mildew   -> Orange___Powdery_mildew (NEW)
- Shot hole        -> Orange___Shot_hole (NEW)
- Spiny whitefly   -> Orange___Spiny_whitefly (NEW)
- Yellow leaves    -> Orange___Yellow_leaves (NEW)
- Citrus canker    -> Orange___Canker (merge)
- Citrus greening  -> Orange___Haunglongbing_(Citrus_greening) (merge)
- Yellow dragon    -> Orange___Haunglongbing_(Citrus_greening) (merge)
- Healthy leaf     -> Orange___healthy (merge)

Rules:
- 80% train, 20% validation split (random seed 42)
- Prefixed filenames ('or_') to prevent collisions
"""

import os
import shutil
import zipfile
import random
from pathlib import Path

BASE_DIR  = Path(r"D:\Codes\final_year_project")
TRAIN_DIR = BASE_DIR / "data" / "main dataset" / "train"
VALID_DIR = BASE_DIR / "data" / "main dataset" / "valid"

EXTRACTED_ZIP = BASE_DIR / "data" / "raw_extracted" / "orange" / "Multi-format open-source sweet orange leaf dataset for disease detection, classification, and analysis" / "Sweetorange.zip"

VALID_RATIO = 0.20
random.seed(42)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

CLASS_MAP = {
    "Citrus mealybugs": "Orange___Citrus_mealybug",
    "Die back":         "Orange___Die_back",
    "Foliage damaged":  "Orange___Foliage_damage",
    "Powdery mildew":   "Orange___Powdery_mildew",
    "Shot hole":        "Orange___Shot_hole",
    "Spiny whitefly":   "Orange___Spiny_whitefly",
    "Yellow leaves":    "Orange___Yellow_leaves",
    "Citrus canker":    "Orange___Canker",
    "Citrus greening":  "Orange___Haunglongbing_(Citrus_greening)",
    "Yellow dragon":    "Orange___Haunglongbing_(Citrus_greening)",
    "Healthy leaf":     "Orange___healthy",
}


def copy_split(zf, members, target_class, prefix="or"):
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


def ingest_orange():
    print("\n--- Ingesting Sweet Orange Dataset ---")
    if not EXTRACTED_ZIP.exists():
        print(f"Error: {EXTRACTED_ZIP} not found")
        return

    # Clean any partial 'or_*' files from Citrus mealybug from aborted run
    for split_dir in [TRAIN_DIR, VALID_DIR]:
        mb_dir = split_dir / "Orange___Citrus_mealybug"
        if mb_dir.exists():
            for f in mb_dir.glob("or_*"):
                f.unlink()

    print(f"Opening Sweetorange.zip ({round(EXTRACTED_ZIP.stat().st_size / (1024**3), 2)} GB)...")
    with zipfile.ZipFile(EXTRACTED_ZIP, 'r') as zf:
        namelist = zf.namelist()
        print(f"Total entries in Sweetorange: {len(namelist)}")

        for folder_name, target_class in CLASS_MAP.items():
            # Converted Image is 640x480 - fast and lightweight
            members = [
                n for n in namelist
                if f"Converted Image/{folder_name}/" in n
                and Path(n).suffix in IMAGE_EXTS
                and not Path(n).name.startswith("._")
                and not n.startswith("__MACOSX")
            ]
            if not members:
                members = [
                    n for n in namelist
                    if f"Original Image/{folder_name}/" in n
                    and Path(n).suffix in IMAGE_EXTS
                    and not Path(n).name.startswith("._")
                    and not n.startswith("__MACOSX")
                ]
            if members:
                n_train, n_valid = copy_split(zf, members, target_class, prefix="or")
                print(f"  [{folder_name}] -> {target_class}: +{n_train} train, +{n_valid} valid (total {len(members)})")
            else:
                print(f"  Warning: No images found for {folder_name}")


def print_orange_summary():
    print("\n==========================================")
    print("Orange Classes Summary in main dataset:")
    print("==========================================")
    orange_train_classes = sorted([d.name for d in TRAIN_DIR.iterdir() if d.is_dir() and d.name.startswith("Orange___")])
    total_train = 0
    total_valid = 0
    for c in orange_train_classes:
        train_count = len(list((TRAIN_DIR / c).glob("*.*")))
        valid_count = len(list((VALID_DIR / c).glob("*.*"))) if (VALID_DIR / c).exists() else 0
        total_train += train_count
        total_valid += valid_count
        print(f"  {c:<40}: {train_count:>5} train | {valid_count:>5} valid")
    print(f"\nTotal Orange classes: {len(orange_train_classes)}")
    print(f"Total Orange train images: {total_train} | valid: {total_valid}")


def cleanup():
    temp_dir = BASE_DIR / "data" / "raw_extracted" / "orange"
    if temp_dir.exists():
        print(f"\nCleaning up temporary extracted archive: {temp_dir}...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("Cleanup completed.")


if __name__ == "__main__":
    print("Starting Orange dataset ingestion...")
    ingest_orange()
    print_orange_summary()
    cleanup()
    print("\nOrange ingestion finished successfully!")
