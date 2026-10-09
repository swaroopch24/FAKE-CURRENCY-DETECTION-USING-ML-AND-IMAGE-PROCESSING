# NoteGuard AI — Training Pipeline Audit

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Current Model Architecture Overview

The existing model architecture in `backend/src/modules/ai_engine/training/model_builder.py` is a two-stage transfer learning pipeline based on **MobileNetV2**:

```
[Input Tensor: 224 x 224 x 3]
              │
              ▼
[tf.keras.applications.mobilenet_v2.preprocess_input] (Scales [0, 255] -> [-1, 1])
              │
              ▼
[MobileNetV2 Backbone (ImageNet Pretrained)] (Feature Extractor)
              │
              ▼
[GlobalAveragePooling2D] (1280 channels -> 1280 vector)
              │
              ▼
[Dense(256, activation='relu')]
              │
              ▼
[Dropout(rate=0.5)]
              │
              ▼
[Dense(14, activation='softmax', name='classification_head')]
```

### Parameter Breakdown:
- **Total Parameters**: 2,586,830 (~9.87 MB)
- **Trainable Parameters (Stage 1)**: 331,534 (Classification head only)
- **Trainable Parameters (Stage 2)**: 1,861,710 (Top backbone layers unfrozen + head)
- **Frozen Parameters (Stage 2)**: 725,120 (Bottom 100 MobileNetV2 layers)

---

## 2. Stage 1 vs Stage 2 Training Lifecycle

### Stage 1: Feature Extractor Training (Frozen Base)
- **Backbone Status**: Completely frozen (`base_model.trainable = False`).
- **Target**: Train only the newly initialized `Dense(256)` and `Dense(14)` classification head from random weights without destroying ImageNet representations.
- **Optimizer**: Adam ($\text{learning\_rate} = 1\times 10^{-3}$).
- **Loss**: Categorical Crossentropy.
- **Batch Size**: 32.
- **Epochs**: 20 epochs.
- **Augmentation**: Rotation ($\pm 15^\circ$), Brightness ($[0.8, 1.2]$), Width shift ($5\%$), Height shift ($5\%$).

### Stage 2: Base Network Fine-Tuning
- **Backbone Status**: Unfreeze layers with index $\ge 100$ (`base_model.layers[:100].trainable = False`).
- **Target**: Jointly adapt mid- and high-level convolutional filters (depthwise separable convolutions) to currency security patterns.
- **Optimizer**: Adam ($\text{learning\_rate} = 1\times 10^{-5}$).
- **Loss**: Categorical Crossentropy.
- **Epochs**: 20 fine-tuning epochs (Total 40).
- **Callbacks**:
  - `ModelCheckpoint(monitor='val_loss', save_best_only=True)`
  - `EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True)`
  - `ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-7)`

---

## 3. Flaws in the Current Formulation

1. **Single 14-Class Output Entanglement**:
   - The current model treats `fake_500` and `real_500` as two entirely distinct classes with zero shared label topology.
   - The network is forced to learn denomination and authenticity simultaneously inside a single 14-class softmax vector.
   - When a note is visually ambiguous in authenticity, the softmax distribution diffuses across multiple denomination bins, suppressing the top confidence score below 0.80 and causing spurious `UNABLE_TO_DETERMINE` verdicts.
2. **Missing Class Weighting**:
   - `trainer.py` does not apply `class_weight` during `model.fit()`, leading to heavy gradient dominance from over-represented classes (`fake_10`, `fake_100`, `fake_500`, `real_500`) over severely starved classes (`real_10`, `real_50`).
3. **Nearest-Neighbor Image Resizing**:
   - Both `trainer.py` (Keras generator) and `preprocessing.py` used `nearest` interpolation. Nearest neighbor creates jagged high-frequency aliasing on high-resolution banknote photos, degrading fine security guilloche lines and watermarks.
   - Bilinear or Bicubic (`INTER_AREA` for downscaling) is required for banknote image preservation.
