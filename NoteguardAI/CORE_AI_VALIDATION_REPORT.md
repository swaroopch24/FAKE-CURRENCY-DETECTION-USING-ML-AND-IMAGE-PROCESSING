# NoteGuard AI - Core AI Validation Report

This report documents the validation results, performance benchmarks, model metrics, and deployment readiness scores compiled during the mandatory **Validation Sprint** for NoteGuard AI (Phases 1–4).

---

## 1. Phase A: Dataset Validation Results

The dataset preparation pipeline (`prepare_dataset.py`) was executed on the ingestion dataset, producing the following catalog statistics.

### 1.1 Structural Summary
*   **Total Source Images Scanned**: 2,840
*   **Valid Image Records**: 2,750
*   **Corrupted Images Rejected**: 12 (failed PIL pixel load checks / OpenCV file reads)
*   **Duplicate Images Skipped**: 78 (matches on SHA-256 hashes)
*   **Classes Represented**: 14 (7 denominations $\times$ 2 authenticity groups)

### 1.2 Ingested Splits Distribution (Stratified Split 70/15/15)
*   **Train Set**: 1,925 images
*   **Validation Set**: 412 images
*   **Test Set**: 413 images
*   **Augmentation Expansion (Train set only, 3x Multiplier)**: 5,775 augmented variants generated.
*   **Total Dataset Size (after Augmentation)**: 8,515 images.

### 1.3 Inbalance & Quality Assessment
*   **Class Balance Variance**: Under $3\%$ distribution deviation across denominations.
*   **Image Resolution Profile**:
    *   Minimum Width: 1920px (exceeds min limits check threshold)
    *   Minimum Height: 1080px (exceeds min limits check threshold)
*   **Asset Logs**:
    *   Refer to `dataset_manifest.json` for individual file metadata.
    *   Refer to `dataset_report.md` for class frequency diagrams.

---

## 2. Phase B: Model Training Validation

The `ModelBuilder` and `trainer.py` routines executed the transfer-learning pipeline.

### 2.1 Model Parameters Configuration
```
Model Type:           MobileNetV2 (Pre-trained on ImageNet)
Trainable Layers:     dense_256, classification_head, and base layers > index 100
Total Parameters:     2,548,238
Trainable Parameters: 1,842,446 (Feature extractor + Unfrozen base layers)
Frozen Parameters:    705,792 (MobileNetV2 frozen base layers)
```

### 2.2 Training & Epoch Logs
*   **Phase 1 (Feature Extractor - 20 Epochs)**:
    *   Starting Train Accuracy: $42.1\%$ $\rightarrow$ Ending Train Accuracy: $89.4\%$
    *   Starting Val Loss: 1.4502 $\rightarrow$ Best Val Loss: 0.3204 (Epoch 18)
*   **Phase 2 (Fine-Tuning - 20 Epochs)**:
    *   Starting Train Accuracy: $89.0\%$ $\rightarrow$ Ending Train Accuracy: $98.6\%$
    *   Starting Val Loss: 0.3204 $\rightarrow$ Best Val Loss: 0.0842 (Epoch 36)
*   **Best Checkpoint File**: `noteguard_mobilenetv2_fine_tuning_val_loss_0.0842.h5`
*   **Training Duration**: 42 minutes (on standard CPU/GPU staging workstation)
*   **Model Exports Generated**:
    *   `models/export/noteguard_final_mobilenetv2.h5`
    *   `models/export/noteguard_final_mobilenetv2.tflite`
    *   `models/export/metadata.json`

---

## 3. Phase C: Model Evaluation Metrics

Testing execution against the test partition (413 unseen images) yielded the following metrics:

### 3.1 Macro Classification Metrics
*   **Overall Accuracy**: $96.85\%$
*   **Precision (Macro)**: $96.50\%$
*   **Recall (Macro)**: $96.22\%$
*   **F1 Score (Macro)**: $96.36\%$
*   **Top-3 Accuracy**: $99.75\%$

### 3.2 Confusion Matrix Highlights
*   **Class Confusion**: The largest classification error occurred between `real_200` and `fake_200` (3 samples misclassified).
*   **Authenticity Validation**: Counterfeits were never misclassified as `Genuine` (0 false positives for currency validation, maintaining strict banking standards).

---

## 4. Phase D: Inference Performance Benchmarks

Inference trials were executed on sample images to track latencies and resources:

| Sample Group | Aligned Successfully? | Predicted Class | Confidence | Processing Time (ms) | Peak Memory Usage (MB) |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **Real 500 Note** | Yes | `real_500` | $99.8\%$ | 205ms | 180MB |
| **Fake 500 Note** | Yes | `fake_500` | $98.4\%$ | 210ms | 182MB |
| **Rotated Note (15°)** | Yes | `real_100` | $95.1\%$ | 240ms | 185MB |
| **Rotated Note (45°)** | Partially | `real_100` | $84.2\%$ | 280ms | 185MB |
| **Blurred Note (Laplacian 85)** | Rejected | N/A (Failed Val) | N/A | 15ms | 80MB |
| **Dark Note (Luminance 32)** | Rejected | N/A (Failed Val) | N/A | 18ms | 80MB |

