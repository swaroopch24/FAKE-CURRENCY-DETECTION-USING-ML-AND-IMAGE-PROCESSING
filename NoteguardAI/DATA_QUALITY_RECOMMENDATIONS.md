# NoteGuard AI — Data Quality & Dataset Curation Recommendations

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Actionable Data Curation Categories

To prevent data contamination, all dataset curation actions are classified strictly under three categories:

```
┌─────────────────┬───────────────────────────────────────────────────────────┐
│ CATEGORY        │ CRITERIA & ACTIONS                                        │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **KEEP**        │ Verified authentic / counterfeit banknote captures with   │
│                 │ clear denomination markings, natural lighting, and       │
│                 │ resolutions >= 300x300.                                   │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **REVIEW**      │ Extreme low-resolution crops (< 200px), images with       │
│                 │ heavy specular flash glare, or sequential burst photos    │
│                 │ of identical physical notes.                              │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **REMOVE**      │ Completely unreadable corrupt files, non-banknote         │
│                 │ thumbnails, or duplicated SHA-256 identical hashes.       │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 2. Dataset Reconstruction Blueprint (Rebuilding `dataset/split`)

### Master Source Repository:
The source of truth for raw data is `dataset/data` (2,905 images across denominations) supplemented by `dataset/cleaned/data/fake/100` (which restores missing `fake_100` notes).

### Stratified 70 / 15 / 15 Partition Plan:

| Class | Master Source Total | Target Train (70%) | Target Val (15%) | Target Test (15%) | Curation Action |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `fake_10` | 250 | 175 | 37 | 38 | **KEEP** — Balance with real_10 |
| `fake_20` | 250 | 175 | 37 | 38 | **KEEP** |
| `fake_50` | 250 | 175 | 37 | 38 | **KEEP** |
| `fake_100` | 250 | 175 | 37 | 38 | **RESTORE** from `cleaned/data/fake/100` |
| `fake_200` | 250 | 175 | 37 | 38 | **KEEP** |
| `fake_500` | 250 | 175 | 37 | 38 | **KEEP** |
| `fake_2000` | 145 | 101 | 22 | 22 | **KEEP** (augment to parity) |
| `real_10` | 250 | 175 | 37 | 38 | **RESTORE** from `data/real/10` |
| `real_20` | 256 | 179 | 38 | 39 | **RESTORE** from `data/real/20` |
| `real_50` | 150 | 105 | 22 | 23 | **RESTORE** 145 missing images |
| `real_100` | 250 | 175 | 37 | 38 | **KEEP** |
| `real_200` | 250 | 175 | 37 | 38 | **RESTORE** from `data/real/200` |
| `real_500` | 144 | 101 | 21 | 22 | **KEEP** (augment to parity) |
| `real_2000` | 250 | 175 | 37 | 38 | **KEEP** |
| **TOTAL** | **3,195** | **2,236** | **478** | **481** | **Balanced 70/15/15 Stratified Split** |
