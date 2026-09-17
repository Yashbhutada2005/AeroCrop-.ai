"""
Ingest Orange Black Spot & Scab from Citrus dataset,
and Banana Bract Mosaic Virus & Moko Disease from archive (5).zip.
"""
import zipfile
import shutil
import random
from pathlib import Path

BASE_DIR  = Path(r"D:\Codes\final_year_project")
TRAIN_DIR = BASE_DIR / "data" / "main dataset" / "train"
VALID_DIR = BASE_DIR / "data" / "main dataset" / "valid"
CITRUS_DIR = BASE_DIR / "data" / "raw_extracted" / "citrus"
ARCHIVE5   = Path(r"C:\Users\devan\Downloads\archive (5).zip")

VALID_RATIO = 0.20
random.seed(42)
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

def imgs(p):
    return [f for f in p.rglob('*') if f.suffix in IMAGE_EXTS]

def copy_split(images, cls, label=""):
    if not images: return 0, 0
    s = images.copy()
    random.shuffle(s)
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

def process(folder, cls, label):
    im_list = imgs(folder)
    if not im_list:
        print(f"  SKIP '{folder.name}' (0 images)")
        return
    t, v = copy_split(im_list, cls, label)
    total = len(list((TRAIN_DIR / cls).iterdir())) if (TRAIN_DIR / cls).exists() else 0
    print(f"  OK '{folder.name}' -> '{cls}' | +{t} train / +{v} valid (total train: {total})")

print("--- 1. INGESTING ORANGE CLASSES ---")
# Black spot leaves
bs_leaf = list(CITRUS_DIR.rglob("Black spot"))
for f in bs_leaf:
    if "leaves" in str(f).lower():
        process(f, "Orange___Black_spot", "ct_leaf")
    elif "fruits" in str(f).lower():
        process(f, "Orange___Black_spot", "ct_fruit")

scab = list(CITRUS_DIR.rglob("Scab"))
for f in scab:
    process(f, "Orange___Scab", "ct_fruit")

print("\n--- 2. INGESTING BANANA RECOGNITION (archive (5).zip) ---")
tmp_b5 = BASE_DIR / "data" / "raw_extracted" / "banana5"
tmp_b5.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(ARCHIVE5) as zf:
    zf.extractall(tmp_b5)

b5_map = {
    "bract mosaic virus": "Banana___Bract_mosaic_virus",
    "moko disease": "Banana___Moko_disease",
    "insect pest": "Banana___Chewing_insect",
    "black sigatoka": "Banana___Black_Sigatoka",
    "yellow sigatoka": "Banana___Sigatoka",
    "panama disease": "Banana___Panama_disease",
    "healthy leaf": "Banana___healthy",
}

for d in tmp_b5.rglob('*'):
    if not d.is_dir(): continue
    name_lower = d.name.lower()
    for key, cls in b5_map.items():
        if key in name_lower:
            label = "b5_aug" if "augmented" in str(d).lower() else "b5_orig"
            process(d, cls, label)
            break

print("\n--- COMPLETED ---")
