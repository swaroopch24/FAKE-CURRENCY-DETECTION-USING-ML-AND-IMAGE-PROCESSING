# NoteGuard AI — Inference Pipeline Forensic Audit

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Inference Pipeline Trace & Verification

We audited the complete inference flow from incoming byte stream to output payload:

```
[UploadFile (FastAPI)] 
        │
        ▼ (read bytes)
[ImageValidator.validate_and_decode()] -> Validates magic bytes, checks size (10KB - 10MB), resolution (>= 100x100), aspect ratio (<= 10:1), EXIF transpose
        │
        ▼ (PIL.Image RGB)
[ImagePreprocessor.normalize_for_cnn()] -> Resizes to (224, 224) nearest, converts to float32 np.ndarray, expands dims to [1, 224, 224, 3]
        │
        ▼ (Numpy Array)
[AIInferenceService.execute_prediction()] -> Acquires thread lock, calls model.predict(tensor, verbose=0), extracts probabilities
        │
        ▼ (Dict with class_label, confidence, p_real, p_fake, raw_probabilities)
[DecisionEngine.evaluate()] -> Enforces 0.80 confidence threshold, aggregates p_real/p_fake, handles ₹2000 circulation rule
        │
        ▼ (Decision Dict)
[FastAPI Router Response] -> Encapsulates into VerificationResponse schema, commits record to PostgreSQL
```

---

## 2. Forensic Checks for Bad Engineering Practices

| Check Item | Forensic Findings | Verdict |
| :--- | :--- | :---: |
| **Mock or Dummy Predictions in Prod** | No mock predictions found in active `verify` pipeline. (`AI_PROVIDER=cnn` in `.env`). | **CLEAN** |
| **Filename-based Label Leakage** | The inference pipeline operates strictly on in-memory raw image bytes (`image_front.read()`). No filename heuristics exist. | **CLEAN** |
| **Stale Memory / Global Leakage** | `ModelLoader` encapsulates model loading inside a thread-safe singleton with double-checked locking (`_lock`). Prediction runs inside `pip_lock`. | **CLEAN** |
| **Concurrency Bottleneck** | `AIInferencePipeline` enforces `threading.Semaphore(MAX_CONCURRENT_INFERENCES = 2)` with a 0.1s timeout, rejecting excess traffic with HTTP 503 rather than unbounded queue starvation. | **CLEAN** |
| **Class Name Lookup Vulnerability** | `AIInferenceService.execute_prediction` uses `training_config.CLASS_NAMES[max_idx]` which suffers from the mapping offset audited in Phase 4. | **CRITICAL DEFECT** |
