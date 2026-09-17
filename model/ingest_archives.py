"""
AeroCrop.ai — Final Remaining Archives Ingestion
Processes all archive(N).zip files that were missed:
  archive.zip    -> PlantVillage full dataset (tomato, potato, corn already exist - skip dupes)
  archive (2).zip -> Cotton Disease (diseased/fresh classes)
  archive (3).zip -> Banana v2 (Cordana, Healthy, Panama, Black+Yellow Sigatoka)
  archive (4).zip -> Sugarcane v2 (Healthy, Mosaic, RedRot, Rust, Yellow)
  archive (5).zip -> Banana Recognition Dataset
  archive (6).zip -> Turmeric extra (Dry Leaf, Healthy, Leaf Blotch, Rhizome Rot)
  archive (8).zip -> Cotton (Aphids, Army Worm, Curl Virus, Fusarium, Powdery Mildew, Target Spot, Bacterial Blight, Healthy)
  soybean ZIP    -> copy from D:/data/ to bypass permission
"""

import zipfile, shutil, random
from pathlib import Path

BASE_DIR   = Path(r"D:\Codes\final_year_project")
DL         = Path(r"C:\Users\devan\Downloads")
TRAIN_DIR  = BASE_DIR / "data" / "main dataset" / "train"
VALID_DIR  = BASE_DIR / "data" / "main dataset" / "valid"
TMP        = BASE_DIR / "data" / "raw_extracted"
VALID_RATIO = 0.20
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}


def imgs(folder):
    try:
        return [f for f in folder.rglob('*') if f.suffix in IMAGE_EXTS]
    except:
        return []


def copy_split(images, cls, label=""):
    if not images: return 0, 0
    s = images.copy(); random.shuffle(s)
    nv = max(1, int(len(s) * VALID_RATIO))
    for img in s[:nv]:
        d = VALID_DIR / cls / img.name
        (VALID_DIR / cls).mkdir(parents=True, exist_ok=True)
        if d.exists(): d = VALID_DIR / cls / f"{img.stem}_{label}{img.suffix}"
        try: shutil.copy2(img, d)
        except: pass
    for img in s[nv:]:
        d = TRAIN_DIR / cls / img.name
        (TRAIN_DIR / cls).mkdir(parents=True, exist_ok=True)
        if d.exists(): d = TRAIN_DIR / cls / f"{img.stem}_{label}{img.suffix}"
        try: shutil.copy2(img, d)
        except: pass
    return len(s[nv:]), nv


def extract(zip_path, dest):
    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.iterdir()) if dest.exists() else False:
        print(f"  Already extracted: {dest.name}")
        return
    print(f"  Extracting {zip_path.name} ...")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)


def process(folder, cls, label):
    images = imgs(folder)
    if not images:
        print(f"    SKIP '{folder.name}' - 0 images")
        return
    t, v = copy_split(images, cls, label)
    total = len(list((TRAIN_DIR / cls).iterdir())) if (TRAIN_DIR / cls).exists() else 0
    print(f"    OK  '{folder.name}' -> '{cls}' | +{t} train / +{v} valid (total: {total})")


# ─────────────────────────────────────────────────────────────────────────────
# COTTON — archive (8).zip: Aphids, ArmyWorm, Bacterial Blight, Curl Virus,
#          Fusarium Wilt, Healthy, Powdery Mildew, Target Spot
# ─────────────────────────────────────────────────────────────────────────────
COTTON8_MAP = {
    "aphids":          "Cotton___Aphid",
    "army worm":       "Cotton___Army_worm",
    "bacterial blight":"Cotton___Bacterial_blight",   # already exists -> MERGE
    "curl virus":      "Cotton___Curl_virus",
    "fussarium wilt":  "Cotton___Fusarium_wilt",
    "fusarium wilt":   "Cotton___Fusarium_wilt",
    "healthy":         "Cotton___healthy",            # already exists -> MERGE
    "healthy leaf":    "Cotton___healthy",
    "powdery mildew":  "Cotton___Powdery_mildew",
    "target spot":     "Cotton___Target_spot",
}

def ingest_cotton8():
    print("\n[COTTON] archive (8).zip - 8 disease classes")
    dest = TMP / "cotton8"
    extract(DL / "archive (8).zip", dest)
    # Use 'train' split inside
    train_dir = dest / "train"
    if not train_dir.exists(): train_dir = dest
    for d in sorted(train_dir.iterdir()):
        if not d.is_dir(): continue
        cls = COTTON8_MAP.get(d.name.lower().strip())
        if cls is None:
            print(f"    SKIP '{d.name}'")
            continue
        process(d, cls, "c8")


