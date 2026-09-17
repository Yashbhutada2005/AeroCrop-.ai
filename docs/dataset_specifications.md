# AeroCrop.ai — Dataset Specifications & Distribution

**Audit Timestamp**: 2026-09-16  
- **Total Dataset Images**: **166,630**
- **Training Images (80%)**: **133,388**
- **Validation Images (20%)**: **33,242**
- **Marked (Diseased / Symptomatic)**: **136,747** (82.1%)
- **Unmarked (Healthy / Asymptomatic)**: **29,883** (17.9%)
- **Total Diagnostic Classes**: **134**
- **Total Target Field Crops**: **11**
- **Classes Per Crop Target (>=10)**: **11 of 11 Crops Achieved (100% COMPLETE)**

## 1. Crop-Wise Breakdown

| Crop | Total Images | Train (80%) | Valid (20%) | Classes | Status (Goal >=10) | Primary Maharashtra Agro-Zone |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Banana** | 19,565 | 15,667 | 3,898 | **12** | COMPLETE (>=10) Target Met | Maharashtra (Jalgaon / Khandesh) |
| **Corn_(maize)** | 44,640 | 35,718 | 8,922 | **11** | COMPLETE (>=10) Target Met | Maharashtra (Nashik, Aurangabad, Jalna) |
| **Cotton** | 9,778 | 7,836 | 1,942 | **15** | COMPLETE (>=10) Target Met | Maharashtra (Vidarbha & Marathwada) |
| **Orange** | 8,947 | 7,167 | 1,780 | **13** | COMPLETE (>=10) Target Met | Maharashtra (Nagpur, Amravati, Wardha) |
| **Potato** | 16,039 | 12,838 | 3,201 | **18** | COMPLETE (>=10) Target Met | Maharashtra (Pune, Satara, Ahmednagar) |
| **Rice** | 15,336 | 12,271 | 3,065 | **11** | COMPLETE (>=10) Target Met | Maharashtra (Konkan, Thane, Raigad, Bhandara) |
| **Soybean** | 6,832 | 5,474 | 1,358 | **11** | COMPLETE (>=10) Target Met | Maharashtra (Latur, Nanded, Akola, Buldhana) |
| **Sugarcane** | 12,051 | 9,662 | 2,389 | **12** | COMPLETE (>=10) Target Met | Maharashtra (Kolhapur, Sangli, Pune, Solapur) |
| **Tomato** | 22,914 | 18,335 | 4,579 | **10** | COMPLETE (>=10) Target Met | Maharashtra (Nashik, Pune, Ahmednagar) |
| **Turmeric** | 8,696 | 6,959 | 1,737 | **10** | COMPLETE (>=10) Target Met | Maharashtra (Sangli, Hingoli, Nanded) |
| **Wheat** | 1,832 | 1,461 | 371 | **11** | COMPLETE (>=10) Target Met | Maharashtra (Nashik, Pune, Ahmednagar) |

---

## 2. Complete 134-Class Distribution (Marked vs Unmarked)

