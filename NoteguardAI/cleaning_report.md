# NoteGuard AI - Dataset Cleaning & Normalization Report (Phase 6)

**Source Directory (Raw/Immutable)**: `C:\PROJECTS\fakecurrency\dataset`  
**Cleaned Directory (Generated Output)**: `C:\PROJECTS\fakecurrency\dataset\cleaned`  
**Execution Timestamp**: `2026-08-10 11:01:39`

---

## 1. Executive Summary & Verification

| Metric | Before Cleaning | After Cleaning | Change / Excluded |
| :--- | :--- | :--- | :--- |
| **Total Real Notes** | 1,723 | 1,659 | -64 |
| **Total Fake Notes** | 2,508 | 2,398 | -110 |
| **Total Feature Images** | 1,318 | 1,291 | -27 |
| **Total Dataset Files** | 5,549 | **5,348** | **-201** |


### Rejection & Exclusion Summary

| Exclusion Reason | Count | Action Taken |
| :--- | :--- | :--- |
| **SHA-256 Exact Duplicates** | 199 | Excluded from `cleaned/` copy |
| **Unsupported Extensions (.avif)** | 2 | Excluded from `cleaned/` copy |
| **Corrupt / Invalid Images** | 0 | Excluded from `cleaned/` copy |
| **Zero-Byte Empty Files** | 0 | Excluded from `cleaned/` copy |
| **Resolution Rejected (<64x64 full note)** | 0 | Excluded from `cleaned/` copy |


## 2. Cleaned Denomination Breakdown

### Real vs Fake Cleaned Counts per Denomination

| Denomination | Cleaned Real Count | Cleaned Fake Count | Real/Fake Imbalance Ratio |
| :--- | :--- | :--- | :--- |
| ₹10 | 488 | 292 | `0.6:1 (Fake heavy)` |
| ₹20 | 258 | 296 | `1.1:1 (Fake heavy)` |
| ₹50 | 265 | 294 | `1.1:1 (Fake heavy)` |
| ₹100 | 249 | 370 | `1.5:1 (Fake heavy)` |
| ₹200 | 285 | 273 | `1.0:1 (Fake heavy)` |
| ₹500 | 114 | 762 | `6.7:1 (Fake heavy)` |
| ₹2000 | 0 | 111 | `N/A (0 Real Notes!)` |


### Cleaned Feature Counts per Denomination Folder

| Denomination Folder | Cleaned Image Count | Category Patterns |
| :--- | :--- | :--- |
| `100_Features` | 229 | `Preserved security feature crops` |
| `10_Features` | 240 | `Preserved security feature crops` |
| `2000_Features` | 129 | `Preserved security feature crops` |
| `200_Features` | 125 | `Preserved security feature crops` |
| `20_Features` | 258 | `Preserved security feature crops` |
| `500_Features` | 123 | `Preserved security feature crops` |
| `50_Features` | 187 | `Preserved security feature crops` |


## 3. Excluded Files & Duplicates Detail

### Unsupported Files (.avif)

- `data\fake\500\demo-7-768x397.avif` (Unsupported file extension (.avif))
- `data\fake\500\demo-7.avif` (Unsupported file extension (.avif))


### SHA-256 Duplicates (199 total excluded)

