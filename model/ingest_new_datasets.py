"""
AeroCrop.ai — New Dataset Ingestion Script
============================================
Extracts all downloaded ZIPs, maps class folders to AeroCrop CropName___DiseaseName
format, merges duplicates, and copies into data/main dataset/train & valid (80/20 split).

Usage:
    python model/ingest_new_datasets.py

Downloads expected at: C:/Users/devan/Downloads/
"""

import os
import sys
import shutil
import zipfile
import random
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent.parent
DOWNLOADS_DIR = Path(r"C:\Users\devan\Downloads")
EXTRACT_TMP   = BASE_DIR / "data" / "raw_extracted"
TRAIN_DIR     = BASE_DIR / "data" / "main dataset" / "train"
VALID_DIR     = BASE_DIR / "data" / "main dataset" / "valid"
VALID_RATIO   = 0.20
RANDOM_SEED   = 42

random.seed(RANDOM_SEED)

# ── Dataset ZIP files to process ───────────────────────────────────────────────
DATASET_ZIPS = {
    "sugarcane":  DOWNLOADS_DIR / "Sugarcane Leaf Dataset.zip",
    "banana":     DOWNLOADS_DIR / "Banana and Banana Leaf Dataset for Classification.zip",
    "citrus":     DOWNLOADS_DIR / "A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning.zip",
    "turmeric_a": DOWNLOADS_DIR / "Image Dataset for Turmeric Plant Leaf Disease Detection.zip",
    "turmeric_b": DOWNLOADS_DIR / "Turmeric Plant Disease Augmented Dataset.zip",
    "plantdoc":   DOWNLOADS_DIR / "PlantDoc-Dataset-master.zip",
    "potato":     DOWNLOADS_DIR / "Potato Leaf Disease Dataset in Uncontrolled Environment.zip",
    "soybean":    DOWNLOADS_DIR / "An India soyabean leaf dataset.zip",
    "maize":      BASE_DIR / "test_specimens" / "maize_repo" / "Kdr_field_Dataset.zip",
}

