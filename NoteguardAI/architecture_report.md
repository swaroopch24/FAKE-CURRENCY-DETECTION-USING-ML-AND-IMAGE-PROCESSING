# Phase 9: AI Architecture & Design Report

## Overview
The AI pipeline has been strategically redesigned to decouple **Denomination Identification** from **Authenticity Assessment**. This architectural shift addresses severe data imbalances (specifically the 0 genuine samples for ₹2000) and enables highly specialized, multi-stage model execution.

## 1. What Changed
- **`config.py` Refactoring**: The static 14-class authenticity target has been dynamically restructured. `CLASSES` and `NUM_CLASSES` are now strictly derived from an active configuration of `SUPPORTED_AUTHENTICITY_DENOMINATIONS`.
- **`model_builder.py` Adjustment**: The standard MobileNetV2 head has been re-parameterized to default to 12 classes instead of 14.
- **Data Configuration Abstraction**: New configuration definitions have been introduced: `SPECIAL_STATUS_DENOMINATIONS`, `EXCLUDED_FROM_AUTHENTICITY`, and `FEATURE_ANALYSIS_DATASETS`.

## 2. Why ₹2000 is Excluded from Initial Authenticity Training
The `real_2000` class currently contains exactly 0 genuine images in our source dataset. Attempting to train a binary (real vs. fake) classifier without genuine examples forces the CNN to guess random features, resulting in a 100% false-positive or false-negative failure rate for ₹2000 notes. By excluding it, we prevent catastrophic interference and ensure high-confidence authenticity classifications for denominations where we actually possess verifiable ground truth.

## 3. Initial Authenticity Model Denominations
The first version of the authenticity CNN will be trained on the following 12 classes (Real/Fake pairs):
- ₹10
- ₹20
- ₹50
- ₹100
- ₹200
- ₹500

## 4. How ₹2000 Will Be Handled During Inference
At runtime, an incoming image will first be evaluated by a **Denomination Identification** model. If the note is identified as ₹2000:
1. The AI pipeline will immediately route it to a specialized handler.
2. It will **not** be passed into the authenticity CNN.
3. The system will return a configurable special-status flag (e.g., `withdrawn_from_circulation`), avoiding strict legal assertions.
4. Only non-₹2000 notes will proceed to the authenticity CNN.

## 5. Later Incorporation of a Denomination Classifier
The pipeline is staged to introduce a dedicated `DenominationClassifier` before the `AuthenticityClassifier`. This initial model will act as a routing layer, solving a simpler N-class problem (detecting visual denomination features). This staged approach significantly reduces the complexity of the authenticity model by ensuring it only evaluates intra-denomination differences (real vs. fake features of the *same* denomination).

## 6. How the Features Dataset Connects
The preserved `dataset/features/` subset (containing cropped security features like watermarks and security threads) will eventually train a granular **Security Feature Verification** model. This will act as the final confidence booster in the pipeline: once the authenticity model flags a note as genuine, the feature verification model will scan isolated regions of interest (ROIs) to definitively prove authenticity.