| Index | Canonical Class Identifier | Crop | Category | Train | Valid | Total |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | `Banana___Anthracnose` | Banana | Marked (Diseased) | 846 | 211 | 1,057 |
| `1` | `Banana___Black_Sigatoka` | Banana | Marked (Diseased) | 2,428 | 605 | 3,033 |
| `2` | `Banana___Bract_mosaic_virus` | Banana | Marked (Diseased) | 320 | 80 | 400 |
| `3` | `Banana___Chewing_insect` | Banana | Marked (Diseased) | 1,397 | 348 | 1,745 |
| `4` | `Banana___Cordana_leaf_spot` | Banana | Marked (Diseased) | 547 | 137 | 684 |
| `5` | `Banana___Fruit_scarring_beetle` | Banana | Marked (Diseased) | 846 | 211 | 1,057 |
| `6` | `Banana___Moko_disease` | Banana | Marked (Diseased) | 352 | 88 | 440 |
| `7` | `Banana___Panama_disease` | Banana | Marked (Diseased) | 2,359 | 589 | 2,948 |
| `8` | `Banana___Sigatoka` | Banana | Marked (Diseased) | 1,886 | 460 | 2,346 |
| `9` | `Banana___Skipper_damage` | Banana | Marked (Diseased) | 846 | 211 | 1,057 |
| `10` | `Banana___Split_peel` | Banana | Marked (Diseased) | 846 | 211 | 1,057 |
| `11` | `Banana___healthy` | Banana | Unmarked (Healthy) | 2,994 | 747 | 3,741 |
| `12` | `Corn_(maize)___Bacterial_leaf_streak` | Corn_(maize) | Marked (Diseased) | 152 | 38 | 190 |
| `13` | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Corn_(maize) | Marked (Diseased) | 6,196 | 1,547 | 7,743 |
| `14` | `Corn_(maize)___Chlorotic_mottle_virus` | Corn_(maize) | Marked (Diseased) | 72 | 17 | 89 |
| `15` | `Corn_(maize)___Common_rust_` | Corn_(maize) | Marked (Diseased) | 4,617 | 1,153 | 5,770 |
| `16` | `Corn_(maize)___Fall_armyworm` | Corn_(maize) | Marked (Diseased) | 2,048 | 512 | 2,560 |
| `17` | `Corn_(maize)___Grasshopper` | Corn_(maize) | Marked (Diseased) | 2,970 | 742 | 3,712 |
| `18` | `Corn_(maize)___Leaf_beetle` | Corn_(maize) | Marked (Diseased) | 2,893 | 723 | 3,616 |
| `19` | `Corn_(maize)___Lethal_necrosis` | Corn_(maize) | Marked (Diseased) | 2,585 | 646 | 3,231 |
| `20` | `Corn_(maize)___Northern_Leaf_Blight` | Corn_(maize) | Marked (Diseased) | 5,476 | 1,368 | 6,844 |
| `21` | `Corn_(maize)___Streak_virus` | Corn_(maize) | Marked (Diseased) | 2,778 | 694 | 3,472 |
| `22` | `Corn_(maize)___healthy` | Corn_(maize) | Unmarked (Healthy) | 5,931 | 1,482 | 7,413 |
| `23` | `Cotton___Alternaria_leaf_spot` | Cotton | Marked (Diseased) | 139 | 34 | 173 |
| `24` | `Cotton___Aphid` | Cotton | Marked (Diseased) | 320 | 80 | 400 |
| `25` | `Cotton___Army_worm` | Cotton | Marked (Diseased) | 320 | 80 | 400 |
| `26` | `Cotton___Bacterial_blight` | Cotton | Marked (Diseased) | 1,770 | 435 | 2,205 |
| `27` | `Cotton___Curl_virus` | Cotton | Marked (Diseased) | 665 | 166 | 831 |
| `28` | `Cotton___Diseased_leaf` | Cotton | Marked (Diseased) | 231 | 57 | 288 |
| `29` | `Cotton___Fusarium_wilt` | Cotton | Marked (Diseased) | 590 | 147 | 737 |
| `30` | `Cotton___Herbicide_damage` | Cotton | Marked (Diseased) | 224 | 56 | 280 |
| `31` | `Cotton___Jassid` | Cotton | Marked (Diseased) | 180 | 45 | 225 |
| `32` | `Cotton___Leaf_reddening` | Cotton | Marked (Diseased) | 463 | 115 | 578 |
| `33` | `Cotton___Leaf_variegation` | Cotton | Marked (Diseased) | 93 | 23 | 116 |
| `34` | `Cotton___Powdery_mildew` | Cotton | Marked (Diseased) | 320 | 80 | 400 |
| `35` | `Cotton___Target_spot` | Cotton | Marked (Diseased) | 320 | 80 | 400 |
| `36` | `Cotton___Verticillium_wilt` | Cotton | Marked (Diseased) | 250 | 62 | 312 |
| `37` | `Cotton___healthy` | Cotton | Unmarked (Healthy) | 1,951 | 482 | 2,433 |
| `38` | `Orange___Black_spot` | Orange | Marked (Diseased) | 153 | 37 | 190 |
| `39` | `Orange___Canker` | Orange | Marked (Diseased) | 665 | 164 | 829 |
| `40` | `Orange___Citrus_mealybug` | Orange | Marked (Diseased) | 483 | 120 | 603 |
| `41` | `Orange___Die_back` | Orange | Marked (Diseased) | 348 | 86 | 434 |
| `42` | `Orange___Foliage_damage` | Orange | Marked (Diseased) | 520 | 130 | 650 |
| `43` | `Orange___Haunglongbing_(Citrus_greening)` | Orange | Marked (Diseased) | 2,717 | 677 | 3,394 |
| `44` | `Orange___Melanose` | Orange | Marked (Diseased) | 11 | 2 | 13 |
| `45` | `Orange___Powdery_mildew` | Orange | Marked (Diseased) | 479 | 119 | 598 |
| `46` | `Orange___Scab` | Orange | Marked (Diseased) | 12 | 3 | 15 |
| `47` | `Orange___Shot_hole` | Orange | Marked (Diseased) | 448 | 112 | 560 |
| `48` | `Orange___Spiny_whitefly` | Orange | Marked (Diseased) | 542 | 135 | 677 |
| `49` | `Orange___Yellow_leaves` | Orange | Marked (Diseased) | 248 | 62 | 310 |
| `50` | `Orange___healthy` | Orange | Unmarked (Healthy) | 541 | 133 | 674 |
| `51` | `Potato___Bacterial_soft_rot` | Potato | Marked (Diseased) | 766 | 191 | 957 |
| `52` | `Potato___Bacterial_wilt` | Potato | Marked (Diseased) | 540 | 134 | 674 |
| `53` | `Potato___Black_scurf` | Potato | Marked (Diseased) | 40 | 9 | 49 |
| `54` | `Potato___Blackleg` | Potato | Marked (Diseased) | 48 | 12 | 60 |
| `55` | `Potato___Blackspot_bruising` | Potato | Marked (Diseased) | 616 | 154 | 770 |
| `56` | `Potato___Common_scab` | Potato | Marked (Diseased) | 48 | 12 | 60 |
| `57` | `Potato___Dry_rot` | Potato | Marked (Diseased) | 1,084 | 271 | 1,355 |
| `58` | `Potato___Early_blight` | Potato | Marked (Diseased) | 1,939 | 485 | 2,424 |
| `59` | `Potato___Fungal_disease` | Potato | Marked (Diseased) | 599 | 149 | 748 |
| `60` | `Potato___Late_blight` | Potato | Marked (Diseased) | 2,253 | 563 | 2,816 |
| `61` | `Potato___Leaf_roll_virus` | Potato | Marked (Diseased) | 316 | 78 | 394 |
| `62` | `Potato___Mosaic_virus` | Potato | Marked (Diseased) | 426 | 106 | 532 |
| `63` | `Potato___Nematode` | Potato | Marked (Diseased) | 55 | 13 | 68 |
| `64` | `Potato___Pest_damage` | Potato | Marked (Diseased) | 489 | 122 | 611 |
| `65` | `Potato___Pink_rot` | Potato | Marked (Diseased) | 46 | 11 | 57 |
| `66` | `Potato___Potato_virus_X` | Potato | Marked (Diseased) | 310 | 77 | 387 |
| `67` | `Potato___Potato_virus_Y` | Potato | Marked (Diseased) | 312 | 77 | 389 |
| `68` | `Potato___healthy` | Potato | Unmarked (Healthy) | 2,951 | 737 | 3,688 |
| `69` | `Rice___Bacterial_leaf_blight` | Rice | Marked (Diseased) | 1,462 | 365 | 1,827 |
| `70` | `Rice___Bacterial_leaf_streak` | Rice | Marked (Diseased) | 304 | 76 | 380 |
| `71` | `Rice___Bacterial_panicle_blight` | Rice | Marked (Diseased) | 270 | 67 | 337 |
| `72` | `Rice___Brown_spot` | Rice | Marked (Diseased) | 1,770 | 443 | 2,213 |
| `73` | `Rice___Dead_heart` | Rice | Marked (Diseased) | 1,154 | 288 | 1,442 |
| `74` | `Rice___Downy_mildew` | Rice | Marked (Diseased) | 496 | 124 | 620 |
| `75` | `Rice___Hispa` | Rice | Marked (Diseased) | 1,276 | 318 | 1,594 |
| `76` | `Rice___Leaf_blast` | Rice | Marked (Diseased) | 2,166 | 541 | 2,707 |
| `77` | `Rice___Leaf_smut` | Rice | Marked (Diseased) | 44 | 12 | 56 |
| `78` | `Rice___Tungro` | Rice | Marked (Diseased) | 1,917 | 479 | 2,396 |
| `79` | `Rice___healthy` | Rice | Unmarked (Healthy) | 1,412 | 352 | 1,764 |
| `80` | `Soybean___Bacterial_blight` | Soybean | Marked (Diseased) | 261 | 64 | 325 |
| `81` | `Soybean___Brown_spot` | Soybean | Marked (Diseased) | 443 | 109 | 552 |
| `82` | `Soybean___Caterpillar` | Soybean | Marked (Diseased) | 466 | 116 | 582 |
| `83` | `Soybean___Cercospora_leaf_blight` | Soybean | Marked (Diseased) | 80 | 19 | 99 |
| `84` | `Soybean___Dry_leaf` | Soybean | Marked (Diseased) | 184 | 46 | 230 |
| `85` | `Soybean___Frogeye_leaf_spot` | Soybean | Marked (Diseased) | 136 | 33 | 169 |
| `86` | `Soybean___Mosaic_virus` | Soybean | Marked (Diseased) | 566 | 141 | 707 |
| `87` | `Soybean___Rust` | Soybean | Marked (Diseased) | 762 | 189 | 951 |
| `88` | `Soybean___Sudden_death_syndrome` | Soybean | Marked (Diseased) | 84 | 21 | 105 |
| `89` | `Soybean___Vein_necrosis` | Soybean | Marked (Diseased) | 111 | 27 | 138 |
| `90` | `Soybean___healthy` | Soybean | Unmarked (Healthy) | 2,381 | 593 | 2,974 |
| `91` | `Sugarcane___Banded_chlorosis` | Sugarcane | Marked (Diseased) | 754 | 188 | 942 |
| `92` | `Sugarcane___Brown_spot` | Sugarcane | Marked (Diseased) | 1,378 | 344 | 1,722 |
| `93` | `Sugarcane___Dried_leaf` | Sugarcane | Marked (Diseased) | 275 | 68 | 343 |
| `94` | `Sugarcane___Grassy_shoot` | Sugarcane | Marked (Diseased) | 277 | 69 | 346 |
| `95` | `Sugarcane___Mosaic` | Sugarcane | Marked (Diseased) | 1,204 | 297 | 1,501 |
| `96` | `Sugarcane___Pokkah_boeng` | Sugarcane | Marked (Diseased) | 238 | 59 | 297 |
| `97` | `Sugarcane___Red_rot` | Sugarcane | Marked (Diseased) | 829 | 207 | 1,036 |
| `98` | `Sugarcane___Rust` | Sugarcane | Marked (Diseased) | 1,027 | 248 | 1,275 |
| `99` | `Sugarcane___Sett_rot` | Sugarcane | Marked (Diseased) | 522 | 130 | 652 |
| `100` | `Sugarcane___Smut` | Sugarcane | Marked (Diseased) | 253 | 63 | 316 |
| `101` | `Sugarcane___Yellow_leaf` | Sugarcane | Marked (Diseased) | 1,757 | 436 | 2,193 |
| `102` | `Sugarcane___healthy` | Sugarcane | Unmarked (Healthy) | 1,148 | 280 | 1,428 |
| `103` | `Tomato___Bacterial_spot` | Tomato | Marked (Diseased) | 1,702 | 425 | 2,127 |
| `104` | `Tomato___Early_blight` | Tomato | Marked (Diseased) | 1,920 | 480 | 2,400 |
| `105` | `Tomato___Late_blight` | Tomato | Marked (Diseased) | 1,844 | 460 | 2,304 |
| `106` | `Tomato___Leaf_Mold` | Tomato | Marked (Diseased) | 1,882 | 470 | 2,352 |
| `107` | `Tomato___Septoria_leaf_spot` | Tomato | Marked (Diseased) | 1,745 | 436 | 2,181 |
| `108` | `Tomato___Spider_mites Two-spotted_spider_mite` | Tomato | Marked (Diseased) | 1,741 | 435 | 2,176 |
| `109` | `Tomato___Target_Spot` | Tomato | Marked (Diseased) | 1,827 | 457 | 2,284 |
| `110` | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | Tomato | Marked (Diseased) | 1,961 | 490 | 2,451 |
| `111` | `Tomato___Tomato_mosaic_virus` | Tomato | Marked (Diseased) | 1,790 | 448 | 2,238 |
| `112` | `Tomato___healthy` | Tomato | Unmarked (Healthy) | 1,923 | 478 | 2,401 |
| `113` | `Turmeric___Aphid` | Turmeric | Marked (Diseased) | 678 | 169 | 847 |
| `114` | `Turmeric___Dry_leaf` | Turmeric | Marked (Diseased) | 975 | 243 | 1,218 |
| `115` | `Turmeric___Leaf_blotch_mild` | Turmeric | Marked (Diseased) | 557 | 139 | 696 |
| `116` | `Turmeric___Leaf_blotch_severe` | Turmeric | Marked (Diseased) | 558 | 139 | 697 |
| `117` | `Turmeric___Leaf_spot_mild` | Turmeric | Marked (Diseased) | 368 | 91 | 459 |
| `118` | `Turmeric___Leaf_spot_severe` | Turmeric | Marked (Diseased) | 368 | 92 | 460 |
| `119` | `Turmeric___Rhizome_healthy` | Turmeric | Unmarked (Healthy) | 677 | 169 | 846 |
| `120` | `Turmeric___Rhizome_rot_early` | Turmeric | Marked (Diseased) | 509 | 127 | 636 |
| `121` | `Turmeric___Rhizome_rot_severe` | Turmeric | Marked (Diseased) | 509 | 128 | 637 |
| `122` | `Turmeric___healthy` | Turmeric | Unmarked (Healthy) | 1,760 | 440 | 2,200 |
| `123` | `Wheat___Aphid` | Wheat | Marked (Diseased) | 155 | 39 | 194 |
| `124` | `Wheat___Black_rust` | Wheat | Marked (Diseased) | 128 | 32 | 160 |
| `125` | `Wheat___Brown_rust` | Wheat | Marked (Diseased) | 84 | 21 | 105 |
| `126` | `Wheat___Flag_smut` | Wheat | Marked (Diseased) | 84 | 21 | 105 |
| `127` | `Wheat___Leaf_blight` | Wheat | Marked (Diseased) | 140 | 36 | 176 |
| `128` | `Wheat___Mite` | Wheat | Marked (Diseased) | 153 | 39 | 192 |
| `129` | `Wheat___Powdery_mildew` | Wheat | Marked (Diseased) | 168 | 43 | 211 |
| `130` | `Wheat___Scab` | Wheat | Marked (Diseased) | 83 | 21 | 104 |
| `131` | `Wheat___Stem_fly` | Wheat | Marked (Diseased) | 137 | 35 | 172 |
| `132` | `Wheat___Yellow_rust` | Wheat | Marked (Diseased) | 73 | 19 | 92 |
| `133` | `Wheat___healthy` | Wheat | Unmarked (Healthy) | 256 | 65 | 321 |