# ── Class Name Mapping ─────────────────────────────────────────────────────────
# Format: "source folder name (lowercase)" -> "AeroCrop___ClassName"
# Entries with None are SKIPPED (fruits, non-leaf, duplicates)
CLASS_MAP = {

    # ── SUGARCANE (Mendeley 355y629ynj) ─────────────────────────────────────
    "healthy leaves":        "Sugarcane___healthy",          # already exists -> MERGE
    "dried leaves":          "Sugarcane___Dried_leaf",
    "pokkah boeng":          "Sugarcane___Pokkah_boeng",
    "banded chlorosis":      "Sugarcane___Banded_chlorosis",
    "viral disease":         "Sugarcane___Mosaic",           # Viral = Mosaic -> MERGE
    "smut":                  "Sugarcane___Smut",
    "sett rot":              "Sugarcane___Sett_rot",
    "brown spot":            "Sugarcane___Brown_spot",
    "yellow leaf":           "Sugarcane___Yellow_leaf",      # already exists -> MERGE
    "brownrust":             "Sugarcane___Rust",             # already exists -> MERGE
    "brown rust":            "Sugarcane___Rust",             # already exists -> MERGE
    "grassy shoot":          "Sugarcane___Grassy_shoot",

    # ── BANANA (Mendeley 5nfjzntwd8) ────────────────────────────────────────
    "anthracnose":                   "Banana___Anthracnose",
    "banana fruit-scarring beetle":  "Banana___Fruit_scarring_beetle",
    "banana skipper damage":         "Banana___Skipper_damage",
    "banana split peel":             "Banana___Split_peel",
    "black sigatoka":                "Banana___Black_Sigatoka",
    "yellow sigatoka":               "Banana___Sigatoka",    # already exists -> MERGE
    "healthy banana":                "Banana___healthy",     # already exists -> MERGE
    "healthy banana leaf":           "Banana___healthy",     # already exists -> MERGE
    "healthy leaf":                  "Banana___healthy",     # already exists -> MERGE
    "panama wilt disease":           "Banana___Panama_disease",  # already exists -> MERGE
    "chewing insect damage on banana leaf": "Banana___Chewing_insect",

    # ── ORANGE / CITRUS (Mendeley 3f83gxmv57) ───────────────────────────────
    # Leaf classes only (skip fruit classes)
    "canker":       "Orange___Canker",
    "blackspot":    "Orange___Black_spot",
    "greening":     "Orange___Haunglongbing_(Citrus_greening)",  # already exists -> MERGE
    "melanose":     "Orange___Melanose",
    "healthy":      None,   # ambiguous — skip root-level healthy
    # Fruit folders -> skip
    "diseased fruit": None,
    "healthy fruit":  None,

    # ── TURMERIC A (Mendeley jtttfbx342) ────────────────────────────────────
    "aphids_disease":  "Turmeric___Aphid",
    "leaf_blotch":     "Turmeric___Leaf_blotch",    # already exists -> MERGE
    "leaf_spot":       "Turmeric___Leaf_spot",
    "healthy_leaf":    "Turmeric___healthy",         # already exists -> MERGE

    # ── TURMERIC B (Augmented Dataset) ──────────────────────────────────────
    "dry leaf":              "Turmeric___Dry_leaf",       # already exists -> MERGE
    "healthy leaf":          "Turmeric___healthy",        # already exists -> MERGE
    "leaf blotch":           "Turmeric___Leaf_blotch",   # already exists -> MERGE
    "rhizome disease root":  "Turmeric___Rhizome_rot",   # already exists -> MERGE
    "rhizome healthy root":  "Turmeric___Rhizome_healthy",

    # ── PLANTDOC (Corn/Maize extra classes) ─────────────────────────────────
    "corn gray leaf spot":   "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",  # MERGE
    "corn leaf blight":      "Corn_(maize)___Northern_Leaf_Blight",                # MERGE
    "corn rust leaf":        "Corn_(maize)___Common_rust_",                        # MERGE
    # Skip non-target PlantDoc classes
    "apple scab leaf":       None,
    "apple leaf":            None,
    "apple rust leaf":       None,
    "bell_pepper leaf spot": None,
    "bell_pepper leaf":      None,
    "blueberry leaf":        None,
    "cherry leaf":           None,
    "peach leaf":            None,
    "potato leaf early blight": None,
    "potato leaf late blight":  None,
    "raspberry leaf":        None,
    "soyabean leaf":         "Soybean___healthy",
    "squash powdery mildew leaf": None,
    "strawberry leaf":       None,
    "tomato early blight leaf":  None,
    "tomato septoria leaf spot":  None,
    "tomato leaf bacterial spot": None,
    "tomato leaf late blight":   None,
    "tomato leaf mosaic virus":  None,
    "tomato leaf yellow virus":  None,
    "tomato leaf":           None,

    # ── POTATO (Mendeley ptz377bwb8) ────────────────────────────────────────
    "bacteria":      "Potato___Bacterial_wilt",
    "fungi":         "Potato___Fungal_disease",
    "nematode":      "Potato___Nematode",
    "pest":          "Potato___Pest_damage",
    "phytophthora":  "Potato___Late_blight",    # already exists -> MERGE
    "virus":         "Potato___Mosaic_virus",
    # "healthy" handled separately below

    # ── SOYBEAN (India dataset) ──────────────────────────────────────────────
    "vein necrosis":     "Soybean___Vein_necrosis",
    "dry leaf":          "Soybean___Dry_leaf",
    "septoria brown spot": "Soybean___Brown_spot",
    "bacterial leaf blight": "Soybean___Bacterial_blight",
    # "healthy" / "root images" handled below

    # ── MAIZE (Kdr field dataset — if applicable) ───────────────────────────
    # Will be handled if extracted classes match
}

# Special: "healthy" folder under Potato should map to Potato___healthy
POTATO_HEALTHY_KEYS = {"healthy", "healthy potatoes", "healthy potato"}
SOYBEAN_HEALTHY_KEYS = {"healthy plants", "healthy", "healthy soybean"}


def find_image_files(folder: Path):
    """Recursively find all image files."""
    exts = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    return [f for f in folder.rglob('*') if f.suffix in exts]


def extract_zip_recursive(zip_path: Path, dest: Path):
    """Extract a ZIP. If nested ZIPs found, extract those too."""
    dest.mkdir(parents=True, exist_ok=True)
    print(f"  Extracting: {zip_path.name} -> {dest}")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest)

    # Find and extract nested ZIPs
    for nested in dest.rglob('*.zip'):
        nested_dest = nested.parent / nested.stem
        if not nested_dest.exists():
            print(f"    Extracting nested: {nested.name}")
            try:
                with zipfile.ZipFile(nested, 'r') as zf:
                    zf.extractall(nested_dest)
            except Exception as e:
                print(f"    WARNING: Could not extract {nested.name}: {e}")


