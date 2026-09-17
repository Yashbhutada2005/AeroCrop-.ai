"""
Script to generate backend/services/disease_service.py with complete 134-class coverage.
"""
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "backend"))

with open(os.path.join(ROOT, "model", "classes.json"), "r", encoding="utf-8") as f:
    classes = json.load(f)

# Load existing 50 classes to preserve any hand-curated details
existing_map = {}
try:
    from services.disease_service import DiseaseService
    for d in DiseaseService.DISEASES:
        # Match by name or class_idx
        existing_map[d.name.lower()] = d
except Exception as e:
    print(f"Notice: Could not load existing DiseaseService: {e}")

def determine_treatment_and_severity(crop: str, cond: str):
    cond_lower = cond.lower()
    
    if "healthy" in cond_lower:
        return (
            [],
            [],
            "None",
            f"Healthy, vigorous {crop} foliage showing robust chlorophyll development with no symptoms of fungal, bacterial, viral infection, or insect pest infestation."
        )

    # 1. Pests and Insects
    if any(k in cond_lower for k in ["aphid", "caterpillar", "army_worm", "armyworm", "grasshopper", "beetle", "jassid", "mite", "stem_fly", "hispa", "whitefly", "mealybug", "skipper", "chewing", "insect", "dead_heart", "nematode"]):
        if "mite" in cond_lower:
            chem = ["Spiromesifen 22.9SC (1 ml/L)", "Propargite 57EC (2 ml/L)", "Abamectin 1.9EC (0.5 ml/L)"]
            org = ["Neem oil 1500 ppm (3 ml/L)", "Wettable sulfur (2.5 g/L)", "Predatory mites (Phytoseiidae)"]
            sev = "Moderate"
            desc = f"Mite infestation causing micro-punctures on {crop} leaves, resulting in stippling, webbing, and bronzing."
        elif any(k in cond_lower for k in ["aphid", "jassid", "whitefly", "mealybug"]):
            chem = ["Imidacloprid 17.8SL (0.5 ml/L)", "Acetamiprid 20SP (0.2 g/L)", "Thiamethoxam 25WG (0.3 g/L)"]
            org = ["Neem oil foliar spray (3 ml/L)", "Yellow sticky traps (10/acre)", "Verticillium lecanii bio-agent (5 g/L)"]
            sev = "Moderate"
            desc = f"Sucking pest infestation on {crop} causing leaf curling, honeydew excretion, and sooty mold development."
        elif any(k in cond_lower for k in ["armyworm", "army_worm", "caterpillar"]):
            chem = ["Emamectin Benzoate 5SG (0.4 g/L)", "Chlorantraniliprole 18.5SC (0.3 ml/L)", "Spinetoram 11.7SC (1 ml/L)"]
            org = ["Bacillus thuringiensis (Bt) spray (2 g/L)", "Pheromone traps (5/acre)", "Beauveria bassiana (5 g/L)"]
            sev = "High"
            desc = f"Aggressive foliar feeding by larvae causing extensive skeletonization and defoliation on {crop} leaves."
        elif "dead_heart" in cond_lower or "stem_fly" in cond_lower:
            chem = ["Cartap Hydrochloride 50SP (2 g/L)", "Chlorantraniliprole 0.4G (4 kg/acre granules)", "Fipronil 5SC (2 ml/L)"]
            org = ["Trichogramma egg parasitoid cards (2/acre)", "Neem cake soil application (100 kg/acre)", "Pheromone monitoring"]
            sev = "High"
            desc = f"Borer attack causing drying of the central growing shoot ('dead heart') in young {crop} plants."
        else:
            chem = ["Chlorpyrifos 20EC (2 ml/L)", "Quinalphos 25EC (2 ml/L)", "Lambda-cyhalothrin 5EC (1 ml/L)"]
            org = ["Neem oil 1500 ppm (3 ml/L)", "Beauveria bassiana (5 g/L)", "Light traps (1/acre)"]
            sev = "Moderate"
            desc = f"Insect pest damage characterized by chewing, scratching, or tissue feeding on {crop} foliage."
        return chem, org, sev, desc

    # 2. Viral Diseases
    if any(k in cond_lower for k in ["virus", "mosaic", "curl", "streak", "tungro", "chlorotic"]):
        chem = ["Thiamethoxam 25WG (0.3 g/L foliar)", "Imidacloprid 17.8SL (0.5 ml/L for vector control)", "Dinotefuran 20SG (0.5 g/L)"]
        org = ["Rogue and incinerate infected plants", "Yellow/Blue sticky traps (12/acre)", "Reflective silver mulches", "Plant barrier crops (maize/sorghum border)"]
        sev = "Critical"
        desc = f"Systemic viral infection in {crop} causing mosaic chlorosis, severe leaf curling, stunting, and yield suppression."
        return chem, org, sev, desc

    # 3. Bacterial Diseases
    if any(k in cond_lower for k in ["bacterial", "canker", "soft_rot", "blackleg"]):
        chem = ["Copper Oxychloride 50WP (2.5 g/L) + Streptocycline (0.1 g/L)", "Kasugamycin 3% SL (2 ml/L)", "Copper Hydroxide 53.8DF (2 g/L)"]
        org = ["Pseudomonas fluorescens (10 g/L spray/drench)", "Avoid overhead irrigation", "Sterilize pruning tools with 10% bleach", "Crop rotation"]
        sev = "High"
        desc = f"Bacterial infection causing water-soaked necrotic lesions, vascular wilting, or soft tissue breakdown on {crop}."
        return chem, org, sev, desc

    # 4. Wilts, Rots and Soil-borne
    if any(k in cond_lower for k in ["wilt", "fusarium", "rhizome_rot", "pink_rot", "dry_rot", "sett_rot", "red_rot", "panama", "moko"]):
        chem = ["Carbendazim 50WP (2 g/L soil drench)", "Metalaxyl 8% + Mancozeb 64% WP (2.5 g/L)", "Thiophanate-Methyl 70WP (1.5 g/L)"]
        org = ["Trichoderma harzianum soil inoculation (2 kg/acre with FYM)", "Ensure proper drainage ridges", "Seed/Rhizome treatment with bio-agents", "Crop rotation"]
        sev = "Critical"
        desc = f"Destructive vascular or root/rhizome pathogen causing internal vascular discoloration, wilting, or decay in {crop}."
        return chem, org, sev, desc

    # 5. Rusts and Smuts
    if any(k in cond_lower for k in ["rust", "smut"]):
        chem = ["Propiconazole 25EC (1 ml/L)", "Tebuconazole 25.9EC (1 ml/L)", "Hexaconazole 5EC (1 ml/L)", "Mancozeb 75WP (2 g/L)"]
        org = ["Sulfur 80WP dusting (2.5 g/L)", "Resistant cultivars", "Avoid dense planting to reduce microclimate humidity"]
        sev = "High"
        desc = f"Pathogen characterized by powdery pustules (uredinia/telia) erupting through the epidermal surface of {crop} leaves."
        return chem, org, sev, desc

    # 6. Blights, Leaf Spots, Mildews, Anthracnose, Scab (General Fungi)
    chem = ["Mancozeb 75WP (2.5 g/L)", "Azoxystrobin 18.2% + Difenoconazole 11.4% SC (1 ml/L)", "Carbendazim 12% + Mancozeb 63% WP (Saaf 2 g/L)"]
    org = ["Neem oil 1500 ppm (3 ml/L)", "Bordeaux mixture 1%", "Trichoderma viride foliar spray (5 g/L)", "Pruning diseased lower leaves"]
    sev = "High" if any(k in cond_lower for k in ["late_blight", "blast", "anthracnose", "severe"]) else "Moderate"
    desc = f"Fungal infection producing circular to irregular chlorotic lesions, necrotic spots, or foliar blighting on {crop} leaves."
    return chem, org, sev, desc