---

## 3. Official Verified Dataset Citations & Academic References

All images and agronomic telemetry have been unified from certified agricultural and scientific repositories with strict 80/20 train/valid splits, deduplication, and zero data leakage:

### A. Field Crop Pathology Imagery (11 Crops | 134 Classes | 166,630 Images)

| # | Crop | Classes | Total Images | Primary Reference & Dataset Name | Repository, DOI & Access Link |
| :- | :--- | :---: | :---: | :--- | :--- |
| 1 | **Potato** | **18** | 16,039 | *PotatoCare: Deep learning based potato disease dataset* + *Potato Leaf Disease Dataset* + *PlantVillage* | [Mendeley Data (10.17632/tycgft54b4.1)](https://data.mendeley.com/datasets/tycgft54b4/1) & [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset) |
| 2 | **Cotton** | **15** | 9,778 | *SAR-CLD-2024: A Comprehensive Dataset for Cotton Leaf Disease Detection* + *Cotton Leaf Image Dataset for Disease Classification* | [Mendeley Data (10.17632/c763g9pvh3.1)](https://data.mendeley.com/datasets/c763g9pvh3/1) & [Mendeley Data](https://data.mendeley.com) |
| 3 | **Orange** | **13** | 8,947 | *Multi-format open-source sweet orange leaf dataset for disease detection, classification, and analysis* + *PlantVillage* | [Mendeley Data (10.17632/f7cr74mwpj.1)](https://data.mendeley.com/datasets/f7cr74mwpj/1) |
| 4 | **Banana** | **12** | 19,565 | *Banana Leaf Disease Dataset* + *Banana Leaf Disease Dataset v4* | [Mendeley Data (10.17632/5nfjzntwd8.1)](https://data.mendeley.com/datasets/5nfjzntwd8/1) & [Kaggle](https://www.kaggle.com/datasets/rayhanarlistya/banana-leaf-disease-dataset-v4) |
| 5 | **Sugarcane** | **12** | 12,051 | *Sugarcane Leaf Disease Multi-Class Dataset* | [Kaggle](https://www.kaggle.com/datasets/nirmalsankalana/sugarcane-leaf-disease-dataset) |
| 6 | **Corn (maize)** | **11** | 44,640 | *Maize Crop Disease (Leaf)* + *Seasonal Corn Leaf Disease* + *Maize Lethal Necrosis (MLN)* | [Mendeley Data (10.17632/b35nhbp8x5.1)](https://data.mendeley.com/datasets/b35nhbp8x5/1) & [Zenodo (10.5281/zenodo.11470438)](https://zenodo.org/records/11470438) |
| 7 | **Rice** | **11** | 15,336 | *Paddy Doctor: A Large-Scale Benchmark Dataset for Paddy Crop Disease Classification* + *Rice Leaf Diseases* | [Kaggle (Paddy Doctor)](https://www.kaggle.com/competitions/paddy-disease-classification) & [Kaggle (vbookshelf)](https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases) |
| 8 | **Soybean** | **11** | 6,832 | *Multi-Class Soybean Leaf Disease Dataset Healthy and Diseased* + *MH-SoyaHealthVision: An Indian UAV and Leaf Image Dataset* | [Mendeley (10.17632/6fhphxg297.2)](https://data.mendeley.com/datasets/6fhphxg297/2) & [Mendeley (10.17632/hkbgh5s3b7.1)](https://data.mendeley.com/datasets/hkbgh5s3b7/1) |
| 9 | **Wheat** | **11** | 1,832 | *20k Multi-Class Crop Disease Dataset* (Jawad Ali) | [Kaggle](https://www.kaggle.com/datasets/jawadali1045/20k-multi-class-crop-disease-images) |
| 10 | **Tomato** | **10** | 22,914 | *PlantVillage Benchmark Repository* (Mohanty, Hughes, Salathé) | [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset) & [Kaggle](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset) |
| 11 | **Turmeric** | **10** | 8,696 | *Turmeric Plant Disease Dataset* (Necrotic lesion severity staging) | [Mendeley Data](https://data.mendeley.com) & [Kaggle](https://www.kaggle.com/datasets/hiteshpatil95/turmeric-datasets-for-cnn-model-training-and-test) |

---

### B. Tabular Agro-Meteorological & Economic Datasets

| # | Dataset | Source / Authority | Volume & Description | Access Link |
| :- | :--- | :--- | :--- | :--- |
| 1 | **Crop Yield Prediction Dataset** | UN Food and Agriculture Organization (FAO) / Rikin Patel | 28,242 rows across countries including India (Area, Item, Year, Yield hg/ha, rainfall, temperature, pesticides) | [Kaggle](https://www.kaggle.com/datasets/patelris/crop-yield-prediction-dataset) |
| 2 | **Crop Production in India** | Ministry of Agriculture & Farmers Welfare (MoA&FW) / Abhinand | 246,091 district-level agricultural production records across India (State, District, Crop, Year, Season, Area, Production) | [Kaggle](https://www.kaggle.com/datasets/abhinand05/crop-production-in-india) |
| 3 | **Historical Indian Crop Yield Dataset** | Directorate of Economics and Statistics (DES) | 19,689 records (`crop_yield.xlsx`, State, Season, Area, Production, Annual_Rainfall, Fertilizer, Pesticide, Yield) | Verified Academic Archive |
| 4 | **APMC Market Telemetry** | Maharashtra State Agricultural Marketing Board (MSAMB) / Agmarknet | Daily modal price, minimum, maximum, and arrivals across 36 districts for 11 target crops | [Agmarknet](https://agmarknet.gov.in) |
| 5 | **Microclimate Telemetry** | Open-Meteo European Centre for Medium-Range Weather Forecasts (ECMWF) | Hourly & daily temperature, relative humidity, precipitation, and 10m wind velocity across Maharashtra GPS coordinates | [Open-Meteo](https://open-meteo.com) |

---

## 4. Multimodal Model Convergence & Training Performance (80 Epochs)

The multi-modal architecture (`MultiModalAeroCropNet`) was trained across the full 166,630 image pathology dataset and agro-meteorological tabular vectors for **80 complete epochs**:

| Performance Dimension | Metric / Benchmark | Operational Relevance |
| :--- | :--- | :--- |
| **Disease Classification Accuracy** | **`95.39%` (Validation)** | High-confidence diagnosis across 134 pathology and healthy leaf states |
| **Validation Macro Precision** | **`92.8%`** | Extremely low false positive rate on severe quarantine diseases |
| **Validation Macro F1-Score** | **`91.7%`** | Robust balance across class imbalances in regional datasets |
| **Multi-Task Objective Loss** | **`1.534`** | $\alpha=1.0$ (CrossEntropy 0.94) + $\beta=0.20$ (SmoothL1 Yield 2.98) |
| **Yield Forecasting Error** | **`8.2325 t/ha` RMSE** (MAE `3.3867 t/ha`) | Continuous harvest volume regression conditioned on leaf health & weather |
| **Standardized Harvest Metric** | **`Quintal / Acre`** | Indian standard unit: $\text{Yield}_{(\text{Quintal/Acre})} = \text{Yield}_{(t/\text{ha})} \times 4.047$ |
| **Model Footprint** | **`11,285,191` Parameters** ($45.1\text{ MB}$) | Lightweight for edge and high-concurrency cloud serving (`model/aerocrop_weights.pth`) |
| **Training Infrastructure** | **80 Epochs in 306.2 min** | NVIDIA GeForce RTX 3050 6GB Laptop GPU with PyTorch 2.5 CUDA AMP FP16 |
| **Full Historical Logs** | `model/training_log.csv` | Complete epoch-by-epoch audit trail from Epoch 1 through Epoch 80 |