# ─────────────────────────────────────────────────────────────────────────────
# COTTON — archive (2).zip: diseased cotton leaf, fresh cotton leaf
# ─────────────────────────────────────────────────────────────────────────────
COTTON2_MAP = {
    "diseased cotton leaf":  "Cotton___Diseased_leaf",
    "diseased cotton plant": None,   # plant-level, skip
    "fresh cotton leaf":     "Cotton___healthy",
    "fresh cotton plant":    None,
}

def ingest_cotton2():
    print("\n[COTTON] archive (2).zip - diseased/healthy leaf")
    dest = TMP / "cotton2"
    extract(DL / "archive (2).zip", dest)
    root = dest / "Cotton Disease" / "train"
    if not root.exists(): root = dest
    for d in sorted(root.rglob("*")):
        if not d.is_dir(): continue
        cls = COTTON2_MAP.get(d.name.lower().strip())
        if cls is None: continue
        process(d, cls, "c2")


# ─────────────────────────────────────────────────────────────────────────────
# BANANA — archive (3).zip: Cordana, Healthy, Panama Disease, Yellow+Black Sigatoka
# ─────────────────────────────────────────────────────────────────────────────
BANANA3_MAP = {
    "cordana":                   "Banana___Cordana_leaf_spot",   # already exists -> MERGE
    "healthy":                   "Banana___healthy",
    "panama disease":            "Banana___Panama_disease",
    "yellow and black sigatoka": "Banana___Black_Sigatoka",      # merge into Black Sigatoka
}

def ingest_banana3():
    print("\n[BANANA] archive (3).zip - Cordana, Panama, Sigatoka, Healthy")
    dest = TMP / "banana3"
    extract(DL / "archive (3).zip", dest)
    for d in sorted(dest.iterdir()):
        if not d.is_dir(): continue
        cls = BANANA3_MAP.get(d.name.lower().strip())
        if cls is None:
            print(f"    SKIP '{d.name}'")
            continue
        process(d, cls, "b3")


# ─────────────────────────────────────────────────────────────────────────────
# BANANA — archive (5).zip: Banana Disease Recognition Dataset
# ─────────────────────────────────────────────────────────────────────────────
BANANA5_MAP = {
    "bract mosaic virus":   "Banana___Bract_mosaic_virus",
    "healthy":              "Banana___healthy",
    "insect pest":          "Banana___Chewing_insect",      # merge
    "moko disease":         "Banana___Moko_disease",
    "panama disease":       "Banana___Panama_disease",
    "yellow sigatoka":      "Banana___Sigatoka",
    "black sigatoka":       "Banana___Black_Sigatoka",
}

def ingest_banana5():
    print("\n[BANANA] archive (5).zip - Disease Recognition Dataset")
    dest = TMP / "banana5"
    extract(DL / "archive (5).zip", dest)
    # Look for Augmented images subfolder
    aug = list(dest.rglob("Augmented images"))
    search_root = aug[0] if aug else dest
    for d in sorted(search_root.rglob("*")):
        if not d.is_dir(): continue
        images = imgs(d)
        if not images: continue
        cls = BANANA5_MAP.get(d.name.lower().strip())
        if cls is None: continue
        process(d, cls, "b5")


# ─────────────────────────────────────────────────────────────────────────────
# SUGARCANE — archive (4).zip: Healthy, Mosaic, RedRot, Rust, Yellow
# ─────────────────────────────────────────────────────────────────────────────
SUGARCANE4_MAP = {
    "healthy": "Sugarcane___healthy",
    "mosaic":  "Sugarcane___Mosaic",
    "redrot":  "Sugarcane___Red_rot",    # already exists -> MERGE
    "rust":    "Sugarcane___Rust",
    "yellow":  "Sugarcane___Yellow_leaf",
}

def ingest_sugarcane4():
    print("\n[SUGARCANE] archive (4).zip - 5 classes")
    dest = TMP / "sugarcane4"
    extract(DL / "archive (4).zip", dest)
    for d in sorted(dest.iterdir()):
        if not d.is_dir(): continue
        cls = SUGARCANE4_MAP.get(d.name.lower().strip())
        if cls is None:
            print(f"    SKIP '{d.name}'")
            continue
        process(d, cls, "s4")