def get_aerocrop_class(folder_name: str, context: str = ""):
    """Map a source folder name to AeroCrop class string."""
    key = folder_name.lower().strip()

    # Context-specific overrides
    if context == "potato" and key in POTATO_HEALTHY_KEYS:
        return "Potato___healthy"
    if context == "soybean" and key in SOYBEAN_HEALTHY_KEYS:
        return "Soybean___healthy"
    if context == "citrus" and key == "healthy":
        return "Orange___healthy"

    return CLASS_MAP.get(key, None)


def copy_images_to_split(images: list, aerocrop_class: str, label: str = ""):
    """Split images 80/20 and copy to train/valid folders."""
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
            # Avoid collision: add suffix
            dest = train_class_dir / f"{img.stem}_{label}{img.suffix}"
        shutil.copy2(img, dest)
        copied_train += 1

    copied_valid = 0
    for img in valid_imgs:
        dest = valid_class_dir / img.name
        if dest.exists():
            dest = valid_class_dir / f"{img.stem}_{label}{img.suffix}"
        shutil.copy2(img, dest)
        copied_valid += 1

    return copied_train, copied_valid


def process_class_folder(folder: Path, context: str, dataset_label: str):
    """Process one class folder: map name -> AeroCrop class, copy images."""
    aerocrop_class = get_aerocrop_class(folder.name, context)

    if aerocrop_class is None:
        print(f"    SKIP  '{folder.name}' (no mapping or excluded)")
        return

    images = find_image_files(folder)
    if not images:
        print(f"    SKIP  '{folder.name}' -> '{aerocrop_class}' (0 images found)")
        return

    t, v = copy_images_to_split(images, aerocrop_class, dataset_label)
    existing_train = len(list((TRAIN_DIR / aerocrop_class).iterdir())) if (TRAIN_DIR / aerocrop_class).exists() else 0
    print(f"    OK  '{folder.name}' -> '{aerocrop_class}' | +{t} train / +{v} valid (total train: {existing_train})")


# ── INGEST FUNCTIONS PER DATASET ───────────────────────────────────────────────

def ingest_sugarcane():
    print("\n[1/8] SUGARCANE — Sugarcane Leaf Dataset.zip")
    dest = EXTRACT_TMP / "sugarcane"
    extract_zip_recursive(DATASET_ZIPS["sugarcane"], dest)

    # Each inner ZIP is a class folder
    for inner_zip in sorted(dest.rglob("*.zip")):
        class_name = inner_zip.stem  # e.g. "Dried Leaves", "smut"
        class_extracted = inner_zip.parent / class_name
        if not class_extracted.exists():
            try:
                with zipfile.ZipFile(inner_zip) as zf:
                    zf.extractall(class_extracted)
            except Exception as e:
                print(f"  WARNING: {inner_zip.name}: {e}")
                continue
        process_class_folder(class_extracted, "sugarcane", "sc")

    # Also check if any direct image folders extracted
    for d in sorted(dest.iterdir()):
        if d.is_dir() and not any(d.rglob("*.zip")):
            process_class_folder(d, "sugarcane", "sc")


def ingest_banana():
    print("\n[2/8] BANANA — Banana and Banana Leaf Dataset for Classification.zip")
    dest = EXTRACT_TMP / "banana"
    extract_zip_recursive(DATASET_ZIPS["banana"], dest)

    # Use AUGMENTED version (nested ZIP inside)
    aug_inner = list(dest.rglob("*Augmented*.zip"))
    if aug_inner:
        aug_dir = aug_inner[0].parent / aug_inner[0].stem
        if not aug_dir.exists():
            with zipfile.ZipFile(aug_inner[0]) as zf:
                zf.extractall(aug_dir)
        # Find class folders
        for d in sorted(aug_dir.rglob("*")):
            if d.is_dir() and find_image_files(d):
                process_class_folder(d, "banana", "bn")
    else:
        for d in sorted(dest.rglob("*")):
            if d.is_dir() and find_image_files(d):
                process_class_folder(d, "banana", "bn")


def ingest_citrus():
    print("\n[3/8] ORANGE/CITRUS — Citrus Dataset.zip")
    dest = EXTRACT_TMP / "citrus"
    extract_zip_recursive(DATASET_ZIPS["citrus"], dest)

    # Find Citrus.zip inside and extract
    inner = list(dest.rglob("Citrus.zip"))
    if inner:
        citrus_dir = inner[0].parent / "Citrus"
        if not citrus_dir.exists():
            with zipfile.ZipFile(inner[0]) as zf:
                zf.extractall(citrus_dir)

        # Process leaf sub-folders only (skip fruit)
        for d in sorted(citrus_dir.rglob("*")):
            if d.is_dir() and "leaf" in d.name.lower() and find_image_files(d):
                process_class_folder(d, "citrus", "ct")
            elif d.is_dir() and d.name.lower() in CLASS_MAP and find_image_files(d):
                process_class_folder(d, "citrus", "ct")


