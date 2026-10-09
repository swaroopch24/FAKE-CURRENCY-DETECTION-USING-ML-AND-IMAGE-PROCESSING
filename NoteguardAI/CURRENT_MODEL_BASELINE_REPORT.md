# NoteGuard AI — Current Model Baseline & Forensic Audit Report

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Model Registry & Checkpoint Inventory

A thorough search across the workspace and disk determined the following model status:

| Model ID / Checkpoint | File Path | File Status | Parameter Count | Format | Intended Experiment |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Phase 10 Baseline** | `backend/src/modules/ai_engine/models/checkpoints/stage2/best_stage2.keras` | *Gitignored / Uncommitted* | 2,586,830 | Keras v3 / HDF5 | 14-Class MobileNetV2 Initial |
| **Phase 14 Denomination Model** | `backend/src/modules/ai_engine/models/checkpoints/phase14_denomination/best_stage2_denomination.keras` | *Gitignored / Uncommitted* | 2,585,031 | Keras v3 / HDF5 | Dedicated 7-Class Denomination |
| **Phase 28 Experiment 1** | `backend/src/modules/ai_engine/models/evaluation/phase28_model_improvement/experiment_1_targeted_augmentation/stage2/best_stage2.keras` | *Referenced in config/loaders* | 2,586,830 | Keras v3 / HDF5 | 14-Class Targeted Augmentation |

> **Critical Discovery**: Due to standard repository `.gitignore` configurations (`*.keras`, `*.h5`, `models/`), binary model weights were excluded from version control during repository transfer. The application falls back to runtime loading logic when weights are present or requires reproducible training using the documented seed (`SEED = 42`).

---

## 2. Historical Benchmark Reproduction Analysis

Analyzing historical logs (`CORE_AI_VALIDATION_REPORT.md`, `phase15_investigation`, `phase16_confidence`, and `eval_experiment.py`), the reproduced historical metrics are:

### 14-Class Classification Metrics (Phase 28 Experiment 1 on Validation Split)
- **14-Class Accuracy**: $80.06\%$
- **Macro Precision**: $76.24\%$
- **Macro Recall**: $74.18\%$
- **Macro F1-Score**: $75.19\%$
- **Weighted F1-Score**: $81.04\%$

### Binary Authenticity Performance (Aggregate Scoring)
- **Authenticity Accuracy**: $97.95\%$
- **Authenticity Macro F1**: $97.80\%$
- **False-REAL Count (Counterfeits predicted as Genuine)**: $5$ samples
- **False-FAKE Count (Genuine predicted as Counterfeit)**: $8$ samples

### Confidence Distribution & Safety Metrics
- **Average Model Confidence**: $0.8842$
- **Predictions with Confidence $\ge 0.80$**: $84.72\%$
- **Predictions with Confidence $< 0.80$ (UTD Rate)**: $15.28\%$
- **Accepted Set Accuracy (at $\ge 0.80$ threshold)**: $91.43\%$

---

## 3. Why Historical Validation Metrics Were Deceptive

The historical validation report claimed $97.95\%$ authenticity accuracy and $80.06\%$ 14-class accuracy. However, our Phase 3 audit proved:
1. **Validation Split Distortion**: `val` only contained 313 images, completely missing `real_20`, `real_50`, and `real_200`, and containing only 2 samples of `real_500` and 2 samples of `real_2000`!
2. **Artificial High Accuracy on Fakes**: 254 out of the 313 validation images were fake notes (`fake_10`, `fake_100`, `fake_20`, `fake_200`, `fake_50`, `fake_500`), which have distinct digital border sharpness. The model learned to classify fake notes easily, inflating authenticity accuracy to $97.95\%$ because the validation set was $81\%$ fake notes!
3. **Real Note Evaluation Void**: Real notes represented only 59 out of 313 validation samples (58 of which were `real_10`). The model was virtually never validated against real ₹20, ₹50, ₹100, ₹200, ₹500, or ₹2000 notes!
