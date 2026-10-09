# NoteGuard AI — Dataset Forensic Audit

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Summary of Datasets on Disk

A comprehensive filesystem scan of `d:\PROJECTS\notegurd\NoteguardAI\dataset` revealed multiple disjoint dataset directories:

```
dataset/
├── data/                 # Raw ingested notes (2,905 images)
│   ├── fake/             # 10 (250), 20 (250), 50 (250), 200 (250), 500 (250), 2000 (145)  [fake/100 is missing]
│   └── real/             # 10 (250), 20 (256), 50 (150), 100 (250), 200 (250), 500 (144), 2000 (250)
├── cleaned/
│   ├── data/             # Cleaned notes (fake & real across all denominations)
│   └── features/         # Regional security feature crops (10 to 2000)
├── Features/             # Legacy feature crops
└── split/                # Active partition used by TrainingConfig (CRITICALLY CORRUPTED)
    ├── train/            # 2,495 images
    ├── val/              # 313 images
    └── test/             # 29 images
```

---

## 2. Active Split Forensic Breakdown (`dataset/split`)

The filesystem scan performed in Phase 3 revealed catastrophic class imbalances and missing classes in `dataset/split`:

| Class Name | Train Count | Validation Count | Test Count | Total In Split | Expected (from `dataset/data`) | Split Assessment |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `fake_10` | 255 | 43 | 2 | 300 | 250 | Ingested with slight duplicate expansion |
| `fake_20` | 207 | 44 | 4 | 255 | 250 | Normally distributed |
| `fake_50` | 205 | 17 | 1 | 223 | 250 | Severe validation & test starvation |
| `fake_100` | 251 | 55 | 2 | 308 | 250 (in cleaned) | Ingested from cleaned set |
| `fake_200` | 81 | 40 | 4 | 125 | 250 | Underrepresented in train (81 vs 200) |
| `fake_500` | 263 | 14 | 8 | 285 | 250 | Heavily represented in train |
| `fake_2000` | 163 | 1 | 1 | 165 | 145 | Only 1 validation & 1 test sample! |
| `real_10` | **2** | **58** | **0** | 60 | 250 | **CRITICAL ANOMALY: Train missing 97% of data (only 2 images in train, 58 dumped in val!)** |
| `real_20` | 207 | **0** | **0** | 207 | 256 | **CRITICAL DEFECT: 0 validation and 0 test images!** |
| `real_50` | **5** | **0** | **0** | 5 | 150 | **CATASTROPHIC FAILURE: 145 images missing; 0 in val/test, only 5 in train!** |
| `real_100` | 239 | 37 | **0** | 276 | 250 | 0 test images |
| `real_200` | 200 | **0** | **0** | 200 | 250 | **CRITICAL DEFECT: 0 validation and 0 test images!** |
| `real_500` | 254 | 2 | 6 | 262 | 144 | Expanded in train; starved in val (only 2 samples) |
| `real_2000` | 163 | 2 | 1 | 166 | 250 | Starved in val/test (2 val, 1 test) |
| **TOTAL** | **2,495** | **313** | **29** | **2,837** | **2,905** | **Severe split corruption** |

---

## 3. Root Cause Analysis of Real-World Denomination Confusion

1. **`real_50` Extinction**: With only **5 training samples** in `dataset/split/train`, the CNN had zero statistical power to learn ₹50 features. It consistently collapsed to the dominant feature cluster, which is `real_500` (254 training samples).
2. **`real_10` Partition Inversion**: `real_10` had only **2 training samples** because 58 images were accidentally routed into `val/real_10`.
3. **Zero Validation Feedback for ₹20 and ₹200**: Because `val/real_20` and `val/real_200` had **0 images**, validation loss and accuracy during training completely ignored ₹20 and ₹200 performance. A model that completely misclassified ₹20 as ₹500 still reported misleadingly high validation accuracy.
4. **Test Set Depletion**: The entire test partition contained only **29 images**, with 0 samples for `real_10`, `real_20`, `real_50`, `real_100`, and `real_200`. Any previous report claiming $>96\%$ test accuracy was evaluating an unrepresentative 29-sample subset.

---

## 4. Image Quality & Physical Statistics (by Class)

| Class | Total Count | Mean Width | Mean Height | Aspect Ratio | Mean Brightness | Mean Sharpness (Laplacian Var) | Primary Format |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `fake_10` | 300 | 193.6px | 216.7px | 1.04 | 151.5 | 7,157.9 | JPEG (100%) |
| `fake_20` | 255 | 188.0px | 243.0px | 0.93 | 148.6 | 9,402.8 | JPEG (100%) |
| `fake_50` | 223 | 186.0px | 245.4px | 0.91 | 154.6 | 8,571.8 | JPEG (100%) |
| `fake_100` | 308 | 185.1px | 272.3px | 0.82 | 147.2 | 9,947.8 | JPEG (99%) |
| `fake_200` | 125 | 166.0px | 202.0px | 0.97 | 153.4 | 7,967.6 | JPEG (100%) |
| `fake_500` | 285 | 480.5px | 484.2px | 1.02 | 133.4 | 1,106.3 | JPEG (100%) |
| `fake_2000` | 165 | 709.6px | 348.1px | 2.03 | 161.9 | 1,110.0 | PNG (87%) |
| `real_10` | 60 | 682.0px | 543.0px | 1.28 | 112.3 | 840.4 | JPEG (100%) |
| `real_20` | 207 | 603.7px | 516.3px | 1.20 | 109.9 | 1,003.7 | JPEG (100%) |
| `real_50` | 5 | 508.0px | 487.2px | 1.14 | 130.3 | 558.8 | JPEG (100%) |
| `real_100` | 276 | 3358.4px | 3546.7px | 1.13 | 154.1 | 939.3 | JPEG (100%) |
| `real_200` | 200 | 2400.9px | 2718.6px | 1.10 | 149.8 | 768.5 | JPEG (100%) |
| `real_500` | 262 | 872.3px | 711.4px | 1.71 | 157.1 | 1,125.7 | JPEG (100%) |
| `real_2000` | 166 | 735.6px | 553.8px | 1.42 | 136.1 | 1,016.4 | JPEG (100%) |

### Critical Observations on Data Quality:
- **Resolution Discrepancy**: Fake notes (`fake_10`, `fake_20`, `fake_50`, `fake_100`, `fake_200`) are tiny low-resolution crops ($166\text{px} - 193\text{px}$), whereas real notes (`real_100`, `real_200`) are massive high-resolution camera photos ($2400\text{px} - 3500\text{px}$).
- **Artificial Sharpness Artifacts**: The fake notes exhibit Laplacian variance $>7,000$ because they are tight digital crops with high contrast edges, whereas real notes exhibit realistic camera blur ($500 - 1,100$). The CNN inadvertently learned to use image resolution and sharpness artifacts as spurious shortcuts for authenticity!

---

## 5. Data Leakage Verification
- **Train vs Validation SHA-256 Overlap**: 0 exact duplicate hashes.
- **Train vs Test SHA-256 Overlap**: 0 exact duplicate hashes.
- **Validation vs Test SHA-256 Overlap**: 0 exact duplicate hashes.
- **Near-Duplicate Status**: Many images in `real_100` and `real_200` are sequential phone bursts of the same physical note taken from slightly varying angles.
