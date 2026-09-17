"""
AeroCrop.ai — Ingest All Corn/Maize Datasets
===========================================
Integrates:
1. African Maize Dataset (Multicrop-Disease-Maiz Disease-Pests and disease.zip)
   - Maize Lethal Necrosis -> Corn_(maize)___Lethal_necrosis
   - Maize fall armyworm -> Corn_(maize)___Fall_armyworm
   - Maize streak virus -> Corn_(maize)___Streak_virus
   - Maize grasshoper -> Corn_(maize)___Grasshopper
   - Maize leaf beetle -> Corn_(maize)___Leaf_beetle
   - Maize Rust -> Corn_(maize)___Common_rust_ (merge)
   - Maize leaf blight -> Corn_(maize)___Northern_Leaf_Blight (merge)
   - Maize leaf spot -> Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot (merge)
   - Maize healthy -> Corn_(maize)___healthy (merge)

2. Seasonal Corn Leaf Disease Dataset (Corn leaf disease dataset.zip)
   - Bacterial Leaf Streak -> Corn_(maize)___Bacterial_leaf_streak
   - Maize Chlorotic Mottle Virus -> Corn_(maize)___Chlorotic_mottle_virus
   - Gray_leaf_spot, Common_rust, Healthy (merges)

3. Zenodo MLN dataset (mln1.zip)
   - Extra Lethal Necrosis images
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
DL_DIR    = Path(r"C:\Users\devan\Downloads")

AFRICAN_ZIP = BASE_DIR / "data" / "raw_extracted" / "maize_african" / "Maize Crop Disease (Leaf)" / "Multicrop-Disease-Maiz Disease-Pests and disease.zip"
SEASONAL_ZIP = DL_DIR / "Corn leaf disease dataset.zip"
MLN_ZIP      = DL_DIR / "mln1.zip"

VALID_RATIO = 0.20
random.seed(42)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

# 1. Map for African Maize dataset
AFRICAN_MAP = {
    "Maize Lethal Necrosis": "Corn_(maize)___Lethal_necrosis",
    "Maize fall armyworm":   "Corn_(maize)___Fall_armyworm",
    "Maize streak virus":    "Corn_(maize)___Streak_virus",
    "Maize grasshoper":      "Corn_(maize)___Grasshopper",
    "Maize leaf beetle":     "Corn_(maize)___Leaf_beetle",
    "Maize Rust":            "Corn_(maize)___Common_rust_",
    "Maize leaf blight":     "Corn_(maize)___Northern_Leaf_Blight",
    "Maize leaf spot":       "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Maize healthy":         "Corn_(maize)___healthy",
}

# 2. Map for Seasonal Corn dataset
SEASONAL_MAP = {
    "Bacterial Leaf Streak":        "Corn_(maize)___Bacterial_leaf_streak",
    "Maize Chlorotic Mottle Virus": "Corn_(maize)___Chlorotic_mottle_virus",
    "Common_rust":                  "Corn_(maize)___Common_rust_",
    "Gray_leaf_spot":               "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Healthy":                      "Corn_(maize)___healthy",
}


def copy_split(zf, members, aerocrop_class, label=""):
    random.shuffle(members)
    n_valid = max(1, int(len(members) * VALID_RATIO))
    valid_members = members[:n_valid]
    train_members = members[n_valid:]

    train_target = TRAIN_DIR / aerocrop_class
    valid_target = VALID_DIR / aerocrop_class
    train_target.mkdir(parents=True, exist_ok=True)
    valid_target.mkdir(parents=True, exist_ok=True)

    for m in train_members:
        fname = Path(m).name
        dest = train_target / f"{label}_{fname}"
        with zf.open(m) as src, open(dest, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    for m in valid_members:
        fname = Path(m).name
        dest = valid_target / f"{label}_{fname}"
        with zf.open(m) as src, open(dest, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    return len(train_members), len(valid_members)


def ingest_african_maize():
    print("\n--- 1. Ingesting African Maize Dataset ---")
    if not AFRICAN_ZIP.exists():
        print(f"Skipping: {AFRICAN_ZIP} not found")
        return

    with zipfile.ZipFile(AFRICAN_ZIP) as zf:
        prefix = "Multicrop-Disease-Maiz Disease-Pests and disease/"
        cat_members = {}
        for n in zf.namelist():
            if n.startswith(prefix) and not n.endswith('/'):
                rel = n[len(prefix):]
                parts = rel.split('/')
                if len(parts) >= 2:
                    cat = parts[0]
                    if cat in AFRICAN_MAP and any(n.endswith(ext) for ext in IMAGE_EXTS):
                        cat_members.setdefault(cat, []).append(n)

        for cat, members in sorted(cat_members.items()):
            target_cls = AFRICAN_MAP[cat]
            t, v = copy_split(zf, members, target_cls, "afr")
            tot_train = len(list((TRAIN_DIR / target_cls).glob("*")))
            print(f"  OK  '{cat}' -> '{target_cls}' | +{t} train / +{v} val (total train: {tot_train})")


def ingest_seasonal_corn():
    print("\n--- 2. Ingesting Seasonal Corn Leaf Disease Dataset ---")
    if not SEASONAL_ZIP.exists():
        print(f"Skipping: {SEASONAL_ZIP} not found")
        return

    with zipfile.ZipFile(SEASONAL_ZIP) as zf:
        prefix = "Final corn dataset/"
        cat_members = {}
        for n in zf.namelist():
            if n.startswith(prefix) and not n.endswith('/'):
                rel = n[len(prefix):]
                parts = rel.split('/')
                if len(parts) >= 2:
                    cat = parts[0]
                    if cat in SEASONAL_MAP and any(n.endswith(ext) for ext in IMAGE_EXTS):
                        cat_members.setdefault(cat, []).append(n)

        for cat, members in sorted(cat_members.items()):
            target_cls = SEASONAL_MAP[cat]
            t, v = copy_split(zf, members, target_cls, "sea")
            tot_train = len(list((TRAIN_DIR / target_cls).glob("*")))
            print(f"  OK  '{cat}' -> '{target_cls}' | +{t} train / +{v} val (total train: {tot_train})")


def print_summary():
    print("\n" + "="*60)
    print("FINAL CORN / MAIZE CLASSES SUMMARY")
    print("="*60)
    corn_dirs = [d for d in TRAIN_DIR.iterdir() if d.is_dir() and d.name.startswith("Corn_(maize)___")]
    total_imgs = 0
    for cd in sorted(corn_dirs):
        c = len(list(cd.glob("*")))
        total_imgs += c
        print(f"  - {cd.name.split('___')[1]}: {c} images")
    print(f"\nTotal Corn Classes: {len(corn_dirs)} | Total Training Images: {total_imgs}")


if __name__ == "__main__":
    print("AeroCrop.ai - Corn / Maize Datasets Ingestion")
    ingest_african_maize()
    ingest_seasonal_corn()
    print_summary()
