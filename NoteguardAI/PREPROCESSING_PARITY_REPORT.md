# NoteGuard AI — Preprocessing Parity & Normalization Audit

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Comparison Across Pipelines

| Attribute | Training Pipeline (`trainer.py`) | Production Inference (`pipeline.py` & `preprocessing.py`) | Validation Test (`evaluate_models.py`) | Parity Status | Risk / Impact |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Image Loading Library** | Keras `load_img` (PIL backend) | `PIL.Image.open(io.BytesIO)` | Keras `ImageDataGenerator` / PIL | **PARITY** | Consistent RGB color order across all entrypoints. |
| **EXIF Orientation Handling** | Handled natively by Keras `load_img` | `ImageOps.exif_transpose(img)` | Handled by Keras `load_img` | **PARITY** | Corrects mobile orientation metadata prior to resizing. |
| **Interpolation Algorithm** | Nearest Neighbor (`NEAREST`) | Nearest Neighbor (`NEAREST`) | Nearest Neighbor (`NEAREST`) | **PARITY (SUB-OPTIMAL)** | Consistent between train and prod, but nearest neighbor produces jagged aliasing on microtext and fine security guilloches. |
| **Pixel Normalization Range** | $[0, 255] \rightarrow [-1, 1]$ via `mobilenet_v2.preprocess_input` inside model Lambda layer | $[0, 255] \rightarrow [-1, 1]$ via embedded model Lambda layer | Embedded model Lambda layer | **PARITY** | Preprocessing layer is embedded directly in the Keras model graph. |
| **Contour Deskewing & Alignment** | **Disabled / None** | **Disabled / Commented out** | **Disabled / None** | **PARITY** | Disabling deskewing in production was correct because training did not use deskewing. |
| **Target Resolution** | $224 \times 224 \times 3$ | $224 \times 224 \times 3$ | $224 \times 224 \times 3$ | **PARITY** | Standard MobileNetV2 spatial dimensions. |

---

## 2. Experimental Benchmark of Preprocessing Pipelines

Historical experimental evaluation (`evaluate_pipelines.py`) on validation samples yielded:

| Preprocessing Pipeline | Accuracy | Precision | Recall | F1-Score | Processing Latency | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Pipeline A: Production PIL (Nearest)** | **80.06%** | **76.24%** | **74.18%** | **75.19%** | **12ms** | **Current Active Pipeline** |
| **Pipeline B: Pure Keras Generator** | 80.06% | 76.24% | 74.18% | 75.19% | 14ms | Exact match with Pipeline A |
| **Pipeline C: OpenCV Bilinear (No Deskew)** | 78.92% | 74.10% | 72.30% | 73.18% | 9ms | Slight distribution shift due to bilinear vs nearest interpolation |
| **Pipeline D: OpenCV + Active Deskewing** | 62.40% | 58.10% | 55.40% | 56.71% | 45ms | **Severe degradation** because model was never trained on cropped/deskewed notes! |

---

## 3. Engineering Recommendations for V2

1. **Retain Current Production Pipeline for Baseline**: Do not re-enable OpenCV deskewing until a model is explicitly trained from scratch on segmented/deskewed notes.
2. **Upgrade Interpolation in V2**: Train the V2 model using **Bicubic (`Image.Resampling.BICUBIC`) or Area (`cv2.INTER_AREA`)** resizing to eliminate high-frequency aliasing on security features.
