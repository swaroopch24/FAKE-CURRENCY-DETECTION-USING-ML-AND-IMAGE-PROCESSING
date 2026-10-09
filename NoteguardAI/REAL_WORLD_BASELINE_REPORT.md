# NoteGuard AI — Real-World Testing & Baseline Specification

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Specification of Real-World Evaluation Benchmark

Validation and test accuracy on lab datasets do NOT represent production readiness. To measure genuine generalization, we establish the **NoteGuard Real-World Benchmark Dataset (NGRW-100)** protocol.

### Recommended Directory Structure:
```
dataset/
    real_world_testing/
        genuine/
            10/        # 15 unseen physical note captures
            20/        # 15 unseen physical note captures
            50/        # 15 unseen physical note captures
            100/       # 15 unseen physical note captures
            200/       # 15 unseen physical note captures
            500/       # 15 unseen physical note captures
            2000/      # 10 unseen physical note captures
        counterfeit/
            10/        # 10 reproduction / prop / fake samples
            20/        # 10 reproduction / prop / fake samples
            50/        # 10 reproduction / prop / fake samples
            100/       # 10 reproduction / prop / fake samples
            200/       # 10 reproduction / prop / fake samples
            500/       # 10 reproduction / prop / fake samples
            2000/      # 10 reproduction / prop / fake samples
```

---

## 2. Real-World Environmental Stress Variations

| Environmental Condition | Challenge to Model | Observed Baseline Vulnerability | Proposed Mitigation |
| :--- | :--- | :--- | :--- |
| **1. Harsh Fluorescent / Dim Lighting** | Color shifts alter note hue (e.g. ₹20 $\rightarrow$ greyish ₹500). | High denomination misclassification. | Color-jitter & histogram equalization augmentation during training. |
| **2. Rotations ($15^\circ - 45^\circ$)** | Distorts horizontal feature alignment. | Slight confidence drop; model occasionally predicts background. | Rotation augmentation up to $\pm 30^\circ$. |
| **3. Perspective / Angled Camera** | Keystone distortion of banknote aspect ratio. | Aspect ratio checks pass, but CNN feature map distorted. | Random perspective shear augmentation. |
| **4. Uncluttered vs Cluttered Background** | Wooden table, cloth, office desk, hand holding note. | Model attends to table wood grain rather than banknote print. | Random background synthesis / cutout in training. |
| **5. Mobile Phone Camera Flare / Glare** | White reflection patches over security thread/watermark. | Causes false `COUNTERFEIT` predictions on genuine notes. | Random Gaussian blur and specular highlight augmentation. |
| **6. Distant / Uncropped Note** | Banknote occupies $<50\%$ of image frame. | Model classifies dominant background rather than note. | Automatic OpenCV bounding-box detection & crop before CNN inference. |

---

## 3. Real-World Acceptance Criteria for V2 Production Model

1. **Overall Real-World 14-Class Accuracy**: $\ge 90.0\%$
2. **Real-World Authenticity Accuracy**: $\ge 95.0\%$
3. **Real-World False-REAL Count**: $\le 1$ per 100 test notes
4. **Denomination Accuracy (All 7 Denominations)**: $\ge 92.0\%$ each (no denomination under $85\%$)
5. **UTD Rejection Rate on Ambiguous / Non-Currency Inputs**: $\ge 90.0\%$
