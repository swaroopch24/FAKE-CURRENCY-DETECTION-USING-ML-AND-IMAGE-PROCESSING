# NoteGuard AI — Class Mapping Forensic Audit

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. The Class Mapping Discrepancy

A critical defect was uncovered when comparing how class indices were generated during training versus how they were interpreted during inference in `backend/src/modules/ai_engine/`.

### Source 1: Standard Keras Alphabetical Order (`ImageDataGenerator.flow_from_directory`)
When `flow_from_directory` is called on standard directory folders without explicitly passing the `classes` parameter, Keras sorts folder names **alphabetically** (ASCII sorting).

### Source 2: `TrainingConfig.CLASS_NAMES` (`backend/src/modules/ai_engine/training/config.py`)
In `config.py`, classes were listed manually in numerical order of denominations (`fake_10`, `fake_20`, `fake_50`, `fake_100`, ...).

---

## 2. Side-by-Side Index Mapping Comparison

| Index | Keras Default Alphabetical Order | `TrainingConfig.CLASS_NAMES` Order | Index Alignment Status | Inference Consequence |
| :---: | :--- | :--- | :---: | :--- |
| **0** | `fake_10` | `fake_10` | **MATCH** | Correct |
| **1** | `fake_100` | `fake_20` | **MISMATCH** | Model predicting ₹100 is decoded as **₹20**! |
| **2** | `fake_20` | `fake_50` | **MISMATCH** | Model predicting ₹20 is decoded as **₹50**! |
| **3** | `fake_200` | `fake_100` | **MISMATCH** | Model predicting ₹200 is decoded as **₹100**! |
| **4** | `fake_2000` | `fake_200` | **MISMATCH** | Model predicting ₹2000 is decoded as **₹200**! |
| **5** | `fake_50` | `fake_500` | **MISMATCH** | Model predicting ₹50 is decoded as **₹500**! |
| **6** | `fake_500` | `fake_2000` | **MISMATCH** | Model predicting ₹500 is decoded as **₹2000**! |
| **7** | `real_10` | `real_10` | **MATCH** | Correct |
| **8** | `real_100` | `real_20` | **MISMATCH** | Model predicting ₹100 is decoded as **₹20**! |
| **9** | `real_20` | `real_50` | **MISMATCH** | Model predicting ₹20 is decoded as **₹50**! |
| **10** | `real_200` | `real_100` | **MISMATCH** | Model predicting ₹200 is decoded as **₹100**! |
| **11** | `real_2000` | `real_200` | **MISMATCH** | Model predicting ₹2000 is decoded as **₹200**! |
| **12** | `real_50` | `real_500` | **MISMATCH** | Model predicting ₹50 is decoded as **₹500**! |
| **13** | `real_500` | `real_2000` | **MISMATCH** | Model predicting ₹500 is decoded as **₹2000**! |

---

## 3. The ₹500 Confusion Mechanism Explained

Look at indices 5 and 12 in the table above:
1. When the CNN evaluated a note and its highest feature match was `real_50` (index 12 in alphabetical order), the backend inference code performed:
   ```python
   # backend/src/modules/ai_engine/inference.py line 38
   pred_label = training_config.CLASS_NAMES[max_idx]  # max_idx is 12
   # training_config.CLASS_NAMES[12] is "real_500"!
   ```
   **The backend literally converted every `real_50` prediction directly into `real_500`!**
2. Similarly, index 5 (`fake_50` in alphabetical order) mapped to `CLASS_NAMES[5]`, which is **`fake_500`**!
3. Index 2 (`fake_20` in alphabetical order) mapped to `CLASS_NAMES[2]`, which is **`fake_50`**!
4. Index 9 (`real_20` in alphabetical order) mapped to `CLASS_NAMES[9]`, which is **`real_50`**!

---

## 4. Aggregate Authenticity Inversion Risk

Because all `fake_*` classes are at indices 0–6 and all `real_*` classes are at indices 7–13 in **both** ordering schemes:
- Summing `p_real = sum(probabilities[7:14])` and `p_fake = sum(probabilities[0:7])` preserved binary authenticity classification (REAL vs FAKE).
- However, the **denomination string extraction** (`parts[1]`) was completely corrupted for 10 out of 14 classes!

---

## 5. Required Fix for V2 Training Pipeline

1. In all data generators (`trainer.py`, `evaluate.py`, `pipeline.py`), `classes=training_config.CLASS_NAMES` must be explicitly declared so that directory reading order is deterministic and identical across training, evaluation, inference, and decision middleware.
2. In training checkpoints, the exact class dictionary mapping `{name: index}` must be embedded directly into model metadata or saved alongside the weights in `metadata.json`.
