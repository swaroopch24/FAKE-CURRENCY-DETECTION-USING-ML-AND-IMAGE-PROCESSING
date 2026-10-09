# NoteGuard AI — Project History and Requirements Audit

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Executive Summary of Project Evolution

NoteGuard AI is an automated authenticity verification system for Indian currency banknotes (₹10, ₹20, ₹50, ₹100, ₹200, ₹500, ₹2000). The project has evolved across multiple architectural iterations:

1. **Initial Baseline**: Single MobileNetV2 transfer-learning network trained on 14 classes (7 denominations $\times$ 2 authenticity groups: `fake_10`, `fake_20`, ..., `real_2000`). Initial validation accuracy was approximately $54.94\%$.
2. **Phase 1-4 (Sprint Validation)**: Ingestion of 2,840 images, stratified splitting, and augmentation yielding 8,515 images. High training accuracy ($98.6\%$) was reported in `CORE_AI_VALIDATION_REPORT.md`, but real-world out-of-distribution (OOD) tests failed completely (e.g. keyboards classified as `fake_10` with 72% confidence).
3. **Phase 14**: Development of a dedicated 7-class denomination classifier (`train_phase14.py`) to isolate denomination prediction from authenticity.
4. **Phase 15-16**: Investigation into confidence calibration and error analysis. Found that a confidence floor of $0.80$ eliminates a significant fraction of spurious false predictions.
5. **Phase 28 (Targeted Augmentation Experiment 1)**: Introduction of targeted augmentation for underrepresented classes. Reported validation accuracy of $80.06\%$ and authenticity accuracy of $97.95\%$.
6. **Phase 29**: Introduction of **Aggregate Authenticity Scoring**:
   $$\text{real\_score} = \sum_{c \in \text{real\_classes}} P(c)$$
   $$\text{fake\_score} = \sum_{c \in \text{fake\_classes}} P(c)$$
   $$\text{authenticity\_confidence} = \max(\text{real\_score}, \text{fake\_score})$$
   $$\text{verdict} = \begin{cases} \text{AUTHENTIC}, & \text{if } \text{real\_score} \ge \text{fake\_score} \\ \text{COUNTERFEIT}, & \text{otherwise} \end{cases}$$
7. **Phase 30 & Current State**: Discovered that earlier application runs were loading legacy model checkpoints. When updated to Phase 28 weights, controlled examples (e.g. genuine ₹500, counterfeit ₹100) worked, but real-world testing uncovered major failures (e.g., genuine ₹20 predicted as genuine ₹500; fake ₹20 predicted as real ₹500).

---

## 2. Requirement Taxonomy Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             REQUIREMENTS AUDIT                              │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│ DOCUMENTED REQUIREMENTS  │  CURRENT IMPLEMENTATION  │     RECOMMENDATIONS   │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ 14-Class CNN inference   │ 14-Class MobileNetV2     │ Two-head / Multi-task │
│ with high accuracy.      │ with aggregate scoring.  │ architecture (Auth +  │
│                          │ Suffers class confusion. │ Denom separated).     │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ Separate Authenticity &  │ Authenticity aggregated; │ Separate output heads │
│ Denomination confidence. │ Denom = argmax(class).   │ with dedicated loss   │
│                          │                          │ functions.            │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ Safe decision threshold  │ 0.80 threshold in        │ Calibrated threshold  │
│ (UTD on uncertainty).    │ DecisionEngine. Returns  │ with temperature      │
│                          │ UNABLE_TO_DETERMINE.     │ scaling.              │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ Special handling for     │ Maps ₹2000 to            │ Retain rule; prevent  │
│ ₹2000 demonetized note.  │ WITHDRAWN_FROM_CIRC.     │ false-trigger on ₹500 │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ User Auth & RBAC         │ JWT Auth, bcrypt,        │ Retain existing       │
│ (Admin vs Teller).       │ Role-based history.      │ robust implementation │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ Non-currency OOD         │ Only basic aspect ratio  │ Add OpenCV contour    │
│ rejection.               │ and size checks in PIL.  │ + aspect filter.      │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ Frontend Single Page App │ React 18 + Vite + TS.    │ Source of truth.      │
│ (Clean migration).       │ Fully functional SPA.    │ Retain React SPA.     │
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

---

## 3. Functional Requirements Status

| ID | Requirement | Documented Specification | Current Status | Defect / Note |
| :--- | :--- | :--- | :---: | :--- |
| **FR-01** | Image Upload & Ingestion | Support JPEG/PNG up to 10MB; min 100x100px. | **Implemented** | Handled in `validation.py`. |
| **FR-02** | Safe Validation | Decompression bomb protection, magic bytes verification. | **Implemented** | Uses PIL format validation. |
| **FR-03** | Currency Authenticity | Binary Genuine vs Counterfeit verdict. | **Partially Implemented** | Uses aggregate probabilities; high error on ₹20/₹50 notes. |
| **FR-04** | Denomination Detection | Identify ₹10, ₹20, ₹50, ₹100, ₹200, ₹500, ₹2000. | **Defective** | Suffers severe class-mapping and training imbalance collapse. |
| **FR-05** | Decision Engine Policy | Thresholding (0.80) with `UNABLE_TO_DETERMINE` state. | **Implemented** | Working as designed in `decision.py`. |
| **FR-06** | ₹2000 Circulation Rule | Flag genuine ₹2000 notes as withdrawn from circulation. | **Implemented** | Handled in `decision.py`. |
| **FR-07** | Relational Persistence | Store verification records, prediction scores, and timestamps. | **Implemented** | PostgreSQL models and migrations operational. |
| **FR-08** | Authentication & RBAC | Role-based permissions (`ROLE_ADMIN`, `ROLE_TELLER`). | **Implemented** | History queries enforce user isolation. |
| **FR-09** | Reporting & Analytics | Dashboard KPIs and verification history logs. | **Implemented** | React frontend charts and history views active. |
| **FR-10** | Security Feature Check | Inspection of Watermark, Security Thread, Microtext. | **Not Implemented (UI Simulated)** | Model does not perform regional ROI feature inspection. |

---

## 4. Non-Functional Requirements Status

- **Local Inference Latency**: Target < 500ms per note. Observed: ~200-250ms on CPU/GPU.
- **Thread Safety**: Double-check locking implemented in `ModelLoader` and `threading.Semaphore(2)` concurrency limiter in `pipeline.py`.
- **Zero Data Leakage**: Enforced by SHA-256 hash checks between dataset partitions.