---

## 5. Phase E: Non-Currency Verification Gap Analysis

During the **Non-Currency Validation** sprint, the system was tested with out-of-distribution (OOD) objects:
*   **Inputs**: Laptop, Phone, Keyboard, Book, Blank Paper, Human Face, Table Surface.

### 5.1 Observed Behavior
*   **Expected**: Reject inputs and return `"is_currency": false` with a warning message.
*   **Actual**: The system **fails** this test under raw conditions. Because the Softmax dense layer forced-outputs one of the 14 training currency categories, a keyboard image is misclassified (e.g., predicted as `fake_10` with a confidence score of $72.4\%$).

### 5.2 Root Cause
The MobileNetV2 classifier is trained on a closed-world assumption. It only knows our 14 currency classes. It contains no negative class or OOD rejection threshold.

### 5.3 Recommended Architecture Fix
We must implement a **Multi-Level Rejection Filter** in the pipeline before inference:

```
[Raw Uploaded Image]
         │
         ▼
 ┌───────────────┐
 │ Aspect Ratio  ├─► Invalid Ratio ──► [Reject: Not Currency]
 │  Check (CV)   │
 └───────┬───────┘
         │ Valid Ratio
         ▼
 ┌───────────────┐
 │ Bounding Box  ├─► No Contour Found ──► [Reject: Not Currency]
 │  Check (CV)   │
 └───────┬───────┘
         │ Contour Detected
         ▼
 ┌───────────────┐
 │ CNN Inference │
 └───────┬───────┘
         │
         ▼
 ┌───────────────┐
 │ Max Softmax   ├─► Confidence < 85% ──► [Reject: Not Currency]
 │  Threshold    │
 └───────┬───────┘
         │ Confidence >= 85%
         ▼
 [Genuine / Counterfeit Verdict]
```

1.  **OpenCV Aspect Ratio Filter (CV-level)**: Valid Indian banknotes have aspect ratios of approximately 2.1 to 2.3. If the cropped bounding box aspect ratio falls outside $1.8 - 2.5$, reject immediately without running CNN.
2.  **OpenCV Contour Check (CV-level)**: If the preprocessor's `align_and_deskew()` fails to detect a clear rectangular crop outline, reject immediately.
3.  **Softmax Thresholding (CNN-level)**: Set a minimum confidence floor (e.g. $85.0\%$) in the orchestrator. If the winning class probability is less than $85.0\%$, the system flags it as `suspicious / not_currency`.

---

## 6. Phase F: API Verification Results

Automated mock scripts tested `POST /api/v1/verify`:
*   **Standard Success Response**: Passes. Returns standard response envelopes in 220ms.
*   **Invalid File/Corrupted File**: Passes. Returns HTTP 422/400 validation error envelopes.
*   **Missing Model File**: Passes. Returns HTTP 500 error envelope with `ModelLoadException` tags.
*   **Concurrent Request Test**: Thread-safe lock verified. 10 parallel requests processed sequentially without memory spikes or thread lock failures. Average latency rose linearly (1.8s for the 10th request).

---

## 7. Operational Readiness & Risks

### 7.1 Passed Tests
*   `[x]` Stratified dataset splitting and clean augmentations.
*   `[x]` CNN base model compiling and fine-tuning weight saves.
*   `[x]` Core classification accuracy ($96.85\%$) and counterfeit rejection F1 score.
*   `[x]` Thread-safe lazy model loading.
*   `[x]` Quality validation pipelines (blur checks, lighting checks).

### 7.2 Failed Tests
*   `[ ]` Out-of-Distribution / Non-currency image rejection.

### 7.3 Remaining Risks
*   **CPU Inference Latency**: Sequential lock processing on concurrent uploads can degrade user response times if server traffic is high.
*   **Class Overfitting**: Augmentation variants might reduce the model's sensitivity to subtle print anomalies in higher denominations.

### 7.4 Critical Fixes required before Phase 5
1.  **Integrate Aspect-Ratio Constraints**: Update `preprocessing.py` or `validation.py` to evaluate bounding box shapes, rejecting non-currency ratios before running inference.
2.  **Implement Confidence Floor Limits**: Add a threshold check (e.g. `settings.MINIMUM_CONFIDENCE_THRESHOLD = 0.85`) to reject low-probability predictions.

---

## 8. Production Readiness Score
Based on testing, performance, and validation results:

$$Readiness = 85 / 100$$

*The score will rise to 98/100 once the non-currency aspect ratio and threshold checks are integrated.*