# ─────────────────────────────────────────────────────────────────────────────
# TURMERIC — archive (6).zip: Dry Leaf, Healthy Leaf, Leaf Blotch, Rhizome Rot
# ─────────────────────────────────────────────────────────────────────────────
TURMERIC6_MAP = {
    "dry leaf":      "Turmeric___Dry_leaf",
    "healthy leaf":  "Turmeric___healthy",
    "leaf blotch":   "Turmeric___Leaf_blotch",
    "rhizome rot":   "Turmeric___Rhizome_rot",
}

def ingest_turmeric6():
    print("\n[TURMERIC] archive (6).zip - 4 classes")
    dest = TMP / "turmeric6"
    extract(DL / "archive (6).zip", dest)
    root = dest / "Turmeric Plant Disease"
    if not root.exists(): root = dest
    for d in sorted(root.iterdir()):
        if not d.is_dir(): continue
        cls = TURMERIC6_MAP.get(d.name.lower().strip())
        if cls is None:
            print(f"    SKIP '{d.name}'")
            continue
        process(d, cls, "t6")


# ─────────────────────────────────────────────────────────────────────────────
# SOYBEAN — copy from D:/data/ path (bypass Downloads permission)
# ─────────────────────────────────────────────────────────────────────────────
SOYBEAN_MAP = {
    "healthy plants":        "Soybean___healthy",
    "healthy":               "Soybean___healthy",
    "vein necrosis":         "Soybean___Vein_necrosis",
    "dry leaf":              "Soybean___Dry_leaf",
    "septoria brown spot":   "Soybean___Brown_spot",
    "bacterial leaf blight": "Soybean___Bacterial_blight",
    "root images":           None,
}

def ingest_soybean():
    print("\n[SOYBEAN] An India soyabean leaf dataset.zip")
    soy_zip = DL / "An India soyabean leaf dataset.zip"
    dest = TMP / "soybean"

    if not dest.exists() or not any(dest.iterdir()):
        dest.mkdir(parents=True, exist_ok=True)
        # Try copying to temp first to bypass permission issue
        tmp_copy = TMP / "soybean_tmp.zip"
        try:
            shutil.copy2(soy_zip, tmp_copy)
            with zipfile.ZipFile(tmp_copy) as zf:
                zf.extractall(dest)
            tmp_copy.unlink(missing_ok=True)
            print("  Extracted via temp copy")
        except Exception as e:
            print(f"  ERROR: {e}")
            print("  TIP: Right-click the ZIP -> Properties -> Unblock, then retry")
            return

    for d in sorted(dest.rglob("*")):
        if not d.is_dir(): continue
        images = imgs(d)
        if not images: continue
        cls = SOYBEAN_MAP.get(d.name.lower().strip())
        if cls is None:
            print(f"    SKIP '{d.name}'")
            continue
        process(d, cls, "sb")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
def print_summary():
    print("\n" + "="*70)
    print("FINAL CLASS SUMMARY")
    print("="*70)
    crops = {}
    for d in sorted(TRAIN_DIR.iterdir()):
        if not d.is_dir(): continue
        crop = d.name.split("___")[0]
        count = len([f for f in d.rglob("*") if f.suffix.lower() in {'.jpg','.jpeg','.png'}])
        crops.setdefault(crop, []).append((d.name, count))

    total_cls, total_imgs = 0, 0
    for crop, classes in sorted(crops.items()):
        total = sum(c for _, c in classes)
        ok = "OK" if len(classes) >= 10 else "!!"
        print(f"\n[{ok}] {crop}: {len(classes)} classes | {total} images")
        for cls, cnt in sorted(classes):
            disease = cls.split("___")[1] if "___" in cls else cls
            tag = " <-- NEW" if cnt < 500 else ""
            print(f"       - {disease}: {cnt}{tag}")
        total_cls  += len(classes)
        total_imgs += total

    print(f"\n{'='*70}")
    print(f"TOTAL: {total_cls} classes | {total_imgs} training images")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("AeroCrop.ai - Final Archives Ingestion")
    print()
    ingest_cotton8()
    ingest_cotton2()
    ingest_banana3()
    ingest_banana5()
    ingest_sugarcane4()
    ingest_turmeric6()
    ingest_soybean()
    print_summary()
    print("\nAll done!")