lines = [
    '"""',
    'AeroCrop.ai — Disease Service',
    '',
    'Provides:',
    '  - Authoritative 134-class agricultural pathology taxonomy across 11 core crops',
    '  - Targeted chemical + organic treatment prescriptions',
    '  - Crop-specific severity flags',
    '',
    'IMPORTANT: Class indices in DISEASES list match model/classes.json exactly (0 to 133).',
    '"""',
    '',
    'from __future__ import annotations',
    'from dataclasses import dataclass, field',
    'from typing import ClassVar',
    '',
    '',
    '@dataclass',
    'class DiseaseInfo:',
    '    class_idx:   int',
    '    name:        str',
    '    crop:        str',
    '    is_healthy:  bool',
    '    chemical_treatment: list[str] = field(default_factory=list)',
    '    organic_treatment:  list[str] = field(default_factory=list)',
    '    severity:    str = "None"  # None | Low | Moderate | High | Critical',
    '    description: str = ""',
    '',
    '',
    'class DiseaseService:',
    '    """',
    '    Comprehensive service exposing the 134-class pathology knowledge base.',
    '    Class indices match model/classes.json exactly (0 to 133).',
    '    """',
    '',
    '    DISEASES: ClassVar[list[DiseaseInfo]] = ['
]

for idx, c in enumerate(classes):
    crop_raw, cond_raw = c.split("___")
    crop_name = crop_raw.replace("Corn_(maize)", "Maize").replace("_", " ").capitalize()
    is_healthy = "healthy" in cond_raw.lower()
    
    # Form human readable name
    cond_clean = cond_raw.replace("_", " ")
    if is_healthy:
        full_name = f"{crop_name} — Healthy"
    else:
        full_name = f"{crop_name} — {cond_clean}"

    # Check if an existing detailed description can be reused
    matched_existing = None
    for name_key, d_obj in existing_map.items():
        if cond_clean.lower() in name_key and crop_name.lower() in name_key:
            matched_existing = d_obj
            break

    if matched_existing and is_healthy == matched_existing.is_healthy:
        chem = matched_existing.chemical_treatment
        org = matched_existing.organic_treatment
        sev = matched_existing.severity
        desc = matched_existing.description
        full_name = matched_existing.name
    else:
        chem, org, sev, desc = determine_treatment_and_severity(crop_name, cond_clean)

    # Format entry
    lines.append(f"        DiseaseInfo(")
    lines.append(f"            class_idx={idx},")
    lines.append(f"            name={json.dumps(full_name)},")
    lines.append(f"            crop={json.dumps(crop_name)},")
    lines.append(f"            is_healthy={is_healthy},")
    lines.append(f"            chemical_treatment={json.dumps(chem)},")
    lines.append(f"            organic_treatment={json.dumps(org)},")
    lines.append(f"            severity={json.dumps(sev)},")
    lines.append(f"            description={json.dumps(desc)},")
    lines.append(f"        ),")

lines.extend([
    '    ]',
    '',
    '    # Fast lookup dict',
    '    _by_idx: ClassVar[dict[int, DiseaseInfo]] = {}',
    '',
    '    @classmethod',
    '    def _ensure_index(cls):',
    '        if not cls._by_idx:',
    '            cls._by_idx = {d.class_idx: d for d in cls.DISEASES}',
    '',
    '    @classmethod',
    '    def get_by_index(cls, idx: int) -> DiseaseInfo | None:',
    '        cls._ensure_index()',
    '        if idx in cls._by_idx:',
    '            return cls._by_idx[idx]',
    '        # Dynamic fallback for safety',
    '        if 0 <= idx < len(cls.DISEASES):',
    '            return cls.DISEASES[idx]',
    '        return None',
    '',
    '    @classmethod',
    '    def get_all_names(cls) -> list[str]:',
    '        return [d.name for d in cls.DISEASES]',
    '',
    '    @classmethod',
    '    def get_class_count(cls) -> int:',
    '        return len(cls.DISEASES)',
    ''
])

out_file = os.path.join(ROOT, "backend", "services", "disease_service.py")
with open(out_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Successfully generated {out_file} with {len(classes)} classes!")
