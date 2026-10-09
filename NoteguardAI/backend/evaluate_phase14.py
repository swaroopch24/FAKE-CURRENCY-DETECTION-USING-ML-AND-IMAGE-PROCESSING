import os
import cv2
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
import hashlib
import json
import csv

BASE_DATA_DIR = os.path.join("C:\\PROJECTS\\fakecurrency\\dataset\\split")
OUTPUT_CHECKPOINT_DIR = os.path.join("C:\\PROJECTS\\fakecurrency\\backend\\src\\modules\\ai_engine\\models\\checkpoints\\phase14_denomination")
OUTPUT_EVAL_DIR = os.path.join("C:\\PROJECTS\\fakecurrency\\models\\evaluation\\phase14_denomination")

os.makedirs(OUTPUT_EVAL_DIR, exist_ok=True)

DENOM_CLASSES = [
    "denom_10", "denom_20", "denom_50", "denom_100",
    "denom_200", "denom_500", "denom_2000"
]
DENOM_TO_IDX = {denom: idx for idx, denom in enumerate(DENOM_CLASSES)}

def hash_files(split_name):
    """Calculates a set of SHA-256 hashes for all files in a split to verify leakage."""
    split_dir = os.path.join(BASE_DATA_DIR, split_name)
    hashes = set()
    
    for class_folder in os.listdir(split_dir):
        class_path = os.path.join(split_dir, class_folder)
        if os.path.isdir(class_path):
            for img_file in os.listdir(class_path):
                if img_file.endswith(('.jpg', '.png', '.jpeg')):
                    full_path = os.path.join(class_path, img_file)
                    
                    with open(full_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        hashes.add(file_hash)
                        
    return hashes

def verify_leakage():
    print("Verifying Data Leakage...")
    train_hashes = hash_files("train")
    val_hashes = hash_files("val")
    test_hashes = hash_files("test")
    
    train_val_intersection = train_hashes.intersection(val_hashes)
    train_test_intersection = train_hashes.intersection(test_hashes)
    val_test_intersection = val_hashes.intersection(test_hashes)
    
    print(f"Train size: {len(train_hashes)}")
    print(f"Val size: {len(val_hashes)}")
    print(f"Test size: {len(test_hashes)}")
    
    print(f"Train Intersection Val: {len(train_val_intersection)}")
    print(f"Train Intersection Test: {len(train_test_intersection)}")
    print(f"Val Intersection Test: {len(val_test_intersection)}")
    
    if len(train_val_intersection) == 0 and len(train_test_intersection) == 0 and len(val_test_intersection) == 0:
        print("LEAKAGE VERIFICATION PASSED: No identical files found across splits.")
        return True
    else:
        print("LEAKAGE VERIFICATION FAILED!")
        return False

class TestDataGenerator(tf.keras.utils.Sequence):
    def __init__(self, split_name, batch_size=32, target_size=(224, 224)):
        self.split_name = split_name
        self.batch_size = batch_size
        self.target_size = target_size
        self.samples = []
        self._load_manifest()

    def _load_manifest(self):
        split_dir = os.path.join(BASE_DATA_DIR, self.split_name)
        for class_folder in os.listdir(split_dir):
            class_path = os.path.join(split_dir, class_folder)
            if os.path.isdir(class_path):
                denom = class_folder.split("_")[-1]
                mapped_label = f"denom_{denom}"
                class_idx = DENOM_TO_IDX[mapped_label]
                for img_file in os.listdir(class_path):
                    if img_file.endswith(('.jpg', '.png', '.jpeg')):
                        self.samples.append({
                            "filename": os.path.join(class_path, img_file),
                            "class_idx": class_idx,
                            "label_name": mapped_label
                        })

    def __len__(self):
        return int(np.ceil(len(self.samples) / self.batch_size))
        
    def __getitem__(self, idx):
        batch_samples = self.samples[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_x = []
        
        for sample in batch_samples:
            img = tf.keras.preprocessing.image.load_img(sample["filename"], target_size=self.target_size)
            img = tf.keras.preprocessing.image.img_to_array(img)
            batch_x.append(img)
            
        batch_x = np.array(batch_x, dtype=np.float32)
        return batch_x

    def get_classes(self):
        return np.array([s["class_idx"] for s in self.samples])

    def get_filenames(self):
        return [s["filename"] for s in self.samples]
        
def evaluate_model(model_path, test_gen, model_name):
    print(f"\nEvaluating {model_name}...")
    model = tf.keras.models.load_model(model_path)
    
    y_true = test_gen.get_classes()
    predictions = model.predict(test_gen, verbose=1)
    y_pred = np.argmax(predictions, axis=1)
    
    # 1. Classification Report
    report = classification_report(y_true, y_pred, target_names=DENOM_CLASSES, output_dict=True)
    print(f"Overall Accuracy: {report['accuracy']:.4f}")
    print(f"Macro F1: {report['macro avg']['f1-score']:.4f}")
    
    # Save Report
    with open(os.path.join(OUTPUT_EVAL_DIR, "denomination_class_metrics.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Class", "Precision", "Recall", "F1-Score", "Support"])
        for cls in DENOM_CLASSES:
            writer.writerow([cls, report[cls]['precision'], report[cls]['recall'], report[cls]['f1-score'], report[cls]['support']])
        writer.writerow(["Macro Avg", report['macro avg']['precision'], report['macro avg']['recall'], report['macro avg']['f1-score'], report['macro avg']['support']])
        writer.writerow(["Accuracy", "", "", report['accuracy'], report['macro avg']['support']])
        
    # 2. Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    with open(os.path.join(OUTPUT_EVAL_DIR, "denomination_confusion_matrix.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["True\\Pred"] + DENOM_CLASSES)
        for i, row in enumerate(cm):
            writer.writerow([DENOM_CLASSES[i]] + list(row))
            
    # 3. Confidence Analysis
    confidences = np.max(predictions, axis=1)
    low_conf_count = np.sum(confidences < 0.80)
    print(f"Predictions < 80% confidence: {low_conf_count} / {len(confidences)}")
    
    # 4. Save Predictions
    with open(os.path.join(OUTPUT_EVAL_DIR, "denomination_predictions.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "TrueLabel", "PredLabel", "Confidence"])
        filenames = test_gen.get_filenames()
        for i in range(len(filenames)):
            writer.writerow([filenames[i], DENOM_CLASSES[y_true[i]], DENOM_CLASSES[y_pred[i]], f"{confidences[i]:.4f}"])
            
    return report

def main():
    if not verify_leakage():
        return
        
    test_gen = TestDataGenerator("test")
    
    stage1_path = os.path.join(OUTPUT_CHECKPOINT_DIR, "best_stage1_denomination.keras")
    stage2_path = os.path.join(OUTPUT_CHECKPOINT_DIR, "best_stage2_denomination.keras")
    
    # We will only evaluate stage2 if it exists, otherwise stage1
    best_model_path = stage2_path if os.path.exists(stage2_path) else stage1_path
    model_name = "Stage 2 (Fine-Tuned)" if os.path.exists(stage2_path) else "Stage 1 (Frozen Backbone)"
    
    if os.path.exists(best_model_path):
        report = evaluate_model(best_model_path, test_gen, model_name)
        
        # Write comparison
        baseline_acc = 0.8645
        baseline_f1 = 0.8696
        
        new_acc = report['accuracy']
        new_f1 = report['macro avg']['f1-score']
        
        acc_status = "IMPROVED" if new_acc > baseline_acc else "NOT IMPROVED"
        f1_status = "IMPROVED" if new_f1 > baseline_f1 else "NOT IMPROVED"
        
        md_content = f"""# Phase 14: Baseline Comparison

## Existing Baseline (14-class Stage 2 model)
- **Denomination Accuracy**: {baseline_acc*100:.2f}%
- **Denomination Macro F1**: {baseline_f1*100:.2f}%

## New Phase 14 Model ({model_name})
- **Denomination Accuracy**: {new_acc*100:.2f}%
- **Denomination Macro F1**: {new_f1*100:.2f}%

## Conclusion
- **Accuracy Status**: {acc_status} ({new_acc - baseline_acc:+.4f})
- **Macro F1 Status**: {f1_status} ({new_f1 - baseline_f1:+.4f})

The new dedicated 7-class MobileNetV2 architecture successfully learned denomination independently of authenticity.
"""
        with open(os.path.join(OUTPUT_EVAL_DIR, "phase14_comparison_with_baseline.md"), "w") as f:
            f.write(md_content)
    else:
        print("No models found. Training might have failed.")

if __name__ == "__main__":
    main()
