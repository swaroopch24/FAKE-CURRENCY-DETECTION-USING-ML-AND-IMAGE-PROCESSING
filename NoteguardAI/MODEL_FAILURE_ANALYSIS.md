# NoteGuard AI — Model Failure & Error Analysis

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Primary Model Failure Taxonomy

Forensic analysis of misclassified images reveals 6 distinct failure categories:

```
                      MODEL FAILURES TAXONOMY
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
1. Class Index          2. Training Data            3. Resolution
   Mapping Offset          Starvation Imbalance        Artifact Shortcut
   (Real 50 -> 500)        (Real 50: 5 imgs)           (Fake notes 190px)
     │                           │                           │
     ▼                           ▼                           ▼
4. Color Hue            5. Lack of Spatial          6. Out of Distribution
   Degradation             Segmentation                Open-World Leak
   (Dim light ₹20)         (Cluttered tables)          (Keyboards / Faces)
```

---

## 2. Detailed Root Cause Breakdown

### Failure Type A: Class Index Mapping Bug (Software Defect)
- **Manifestation**: True ₹50 notes consistently classified as ₹500. True ₹2000 notes classified as ₹200. True ₹200 notes classified as ₹100.
- **Root Cause**: Index discrepancy between default Keras alphabetical directory scanning and manual `config.py` ordering.
- **Fix**: Explicitly define `classes=training_config.CLASS_NAMES` across all training and evaluation generators.

### Failure Type B: Severe Training Dataset Imbalance (Dataset Defect)
- **Manifestation**: The model exhibits high confidence on ₹500 and near-zero recall on genuine ₹50 notes.
- **Root Cause**: `dataset/split/train` contained only 5 images of `real_50` and 2 images of `real_10`, while containing 254 images of `real_500`.
- **Fix**: Re-split and balance dataset from master `dataset/data` repository using stratified 70/15/15 sampling.

### Failure Type C: Low-Resolution Digital Shortcut Bias (Feature Learning Defect)
- **Manifestation**: Fake notes in the dataset are small cropped thumbnails ($166\text{px} - 193\text{px}$) with artificial edge sharpness, whereas real notes are full-size camera captures ($2400\text{px} - 3500\text{px}$).
- **Root Cause**: MobileNetV2 learned high-frequency pixel sharpening as a shortcut for counterfeit classification.
- **Fix**: Apply image blur and downsampling augmentation to real notes; standardize all inputs through bicubic antialiasing.

### Failure Type D: Background Clutter & Non-Currency Ingestion (System Vulnerability)
- **Manifestation**: Photos taken on wooden tables or textured cloths result in misclassification because background features overpower the banknote print.
- **Fix**: Introduce contour-based bounding-box extraction in preprocessing and train with background cutout augmentation.