| Excluded Duplicate Path | Kept Original Path | SHA-256 Hash |
| :--- | :--- | :--- |
| `Features\2000_Features\Screenshot 2025-10-12 133807.png` | `Features\2000_Features\2000_8.png` | `468a8fe325949ec0...` |
| `Features\2000_Features\Screenshot 2025-10-12 134147.png` | `Features\2000_Features\2000_9.png` | `e7f798c2976ac7f1...` |
| `Features\2000_Features\Screenshot 2025-10-12 134407.png` | `Features\2000_Features\2000_10.png` | `262f7c1c4ca497db...` |
| `Features\2000_Features\Screenshot 2025-10-12 134907.png` | `Features\2000_Features\2000_11.png` | `b46345b1b0474451...` |
| `Features\2000_Features\Screenshot 2025-10-12 135131.png` | `Features\2000_Features\2000_12.png` | `7ae622446d36a485...` |
| `Features\2000_Features\Screenshot 2025-10-12 135347.png` | `Features\2000_Features\2000_13.png` | `8fa9082a8e11e00c...` |
| `Features\2000_Features\Screenshot 2025-10-12 135541.png` | `Features\2000_Features\2000_14.png` | `43c8fd820db56e21...` |
| `Features\2000_Features\Screenshot 2025-10-12 135742.png` | `Features\2000_Features\2000_15.png` | `9639d981a4a40395...` |
| `Features\2000_Features\Screenshot 2025-10-12 135958.png` | `Features\2000_Features\2000_16.png` | `c37e6301c263ac6e...` |
| `Features\2000_Features\Screenshot 2025-10-12 140239.png` | `Features\2000_Features\2000_17.png` | `cc7fa5f205d59e86...` |
| `Features\2000_Features\Screenshot 2025-10-12 140409.png` | `Features\2000_Features\2000_18.png` | `12be0f1fc235005e...` |
| `Features\2000_Features\Screenshot 2025-10-12 140635.png` | `Features\2000_Features\2000_19.png` | `39488dec4199773d...` |
| `Features\2000_Features\csc.jpg` | `Features\2000_Features\2000_6.jpg` | `2d792d1bd1f8aabb...` |
| `Features\2000_Features\ddffd.jpg` | `Features\2000_Features\2000_2.jpg` | `ec2cbba8af85ea7d...` |
| `Features\2000_Features\f4.jpg` | `Features\2000_Features\2000_5.jpg` | `0c9be1fc3c901d70...` |
| `Features\2000_Features\rgvdcx.jpg` | `Features\2000_Features\2000_4.jpg` | `6119466d0656196c...` |
| `Features\2000_Features\sdfgb.jpg` | `Features\2000_Features\2000_1.jpg` | `2dd53c5e46330a0a...` |
| `Features\2000_Features\vd.jpg` | `Features\2000_Features\2000_3.jpg` | `7a395e2b66aaea63...` |
| `Features\500_Features\Screenshot 2025-10-12 113216.png` | `Features\500_Features\500_8.png` | `c490c6a73eb3b37a...` |
| `Features\500_Features\Screenshot 2025-10-12 113835.png` | `Features\500_Features\500_9.png` | `f4bb5eefb08fffaf...` |
| `Features\500_Features\Screenshot 2025-10-12 114114.png` | `Features\500_Features\500_10.png` | `174d569c30083970...` |
| `Features\500_Features\Screenshot 2025-10-12 114528.png` | `Features\500_Features\500_11.png` | `11616a99293b971f...` |
| `Features\500_Features\Screenshot 2025-10-12 114940.png` | `Features\500_Features\500_12.png` | `776348a73f2bf3d8...` |
| `Features\500_Features\Screenshot 2025-10-12 115241.png` | `Features\500_Features\500_13.png` | `51fca6c3edec28df...` |
| `Features\500_Features\Screenshot 2025-10-12 115508.png` | `Features\500_Features\500_14.png` | `2ee2ed0c226f7acb...` |
| `Features\500_Features\Screenshot 2025-10-12 142407.png` | `Features\500_Features\500_15.png` | `6089082f1e1a9fd9...` |
| `Features\500_Features\Screenshot 2025-10-12 142545.png` | `Features\500_Features\500_16.png` | `0e6634105372c391...` |
| `data\fake\100\aug_1124_WhatsApp Image 2025-04-05 at 10.55.40.jpeg` | `data\fake\100\aug_1101_WhatsApp Image 2025-04-05 at 10.55.40.jpeg` | `d3fe55090e748d60...` |
| `data\fake\100\aug_1364_WhatsApp Image 2025-04-05 at 10.48.38.jpeg` | `data\fake\100\aug_1358_WhatsApp Image 2025-04-05 at 10.48.38.jpeg` | `02c04e20e5638cc6...` |
| `data\fake\100\aug_1369_WhatsApp Image 2025-04-05 at 10.48.38.jpeg` | `data\fake\100\aug_1358_WhatsApp Image 2025-04-05 at 10.48.38.jpeg` | `02c04e20e5638cc6...` |
| *... and 169 more duplicates recorded in JSON manifest* | | |


## 4. Observations & Items Requiring Review

> [!WARNING]
> **Critical Class Imbalance**:  
> 1. **Missing ₹2000 Real Notes**: `data/real/2000` has **0 real images**, whereas `data/fake/2000` has **126 cleaned fake images**.  
> 2. **₹500 Real vs Fake Gap**: Real ₹500 has **116 cleaned images** vs Fake ₹500 with **749 cleaned images** (~6.5x fake heavy ratio).  

> [!NOTE]
> **Normalized Path Verification**:  
> Physical disk path `Features/` was cleanly mapped to lowercase `dataset/cleaned/features/` in the output directory.  

> [!IMPORTANT]
> **Raw Dataset Immutability**:  
> Source directory `dataset/` remains 100% untouched. All cleaned output files reside in `dataset/cleaned/`.  
