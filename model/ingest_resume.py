"""
AeroCrop.ai — Resume Ingestion (Steps 5-fix, 6, 7, 8)
Fixes:
 - Turmeric B: "Dry Leaf" mapped to Turmeric___Dry_leaf (not Soybean)
 - PlantDoc: extracted to C:/tmp/plantdoc to avoid Windows 260-char path limit
 - Potato and Soybean: also run
"""

import os
import sys
import shutil
import zipfile
import random
from pathlib import Path

# Enable long path support by using \\?\ prefix on Windows
def lp(p: Path) -> str:
    """Return long-path-safe string for Windows."""
    s = str(p.resolve())
    if not s.startswith("\\\\?\\"):
        s = "\\\\?\\" + s
    return s

BASE_DIR      = Path(r"D:\Codes\final_year_project")
DOWNLOADS_DIR = Path(r"C:\Users\devan\Downloads")
EXTRACT_TMP   = BASE_DIR / "data" / "raw_extracted"
TRAIN_DIR     = BASE_DIR / "data" / "main dataset" / "train"
VALID_DIR     = BASE_DIR / "data" / "main dataset" / "valid"
# PlantDoc extracted to short path to avoid 260-char Windows limit
PLANTDOC_TMP  = Path(r"C:\tmp\plantdoc")
VALID_RATIO   = 0.20
RANDOM_SEED   = 42

random.seed(RANDOM_SEED)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}


def find_image_files(folder: Path):
    try:
        return [f for f in folder.rglob('*') if f.suffix in IMAGE_EXTS]
    except Exception:
        return []


