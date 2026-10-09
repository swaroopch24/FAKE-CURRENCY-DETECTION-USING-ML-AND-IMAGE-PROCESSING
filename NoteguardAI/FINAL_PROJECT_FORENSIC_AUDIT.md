# NoteGuard AI — Final Master Forensic Audit Report

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer + AI System Architect + Backend Engineer  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Executive Summary

A comprehensive read-only forensic audit was executed across all 30 phases of the **NoteGuard AI** currency verification project. 

The audit successfully uncovered the **three fundamental root causes** behind the real-world model failures (e.g. ₹20 $\rightarrow$ ₹500, fake ₹20 $\rightarrow$ real ₹500, inconsistent predictions):

1. **Class Mapping Offset Bug (Software Defect)**:
   - A critical misalignment between default Keras alphabetical directory scanning and `config.py` ordering caused index 12 (`real_50`) to be translated directly to `CLASS_NAMES[12]` (`real_500`), and index 5 (`fake_50`) to be translated to `fake_500` during inference!
2. **Catastrophic Dataset Split Imbalance & Depletion (Data Defect)**:
   - In `dataset/split/train`, `real_50` had only **5 images** and `real_10` had only **2 images**, while `real_500` had 254 images.
   - `dataset/split/val` was completely missing `real_20`, `real_50`, and `real_200`, and `dataset/split/test` contained only 29 total images with 0 real note samples for 5 denominations. Validation accuracy was artificially inflated by an unrepresentative $81\%$ fake-note distribution.
3. **Single 14-Class Output Entanglement (Architectural Defect)**:
   - The 14-class single softmax head forces the model to learn denomination and authenticity simultaneously, creating severe feature interference and low softmax activations on ambiguous notes.

The good news:
- The master dataset in `dataset/data` contains **2,905 raw images** (plus cleaned sets) with sufficient volume to build a high-accuracy, balanced dataset.
- The backend architecture, PostgreSQL database, authentication, RBAC, rate-limiting, and React 18 frontend SPA are robust and operational.

---

## 2. Comprehensive System Health Scorecard

```
┌──────────────────────────────────────┬─────────┬────────────────────────────────┐
│ SUBSYSTEM                            │ STATUS  │ HEALTH / DEFECT SUMMARY        │
├──────────────────────────────────────┼─────────┼────────────────────────────────┤
│ 1. Backend API & Core Middleware     │ HEALTHY │ FastAPI, JWT, Rate Limiting ok │
│ 2. PostgreSQL Relational Database    │ HEALTHY │ 12 tables mapped with Alembic  │
│ 3. React 18 Frontend SPA             │ HEALTHY │ Clean Vite build, 0 TS errors  │
│ 4. Request Validation & MIME Checks  │ HEALTHY │ Size, magic bytes, aspect ok   │
│ 5. Active Preprocessing Parity       │ HEALTHY │ Normalization matches model    │
│ 6. Decision Engine & Thresholds      │ HEALTHY │ 0.80 cutoff justified          │
│ 7. Class Index Mapping               │ DEFECT  │ Alphabetical vs config offset  │
│ 8. Active Dataset Partition (split/) │ DEFECT  │ Missing classes & unbalance    │
│ 9. Single 14-Class CNN Architecture  │ LIMITED │ Denom/Auth entanglement       │
│ 10. Real-World Model Generalization  │ POOR    │ Biased towards ₹500 & sharp fks│
└──────────────────────────────────────┴─────────┴────────────────────────────────┘
```

---

## 3. Critical, Medium, and Minor Problem Matrix

### Critical Problems (Blockers for Retraining & Deployment):
1. **Class Mapping Bug**: `inference.py` decodes model output indices using `training_config.CLASS_NAMES`, which does not match Keras alphabetical folder order unless explicitly fixed.
2. **`dataset/split` Corruption**: `train/real_50` (5 images), `train/real_10` (2 images), `val` missing ₹20/₹50/₹200, `test` has only 29 images.
3. **Uncommitted Model Weights**: Binary checkpoints were gitignored; model retraining on a clean dataset is required.

### Medium Problems:
1. **Nearest Neighbor Resizing**: Degrades fine line security guilloches and watermarks; should be upgraded to Bicubic / Area interpolation.
2. **Open-World / Non-Currency Ingestion**: Closed-world 14-class softmax assigns arbitrary high probabilities to non-currency items (keyboards, faces) without visual aspect ratio bounding checks.
3. **Hardcoded Staging Paths**: Multiple diagnostic scripts reference non-existent `C:\PROJECTS\fakecurrency`.

### Minor Problems:
1. **Residual `"use client";` Directives**: Leftover Next.js headers in React component files.
2. **Missing `httpx` / `pytest` in venv**: Need test dependencies in Python environment for local automated test runs.

---

## 4. Recommended V2 Architecture & Multi-Task Design

To achieve true banking-grade accuracy, the V2 architecture should adopt a **Two-Head Multi-Task Network**:

```
                  [Input Banknote Image: 224 x 224 x 3]
                                   │
                                   ▼
             [MobileNetV2 / EfficientNetB0 Feature Extractor]
                                   │
                                   ▼
                       [GlobalAveragePooling2D]
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
       [Authenticity Head]                  [Denomination Head]
       Dense(128, relu)                     Dense(128, relu)
       Dropout(0.4)                         Dropout(0.4)
       Dense(1, sigmoid)                    Dense(7, softmax)
       Loss: Binary Crossentropy            Loss: Categorical Crossentropy
       Output: P(Authentic)                 Output: P(₹10, ₹20, ..., ₹2000)
```

### Benefits of Multi-Task Architecture:
1. **Decoupled Learning**: Authenticity features (security thread, latent image, microprint sharpness) are learned independently of denomination features (color palette, numerical numerals, architectural monuments).
2. **Clean Output Probabilities**: Eliminates aggregate score summation artifacts and prevents ambiguous authenticity from dragging down denomination confidence.
3. **Zero Class Mapping Confusion**: Denomination output is always a 7-class vector ($[0..6]$) and authenticity is a binary sigmoid score ($[0..1]$).

---

## 5. Recommended Experimental Roadmap (Ordered by Priority)

```
                       RECOMMENDED V2 ROADMAP
                                 │
                                 ▼
                     PHASE A: DATASET CURATION
                     Rebuild dataset/split from 
                     dataset/data using 70/15/15
                                 │
                                 ▼
                     PHASE B: CLASS MAPPING FIX
                     Lock explicit class dicts
                     in training & inference
                                 │
                                 ▼
                     PHASE C: BASELINE RETRAINING
                     Train balanced 14-class MobileNetV2
                     Measure baseline on full Test set
                                 │
                                 ▼
                     PHASE D: MULTI-TASK ARCHITECTURE
                     Train Two-Head Network (Auth + Denom)
                     on GPU workstation
                                 │
                                 ▼
                     PHASE E: REAL-WORLD BENCHMARK
                     Evaluate on NGRW-100 unseen note set
```

---

## 6. Conclusion & Next Steps

The read-only forensic audit is complete. All 16 audit documents, reports, and dataset manifests are written to disk.

We have identified the root causes of previous model errors. We are ready to proceed to Phase A (Dataset Curation & Balance) and Phase B (V2 Multi-Task Training) upon your explicit review and approval.
