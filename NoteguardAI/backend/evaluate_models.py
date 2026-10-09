import os
import json
import csv
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from src.modules.ai_engine.training.config import training_config

EVAL_DIR = os.path.join(training_config.BASE_DIR, "models", "evaluation", "phase11")
os.makedirs(EVAL_DIR, exist_ok=True)

def load_test_data(test_dir):
    datagen = tf.keras.preprocessing.image.ImageDataGenerator()
    generator = datagen.flow_from_directory(
        directory=test_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        classes=training_config.CLASS_NAMES,
        shuffle=False
    )
    return generator

def parse_class_label(label):
    parts = label.split("_")
    authenticity = "REAL" if "real" in label.lower() else "FAKE"
    denomination = parts[-1]
    return authenticity, denomination

def analyze_predictions(model, generator, stage_name):
    print(f"\n--- Evaluating {stage_name} ---")
    predictions = model.predict(generator, verbose=1)
    y_pred = np.argmax(predictions, axis=1)
    y_true = generator.classes
    confidences = np.max(predictions, axis=1)
    filenames = generator.filenames
    class_labels = list(generator.class_indices.keys())
    
    # 1. Overall & Per-Class Metrics
    report_dict = classification_report(y_true, y_pred, target_names=class_labels, output_dict=True, zero_division=0)
    
    # Save Classification Report CSV
    csv_report_path = os.path.join(EVAL_DIR, f"classification_report_{stage_name}.csv")
    with open(csv_report_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Class", "Precision", "Recall", "F1-Score", "Support"])
        for k, v in report_dict.items():
            if k not in ['accuracy', 'macro avg', 'weighted avg']:
                writer.writerow([k, v['precision'], v['recall'], v['f1-score'], v['support']])
        writer.writerow(["macro avg", report_dict['macro avg']['precision'], report_dict['macro avg']['recall'], report_dict['macro avg']['f1-score'], report_dict['macro avg']['support']])
        writer.writerow(["weighted avg", report_dict['weighted avg']['precision'], report_dict['weighted avg']['recall'], report_dict['weighted avg']['f1-score'], report_dict['weighted avg']['support']])

    # 2. Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    cm_csv_path = os.path.join(EVAL_DIR, f"confusion_matrix_{stage_name}.csv")
    with open(cm_csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["True\\Pred"] + class_labels)
        for i, row in enumerate(cm):
            writer.writerow([class_labels[i]] + row.tolist())

    # 3. Authenticity Analysis
    y_true_auth = [parse_class_label(class_labels[idx])[0] for idx in y_true]
    y_pred_auth = [parse_class_label(class_labels[idx])[0] for idx in y_pred]
    auth_report = classification_report(y_true_auth, y_pred_auth, output_dict=True, zero_division=0)
    auth_cm = confusion_matrix(y_true_auth, y_pred_auth, labels=["REAL", "FAKE"])
    
    # 4. Denomination Analysis
    y_true_denom = [parse_class_label(class_labels[idx])[1] for idx in y_true]
    y_pred_denom = [parse_class_label(class_labels[idx])[1] for idx in y_pred]
    denom_report = classification_report(y_true_denom, y_pred_denom, output_dict=True, zero_division=0)

    # 5. Confidence & Error Analysis
    correct_conf = []
    incorrect_conf = []
    misclassified = []
    low_conf_count = 0
    CONFIDENCE_THRESHOLD = 0.60
    
    for i in range(len(y_true)):
        is_correct = (y_true[i] == y_pred[i])
        conf = float(confidences[i])
        
        if is_correct:
            correct_conf.append(conf)
        else:
            incorrect_conf.append(conf)
            misclassified.append({
                "Filename": filenames[i],
                "True_Class": class_labels[y_true[i]],
                "Pred_Class": class_labels[y_pred[i]],
                "Confidence": conf
            })
            
        if conf < CONFIDENCE_THRESHOLD:
            low_conf_count += 1
            
    conf_analysis = {
        "average_confidence": float(np.mean(confidences)),
        "avg_confidence_correct": float(np.mean(correct_conf)) if correct_conf else 0.0,
        "avg_confidence_incorrect": float(np.mean(incorrect_conf)) if incorrect_conf else 0.0,
        "low_confidence_predictions_under_0.60": low_conf_count
    }

    misclassified_csv_path = os.path.join(EVAL_DIR, f"misclassified_samples_{stage_name}.csv")
    with open(misclassified_csv_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Filename", "True_Class", "Pred_Class", "Confidence"])
        writer.writeheader()
        writer.writerows(misclassified)

    # Output JSON Artifact
    results = {
        "stage": stage_name,
        "metrics": {
            "accuracy": report_dict['accuracy'],
            "macro_f1": report_dict['macro avg']['f1-score'],
            "weighted_f1": report_dict['weighted avg']['f1-score']
        },
        "binary_authenticity": auth_report,
        "denomination": denom_report,
        "confidence_analysis": conf_analysis
    }
    
    with open(os.path.join(EVAL_DIR, f"test_results_{stage_name}.json"), 'w') as f:
        json.dump(results, f, indent=4)
        
    return results

if __name__ == "__main__":
    print("=== NOTEGUARD AI PHASE 11 EVALUATION ===")
    project_root = os.path.abspath(os.path.join(training_config.BASE_DIR, "..", "..", "..", ".."))
    test_dir = os.path.join("C:\\PROJECTS\\fakecurrency\\dataset\\split\\test")
    
    generator = load_test_data(test_dir)
    print(f"Discovered Classes: {list(generator.class_indices.keys())}")
    
    stage1_path = os.path.join(training_config.OUTPUT_MODEL_DIR, "stage1", "best_stage1.keras")
    stage2_path = os.path.join(training_config.OUTPUT_MODEL_DIR, "stage2", "best_stage2.keras")
    
    print("Loading Stage 1 model...")
    model1 = tf.keras.models.load_model(stage1_path)
    res1 = analyze_predictions(model1, generator, "stage1")
    
    print("Loading Stage 2 model...")
    model2 = tf.keras.models.load_model(stage2_path)
    res2 = analyze_predictions(model2, generator, "stage2")
    
    print("Evaluation Complete. Results saved to", EVAL_DIR)
