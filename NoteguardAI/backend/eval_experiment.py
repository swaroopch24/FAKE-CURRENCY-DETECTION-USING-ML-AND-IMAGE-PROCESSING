import os
import json
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import csv
from PIL import Image, ImageOps

class ExperimentEvaluator:
    def __init__(self, model_path: str, dataset_dir: str):
        print(f"Loading model from: {model_path}")
        self.model = tf.keras.models.load_model(model_path)
        self.dataset_dir = dataset_dir
        self.target_size = 224
        
        # Hardcode class names matching config
        self.class_names = [
            "fake_10", "fake_20", "fake_50", "fake_100", "fake_200", "fake_500", "fake_2000",
            "real_10", "real_20", "real_50", "real_100", "real_200", "real_500", "real_2000"
        ]
        
    def get_image_paths(self):
        paths = []
        labels = []
        for class_idx, class_name in enumerate(self.class_names):
            class_dir = os.path.join(self.dataset_dir, class_name)
            if not os.path.isdir(class_dir):
                continue
            for fname in os.listdir(class_dir):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                    paths.append(os.path.join(class_dir, fname))
                    labels.append(class_idx)
        return paths, labels

    def preprocess_image(self, path):
        pil_img = Image.open(path)
        pil_img = ImageOps.exif_transpose(pil_img)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        resized = pil_img.resize((self.target_size, self.target_size), resample=Image.Resampling.NEAREST)
        img_array = np.array(resized, dtype=np.float32)
        return img_array

    def evaluate(self, output_dir: str):
        paths, labels = self.get_image_paths()
        print(f"Evaluating on {len(paths)} validation images...")
        
        y_true = []
        y_pred = []
        confidences = []
        
        batch_size = 32
        for i in range(0, len(paths), batch_size):
            batch_paths = paths[i:i+batch_size]
            batch_labels = labels[i:i+batch_size]
            
            tensors = []
            for path in batch_paths:
                tensors.append(self.preprocess_image(path))
                
            batch_tensor = np.array(tensors)
            preds = self.model.predict(batch_tensor, verbose=0)
            
            for pred, label in zip(preds, batch_labels):
                pred_idx = np.argmax(pred)
                conf = float(pred[pred_idx])
                y_true.append(label)
                y_pred.append(pred_idx)
                confidences.append(conf)
                
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        confidences = np.array(confidences)
        
        # 1. 14-class Metrics
        acc_14 = accuracy_score(y_true, y_pred)
        prec_14 = precision_score(y_true, y_pred, average='macro', zero_division=0)
        rec_14 = recall_score(y_true, y_pred, average='macro', zero_division=0)
        f1_14 = f1_score(y_true, y_pred, average='macro', zero_division=0)
        
        # Denomination Mappings (strip real_/fake_ prefix)
        denom_true = [self.class_names[idx].split('_')[1] for idx in y_true]
        denom_pred = [self.class_names[idx].split('_')[1] for idx in y_pred]
        
        acc_denom = accuracy_score(denom_true, denom_pred)
        f1_denom = f1_score(denom_true, denom_pred, average='macro', zero_division=0)
        
        # Authenticity Mappings (is_real boolean)
        auth_true = ["real_" in self.class_names[idx] for idx in y_true]
        auth_pred = ["real_" in self.class_names[idx] for idx in y_pred]
        
        acc_auth = accuracy_score(auth_true, auth_pred)
        f1_auth = f1_score(auth_true, auth_pred, average='macro', zero_division=0)
        
        # False-REAL / False-FAKE
        auth_true = np.array(auth_true)
        auth_pred = np.array(auth_pred)
        false_real = np.sum((~auth_true) & auth_pred)  # True is Fake, Pred is Real
        false_fake = np.sum(auth_true & (~auth_pred))  # True is Real, Pred is Fake
        
        # Confidence Metrics
        avg_conf = np.mean(confidences)
        min_conf = np.min(confidences)
        max_conf = np.max(confidences)
        
        above_80_idx = confidences >= 0.80
        pct_above_80 = np.mean(above_80_idx) * 100
        pct_below_80 = 100 - pct_above_80
        
        # Accepted set accuracy
        if np.sum(above_80_idx) > 0:
            accepted_acc = accuracy_score(y_true[above_80_idx], y_pred[above_80_idx])
        else:
            accepted_acc = 0.0
            
        unable_rate = pct_below_80
        

        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        cm_path = os.path.join(output_dir, "experiment_1_confusion_matrix.csv")
        with open(cm_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([''] + self.class_names)
            for i, row in enumerate(cm):
                writer.writerow([self.class_names[i]] + list(row))
        
        metrics = {
            "14_class_accuracy": float(acc_14),
            "14_class_macro_precision": float(prec_14),
            "14_class_macro_recall": float(rec_14),
            "14_class_macro_f1": float(f1_14),
            "denomination_accuracy": float(acc_denom),
            "denomination_macro_f1": float(f1_denom),
            "authenticity_accuracy": float(acc_auth),
            "authenticity_macro_f1": float(f1_auth),
            "false_real_count": int(false_real),
            "false_fake_count": int(false_fake),
            "average_confidence": float(avg_conf),
            "minimum_confidence": float(min_conf),
            "maximum_confidence": float(max_conf),
            "pct_confidence_ge_80": float(pct_above_80),
            "pct_confidence_lt_80": float(pct_below_80),
            "accepted_set_accuracy": float(accepted_acc),
            "unable_to_determine_rate": float(unable_rate)
        }
        
        # Save metrics to CSV
        metrics_path = os.path.join(output_dir, "experiment_1_validation_metrics.csv")
        with open(metrics_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(metrics.keys())
            writer.writerow(metrics.values())
        
        print("\n=== Evaluation Results ===")
        for k, v in metrics.items():
            print(f"{k}: {v}")
            
        print(f"\nSaved confusion matrix to {cm_path}")
        print(f"Saved metrics to {metrics_path}")

if __name__ == "__main__":
    output_dir = r"C:\PROJECTS\fakecurrency\backend\src\modules\ai_engine\models\evaluation\phase28_model_improvement\experiment_1_targeted_augmentation"
    base_dir = r"C:\PROJECTS\fakecurrency"
    dataset_dir = os.path.join(base_dir, "dataset", "split", "val")
    
    # Load the best Stage 2 model rather than the final .h5 which has TrueDivide serialization issues
    model_path = os.path.join(output_dir, "stage2", "best_stage2.keras")
    
    evaluator = ExperimentEvaluator(model_path, dataset_dir)
    evaluator.evaluate(output_dir)
