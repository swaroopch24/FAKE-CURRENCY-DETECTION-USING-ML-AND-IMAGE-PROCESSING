import os
import sys
import time
import json
from collections import defaultdict
import numpy as np
import tensorflow as tf

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.modules.ai_engine.loaders import ModelLoader
from src.modules.ai_engine.training.config import training_config
from src.modules.ai_engine.decision import DecisionEngine

def compute_metrics_multiclass(y_true, y_pred, class_names):
    num_classes = len(class_names)
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
        
    per_class = {}
    precisions = []
    recalls = []
    f1s = []
    supports = []
    
    for i, name in enumerate(class_names):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp
        support = int(np.sum(cm[i, :]))
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        
        per_class[name] = {
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1),
            "support": support
        }
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        supports.append(support)
        
    accuracy = float(np.sum(np.diag(cm)) / len(y_true)) if len(y_true) > 0 else 0.0
    macro_prec = float(np.mean(precisions))
    macro_rec = float(np.mean(recalls))
    macro_f1 = float(np.mean(f1s))
    
    total_supp = np.sum(supports)
    weighted_f1 = float(np.sum(np.array(f1s) * np.array(supports)) / total_supp) if total_supp > 0 else 0.0
    
    return {
        "accuracy": accuracy,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "confusion_matrix": cm.tolist(),
        "per_class": per_class
    }