def ingest_turmeric():
    print("\n[4/8] TURMERIC A — Image Dataset for Turmeric Plant Leaf Disease Detection.zip")
    dest_a = EXTRACT_TMP / "turmeric_a"
    extract_zip_recursive(DATASET_ZIPS["turmeric_a"], dest_a)

    # Use Augmented DataSet subfolder
    aug_dir = dest_a / "Image Dataset for Turmeric Plant Leaf Disease Detection" / "Augmented DataSet"
    if not aug_dir.exists():
        aug_dir = dest_a  # fallback
    for d in sorted(aug_dir.iterdir()):
        if d.is_dir():
            process_class_folder(d, "turmeric", "ta")

    print("\n[5/8] TURMERIC B — Turmeric Plant Disease Augmented Dataset.zip")
    dest_b = EXTRACT_TMP / "turmeric_b"
    extract_zip_recursive(DATASET_ZIPS["turmeric_b"], dest_b)
    root = dest_b / "Turmeric Plant Disease Augmented Dataset"
    if not root.exists():
        root = dest_b
    for d in sorted(root.iterdir()):
        if d.is_dir():
            process_class_folder(d, "turmeric", "tb")


def ingest_plantdoc():
    print("\n[6/8] CORN (PlantDoc extra classes) — PlantDoc-Dataset-master.zip")
    dest = EXTRACT_TMP / "plantdoc"
    extract_zip_recursive(DATASET_ZIPS["plantdoc"], dest)

    # Use train folder (larger)
    for split in ["train", "test"]:
        split_dir = dest / "PlantDoc-Dataset-master" / split
        if split_dir.exists():
            for d in sorted(split_dir.iterdir()):
                if d.is_dir():
                    process_class_folder(d, "plantdoc", "pd")


def ingest_potato():
    print("\n[7/8] POTATO — Potato Leaf Disease Dataset in Uncontrolled Environment.zip")
    dest = EXTRACT_TMP / "potato"
    extract_zip_recursive(DATASET_ZIPS["potato"], dest)

    root = dest / "Potato Leaf Disease Dataset in Uncontrolled Environment"
    if not root.exists():
        root = dest
    for d in sorted(root.iterdir()):
        if d.is_dir():
            process_class_folder(d, "potato", "pt")


def ingest_soybean():
    print("\n[8/8] SOYBEAN — An India soyabean leaf dataset.zip")
    z = DATASET_ZIPS["soybean"]
    if not z.exists():
        print("  SKIP: soybean ZIP not found (permission issue at download time)")
        return
    dest = EXTRACT_TMP / "soybean"
    extract_zip_recursive(z, dest)

    for d in sorted(dest.rglob("*")):
        if d.is_dir() and find_image_files(d):
            process_class_folder(d, "soybean", "sb")


# ── SUMMARY ───────────────────────────────────────────────────────────────────

def print_summary():
    print("\n" + "="*70)
    print("FINAL CLASS SUMMARY")
    print("="*70)

    crops = {}
    for d in sorted(TRAIN_DIR.iterdir()):
        if not d.is_dir():
            continue
        crop = d.name.split("___")[0]
        count = len([f for f in d.rglob("*") if f.suffix.lower() in {'.jpg','.jpeg','.png'}])
        crops.setdefault(crop, []).append((d.name, count))

    for crop, classes in sorted(crops.items()):
        total = sum(c for _, c in classes)
        ok = "OK" if len(classes) >= 10 else "!"
        print(f"\n{ok} {crop}: {len(classes)} classes, {total} train images")
        for cls, cnt in sorted(classes):
            disease = cls.split("___")[1] if "___" in cls else cls
            print(f"     - {disease}: {cnt}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("AeroCrop.ai Dataset Ingestion")
    print(f"  Train dir : {TRAIN_DIR}")
    print(f"  Valid dir : {VALID_DIR}")
    print(f"  Tmp dir   : {EXTRACT_TMP}")
    print(f"  Valid %   : {int(VALID_RATIO*100)}%")
    print()

    EXTRACT_TMP.mkdir(parents=True, exist_ok=True)

    ingest_sugarcane()
    ingest_banana()
    ingest_citrus()
    ingest_turmeric()
    ingest_plantdoc()
    ingest_potato()
    ingest_soybean()

    print_summary()

    print("\nOK Done! Check data/main dataset/train for new class folders.")
    print("  Run 'python model/train.py' to retrain with expanded dataset.")