def extract_zip_to_short(zip_path: Path, dest: Path):
    """Extract ZIP using short base dest path."""
    dest.mkdir(parents=True, exist_ok=True)
    print(f"  Extracting: {zip_path.name} -> {dest}")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.infolist():
            # Shorten filename to avoid long path issues
            parts = Path(member.filename).parts
            # Keep only last 2 parts (parent_folder/filename)
            if len(parts) >= 2:
                short_path = dest / parts[-2] / parts[-1]
            elif len(parts) == 1:
                short_path = dest / parts[-1]
            else:
                continue

            if member.filename.endswith('/'):
                short_path.mkdir(parents=True, exist_ok=True)
                continue

            short_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                with zf.open(member) as src, open(short_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            except Exception as e:
                pass  # skip files with issues


def copy_images_to_split(images: list, aerocrop_class: str, label: str = ""):
    if not images:
        return 0, 0
    shuffled = images.copy()
    random.shuffle(shuffled)
    n_valid = max(1, int(len(shuffled) * VALID_RATIO))
    valid_imgs = shuffled[:n_valid]
    train_imgs = shuffled[n_valid:]

    train_class_dir = TRAIN_DIR / aerocrop_class
    valid_class_dir = VALID_DIR / aerocrop_class
    train_class_dir.mkdir(parents=True, exist_ok=True)
    valid_class_dir.mkdir(parents=True, exist_ok=True)

    copied_train = 0
    for img in train_imgs:
        dest = train_class_dir / img.name
        if dest.exists():
            dest = train_class_dir / f"{img.stem}_{label}{img.suffix}"
        try:
            shutil.copy2(img, dest)
            copied_train += 1
        except Exception:
            pass

    copied_valid = 0
    for img in valid_imgs:
        dest = valid_class_dir / img.name
        if dest.exists():
            dest = valid_class_dir / f"{img.stem}_{label}{img.suffix}"
        try:
            shutil.copy2(img, dest)
            copied_valid += 1
        except Exception:
            pass

    return copied_train, copied_valid


# ── STEP 5 FIX: Turmeric B "Dry Leaf" → Turmeric___Dry_leaf ─────────────────

def fix_turmeric_dry_leaf():
    """Move wrongly classified Turmeric 'Dry Leaf' from Soybean to Turmeric."""
    wrong_train = TRAIN_DIR / "Soybean___Dry_leaf"
    wrong_valid = VALID_DIR / "Soybean___Dry_leaf"
    correct_train = TRAIN_DIR / "Turmeric___Dry_leaf"
    correct_valid = VALID_DIR / "Turmeric___Dry_leaf"

    moved = 0
    for src_dir, dst_dir in [(wrong_train, correct_train), (wrong_valid, correct_valid)]:
        if src_dir.exists():
            dst_dir.mkdir(parents=True, exist_ok=True)
            for f in src_dir.iterdir():
                dest = dst_dir / f.name
                if dest.exists():
                    dest = dst_dir / f"{f.stem}_tb{f.suffix}"
                shutil.move(str(f), str(dest))
                moved += 1
            # Remove now-empty wrong folder
            try:
                src_dir.rmdir()
            except Exception:
                pass

    existing = len(list(correct_train.iterdir())) if correct_train.exists() else 0
    print(f"  FIX: Moved {moved} 'Dry Leaf' files -> Turmeric___Dry_leaf (total train: {existing})")


# ── STEP 6: PlantDoc (short path extraction) ─────────────────────────────────

PLANTDOC_CLASS_MAP = {
    "corn gray leaf spot":  "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "corn leaf blight":     "Corn_(maize)___Northern_Leaf_Blight",
    "corn rust leaf":       "Corn_(maize)___Common_rust_",
    "soyabean leaf":        "Soybean___healthy",
    # Everything else → None (skip)
}

def ingest_plantdoc():
    print("\n[6/8] CORN (PlantDoc) - extracting to short path to avoid Windows limit")
    PLANTDOC_TMP.mkdir(parents=True, exist_ok=True)
    plantdoc_zip = DOWNLOADS_DIR / "PlantDoc-Dataset-master.zip"

    extract_zip_to_short(plantdoc_zip, PLANTDOC_TMP)

    total_processed = 0
    for d in sorted(PLANTDOC_TMP.iterdir()):
        if not d.is_dir():
            continue
        key = d.name.lower().strip()
        aerocrop_class = PLANTDOC_CLASS_MAP.get(key)
        if aerocrop_class is None:
            continue

        images = find_image_files(d)
        if not images:
            continue

        t, v = copy_images_to_split(images, aerocrop_class, "pd")
        existing = len(list((TRAIN_DIR / aerocrop_class).iterdir())) if (TRAIN_DIR / aerocrop_class).exists() else 0
        print(f"    OK  '{d.name}' -> '{aerocrop_class}' | +{t} train / +{v} valid (total train: {existing})")
        total_processed += t + v

    print(f"  PlantDoc: {total_processed} images processed")


# ── STEP 7: Potato ───────────────────────────────────────────────────────────

POTATO_CLASS_MAP = {
    "bacteria":     "Potato___Bacterial_wilt",
    "fungi":        "Potato___Fungal_disease",
    "healthy":      "Potato___healthy",
    "nematode":     "Potato___Nematode",
    "pest":         "Potato___Pest_damage",
    "phytophthora": "Potato___Late_blight",
    "virus":        "Potato___Mosaic_virus",
}

def ingest_potato():
    print("\n[7/8] POTATO - Potato Leaf Disease Dataset")
    dest = EXTRACT_TMP / "potato"

    if not dest.exists():
        potato_zip = DOWNLOADS_DIR / "Potato Leaf Disease Dataset in Uncontrolled Environment.zip"
        dest.mkdir(parents=True, exist_ok=True)
        print(f"  Extracting: {potato_zip.name}")
        with zipfile.ZipFile(potato_zip) as zf:
            zf.extractall(dest)

    # Find root folder
    root = dest / "Potato Leaf Disease Dataset in Uncontrolled Environment"
    if not root.exists():
        root = dest

    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        key = d.name.lower().strip()
        aerocrop_class = POTATO_CLASS_MAP.get(key)
        if aerocrop_class is None:
            print(f"    SKIP  '{d.name}' (no mapping)")
            continue
        images = find_image_files(d)
        t, v = copy_images_to_split(images, aerocrop_class, "pt")
        existing = len(list((TRAIN_DIR / aerocrop_class).iterdir())) if (TRAIN_DIR / aerocrop_class).exists() else 0
        print(f"    OK  '{d.name}' -> '{aerocrop_class}' | +{t} train / +{v} valid (total train: {existing})")


# ── STEP 8: Soybean ──────────────────────────────────────────────────────────

SOYBEAN_CLASS_MAP = {
    "healthy plants":       "Soybean___healthy",
    "healthy":              "Soybean___healthy",
    "vein necrosis":        "Soybean___Vein_necrosis",
    "dry leaf":             "Soybean___Dry_leaf",
    "septoria brown spot":  "Soybean___Brown_spot",
    "bacterial leaf blight":"Soybean___Bacterial_blight",
    "root images":          None,  # skip root images
}

def ingest_soybean():
    print("\n[8/8] SOYBEAN - An India soyabean leaf dataset")
    soy_zip = DOWNLOADS_DIR / "An India soyabean leaf dataset.zip"
    if not soy_zip.exists():
        print(f"  SKIP: {soy_zip.name} not found (may need manual download)")
        return

    dest = EXTRACT_TMP / "soybean"
    if not dest.exists():
        dest.mkdir(parents=True, exist_ok=True)
        print(f"  Extracting: {soy_zip.name}")
        try:
            with zipfile.ZipFile(soy_zip) as zf:
                zf.extractall(dest)
        except PermissionError as e:
            print(f"  Permission error: {e}")
            print("  SKIP: Run script as Administrator or copy file first")
            return

    for d in sorted(dest.rglob("*")):
        if not d.is_dir():
            continue
        images = find_image_files(d)
        if not images:
            continue
        key = d.name.lower().strip()
        aerocrop_class = SOYBEAN_CLASS_MAP.get(key)
        if aerocrop_class is None:
            print(f"    SKIP  '{d.name}'")
            continue
        t, v = copy_images_to_split(images, aerocrop_class, "sb")
        existing = len(list((TRAIN_DIR / aerocrop_class).iterdir())) if (TRAIN_DIR / aerocrop_class).exists() else 0
        print(f"    OK  '{d.name}' -> '{aerocrop_class}' | +{t} train / +{v} valid (total train: {existing})")


# ── SUMMARY ──────────────────────────────────────────────────────────────────

def print_summary():
    print("\n" + "="*70)
    print("FINAL CLASS SUMMARY (train folder)")
    print("="*70)

    crops = {}
    for d in sorted(TRAIN_DIR.iterdir()):
        if not d.is_dir():
            continue
        crop = d.name.split("___")[0]
        count = len([f for f in d.rglob("*") if f.suffix.lower() in {'.jpg','.jpeg','.png'}])
        crops.setdefault(crop, []).append((d.name, count))

    total_classes = 0
    total_images  = 0
    for crop, classes in sorted(crops.items()):
        total = sum(c for _, c in classes)
        ok = "OK" if len(classes) >= 10 else "!!"
        print(f"\n[{ok}] {crop}: {len(classes)} classes | {total} images")
        for cls, cnt in sorted(classes):
            disease = cls.split("___")[1] if "___" in cls else cls
            print(f"       - {disease}: {cnt}")
        total_classes += len(classes)
        total_images  += total

    print(f"\n{'='*70}")
    print(f"TOTAL: {total_classes} classes | {total_images} training images")


# ── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("AeroCrop.ai - Resume Ingestion (Steps 5-fix, 6, 7, 8)")
    print()

    print("[5-FIX] Correcting Turmeric 'Dry Leaf' misclassification...")
    fix_turmeric_dry_leaf()

    ingest_plantdoc()
    ingest_potato()
    ingest_soybean()

    print_summary()
    print("\nDone! All datasets ingested.")