def run_evaluation():
    print("=== STARTING FULL TECHNICAL AUDIT MODEL EVALUATION ===")
    loader = ModelLoader()
    model = loader.load_model()
    print("Loaded model:", model.name)
    print("Model input shape:", model.input_shape)
    print("Model output shape:", model.output_shape)
    
    test_dir = os.path.join("dataset", "split", "test")
    print(f"Loading test data from: {test_dir}")
    
    datagen = tf.keras.preprocessing.image.ImageDataGenerator()
    generator = datagen.flow_from_directory(
        directory=test_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode="categorical",
        classes=training_config.CLASS_NAMES,
        shuffle=False
    )
    
    print(f"Total test samples: {generator.samples}")
    print(f"Classes: {training_config.CLASS_NAMES}")
    
    # Measure latency
    start_time = time.time()
    predictions = model.predict(generator, verbose=1)
    total_time = time.time() - start_time
    avg_latency_ms = (total_time / generator.samples) * 1000.0
    print(f"Total prediction time: {total_time:.3f}s, Avg per sample: {avg_latency_ms:.2f}ms")
    
    y_pred = np.argmax(predictions, axis=1)
    y_true = generator.classes
    confidences = np.max(predictions, axis=1)
    filenames = generator.filenames
    
    # 1. 14-Class Metrics
    metrics_14 = compute_metrics_multiclass(y_true, y_pred, training_config.CLASS_NAMES)
    
    # 2. Binary Authenticity Report & Confusion Matrix
    def get_auth(idx):
        cls = training_config.CLASS_NAMES[idx]
        return "REAL" if "real" in cls.lower() else "FAKE"
        
    def get_denom(idx):
        cls = training_config.CLASS_NAMES[idx]
        return cls.split("_")[-1]
        
    y_true_auth = [0 if "real" in training_config.CLASS_NAMES[i].lower() else 1 for i in y_true] # 0: REAL, 1: FAKE
    y_pred_auth = []
    
    # Decision Engine evaluation for each prediction
    decision_engine = DecisionEngine()
    decision_states = []
    false_positives_auth = [] # Genuine predicted as Fake
    false_negatives_auth = [] # Fake predicted as Genuine (CRITICAL)
    misclassified_samples = []
    
    for i in range(len(y_true)):
        probs = predictions[i]
        max_idx = y_pred[i]
        p_real = sum(float(probs[j]) for j, name in enumerate(training_config.CLASS_NAMES) if "real" in name)
        p_fake = sum(float(probs[j]) for j, name in enumerate(training_config.CLASS_NAMES) if "fake" in name)
        
        pred_auth_code = 0 if p_real >= p_fake else 1 # 0: REAL, 1: FAKE
        y_pred_auth.append(pred_auth_code)
        
        # Decision engine run
        raw_res = {
            "class_label": training_config.CLASS_NAMES[max_idx],
            "confidence": float(confidences[i]),
            "p_real": p_real,
            "p_fake": p_fake,
            "raw_probabilities": probs.tolist()
        }
        dec = decision_engine.evaluate(raw_res)
        decision_states.append(dec["status"].value if hasattr(dec["status"], "value") else str(dec["status"]))
        
        # Track errors
        true_cls = training_config.CLASS_NAMES[y_true[i]]
        pred_cls = training_config.CLASS_NAMES[max_idx]
        
        if y_true[i] != max_idx:
            misclassified_samples.append({
                "filename": filenames[i],
                "true_class": true_cls,
                "pred_class": pred_cls,
                "confidence": float(confidences[i]),
                "p_real": p_real,
                "p_fake": p_fake,
                "true_auth": get_auth(y_true[i]),
                "pred_auth": "REAL" if pred_auth_code == 0 else "FAKE",
                "true_denom": get_denom(y_true[i]),
                "pred_denom": get_denom(max_idx),
                "decision_state": dec["status"].value if hasattr(dec["status"], "value") else str(dec["status"])
            })
            
        if y_true_auth[i] == 1 and pred_auth_code == 0:
            # FAKE predicted as REAL
            false_negatives_auth.append({
                "filename": filenames[i],
                "true_class": true_cls,
                "pred_class": pred_cls,
                "confidence": float(confidences[i]),
                "p_real": p_real,
                "p_fake": p_fake
            })
        elif y_true_auth[i] == 0 and pred_auth_code == 1:
            # REAL predicted as FAKE
            false_positives_auth.append({
                "filename": filenames[i],
                "true_class": true_cls,
                "pred_class": pred_cls,
                "confidence": float(confidences[i]),
                "p_real": p_real,
                "p_fake": p_fake
            })
            
    metrics_auth = compute_metrics_multiclass(y_true_auth, y_pred_auth, ["REAL", "FAKE"])
    
    # 3. Denomination Metrics
    denoms = ["10", "20", "50", "100", "200", "500", "2000"]
    denom_map = {d: i for i, d in enumerate(denoms)}
    y_true_denom_idx = [denom_map[get_denom(i)] for i in y_true]
    y_pred_denom_idx = [denom_map[get_denom(i)] for i in y_pred]
    metrics_denom = compute_metrics_multiclass(y_true_denom_idx, y_pred_denom_idx, denoms)
    
    # 4. Confidence Distribution
    conf_bins = {
        "<0.50": int(np.sum(confidences < 0.50)),
        "0.50-0.70": int(np.sum((confidences >= 0.50) & (confidences < 0.70))),
        "0.70-0.80": int(np.sum((confidences >= 0.70) & (confidences < 0.80))),
        "0.80-0.90": int(np.sum((confidences >= 0.80) & (confidences < 0.90))),
        "0.90-1.00": int(np.sum(confidences >= 0.90))
    }
    
    # Decision state counts
    dec_counts = {}
    for st in decision_states:
        dec_counts[st] = dec_counts.get(st, 0) + 1
        
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_test_samples": generator.samples,
        "latency": {
            "total_seconds": total_time,
            "avg_ms_per_sample": avg_latency_ms
        },
        "overall_14_class": {
            "accuracy": metrics_14["accuracy"],
            "macro_precision": metrics_14["macro_precision"],
            "macro_recall": metrics_14["macro_recall"],
            "macro_f1": metrics_14["macro_f1"],
            "weighted_f1": metrics_14["weighted_f1"],
            "confusion_matrix": metrics_14["confusion_matrix"]
        },
        "binary_authenticity": {
            "accuracy": metrics_auth["accuracy"],
            "macro_f1": metrics_auth["macro_f1"],
            "REAL_metrics": metrics_auth["per_class"]["REAL"],
            "FAKE_metrics": metrics_auth["per_class"]["FAKE"],
            "confusion_matrix_REAL_FAKE": metrics_auth["confusion_matrix"],
            "false_negatives_count_FAKE_predicted_as_REAL": len(false_negatives_auth),
            "false_positives_count_REAL_predicted_as_FAKE": len(false_positives_auth)
        },
        "denomination": {
            "accuracy": metrics_denom["accuracy"],
            "macro_f1": metrics_denom["macro_f1"],
            "per_denomination": metrics_denom["per_class"],
            "confusion_matrix": metrics_denom["confusion_matrix"]
        },
        "per_class_14": metrics_14["per_class"],
        "confidence_analysis": {
            "mean_confidence": float(np.mean(confidences)),
            "std_confidence": float(np.std(confidences)),
            "min_confidence": float(np.min(confidences)),
            "max_confidence": float(np.max(confidences)),
            "bins": conf_bins
        },
        "decision_engine_outcomes": dec_counts,
        "false_negatives_samples": false_negatives_auth,
        "false_positives_samples": false_positives_auth,
        "total_misclassified_14class": len(misclassified_samples),
        "misclassified_samples": misclassified_samples
    }
    
    out_path = os.path.join("backend", "AUDIT_TEST_EVALUATION_RESULTS.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results successfully saved to {out_path}")
    
    print("\n=======================================================")
    print("           AUDIT EVALUATION SUMMARY RESULTS            ")
    print("=======================================================")
    print(f"Total Test Samples Evaluated: {generator.samples}")
    print(f"14-Class Accuracy:            {metrics_14['accuracy']*100:.2f}%")
    print(f"14-Class Macro F1:            {metrics_14['macro_f1']*100:.2f}%")
    print(f"14-Class Weighted F1:         {metrics_14['weighted_f1']*100:.2f}%")
    print(f"-------------------------------------------------------")
    print(f"Authenticity Accuracy:        {metrics_auth['accuracy']*100:.2f}%")
    print(f"Authenticity Macro F1:        {metrics_auth['macro_f1']*100:.2f}%")
    print(f"REAL Precision / Recall / F1: {metrics_auth['per_class']['REAL']['precision']*100:.2f}% / {metrics_auth['per_class']['REAL']['recall']*100:.2f}% / {metrics_auth['per_class']['REAL']['f1_score']*100:.2f}%")
    print(f"FAKE Precision / Recall / F1: {metrics_auth['per_class']['FAKE']['precision']*100:.2f}% / {metrics_auth['per_class']['FAKE']['recall']*100:.2f}% / {metrics_auth['per_class']['FAKE']['f1_score']*100:.2f}%")
    print(f"False Negatives (FAKE->REAL): {len(false_negatives_auth)} ({len(false_negatives_auth)/250*100:.2f}% of fake test notes)")
    print(f"False Positives (REAL->FAKE): {len(false_positives_auth)} ({len(false_positives_auth)/238*100:.2f}% of real test notes)")
    print(f"-------------------------------------------------------")
    print(f"Denomination Accuracy:        {metrics_denom['accuracy']*100:.2f}%")
    print(f"Denomination Macro F1:        {metrics_denom['macro_f1']*100:.2f}%")
    print(f"-------------------------------------------------------")
    print(f"Avg Inference Latency (Batch):{avg_latency_ms:.2f} ms / sample")
    print(f"Confidence (Mean +/- Std):    {float(np.mean(confidences)):.4f} +/- {float(np.std(confidences)):.4f}")
    print(f"Confidence Bins:              {conf_bins}")
    print(f"Decision States:              {dec_counts}")
    print("=======================================================")

if __name__ == "__main__":
    run_evaluation()
