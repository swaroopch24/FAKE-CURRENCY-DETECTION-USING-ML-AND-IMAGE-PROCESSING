import os
import time
import json
import numpy as np
import tensorflow as tf
import cv2
from PIL import Image, ImageOps
from src.modules.ai_engine.training.config import training_config
from src.modules.ai_engine.preprocessing import ImagePreprocessor

# Force CPU inference for consistent evaluation
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class PipelineEvaluator:
    def __init__(self, model_path: str, dataset_dir: str):
        print(f"Loading model from: {model_path}")
        self.model = tf.keras.models.load_model(model_path)
        self.dataset_dir = dataset_dir
        self.target_size = training_config.IMAGE_SIZE
        self.class_names = training_config.CLASS_NAMES
        self.preprocessor = ImagePreprocessor()
        
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

    def evaluate_pipeline(self, name: str, pipeline_func, paths, labels):
        print(f"\n--- Evaluating Pipeline: {name} ---")
        y_true = []
        y_pred = []
        confidences = []
        
        specific_14_conf = None
        
        batch_size = 32
        
        start_time = time.time()
        
        # We will batch the tensors
        for i in range(0, len(paths), batch_size):
            batch_paths = paths[i:i+batch_size]
            batch_labels = labels[i:i+batch_size]
            
            tensors = []
            valid_labels = []
            batch_valid_paths = []
            
            for path, label in zip(batch_paths, batch_labels):
                try:
                    tensor = pipeline_func(path)
                    tensors.append(tensor[0]) # tensor is [1, 224, 224, 3], append [224, 224, 3]
                    valid_labels.append(label)
                    batch_valid_paths.append(path)
                except Exception as e:
                    print(f"Error processing {path}: {e}")
            
            if not tensors:
                continue
                
            batch_tensor = np.array(tensors)
            preds = self.model.predict(batch_tensor, verbose=0)
            
            for j, (pred, label, path) in enumerate(zip(preds, valid_labels, batch_valid_paths)):
                pred_idx = np.argmax(pred)
                conf = pred[pred_idx]
                
                y_true.append(label)
                y_pred.append(pred_idx)
                confidences.append(float(conf))
                
                if "14.jpg" in path and "real_2000" in path:
                    specific_14_conf = float(pred[self.class_names.index("real_2000")])
        
        end_time = time.time()
        
        # Calculate metrics
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        confidences = np.array(confidences)
        
        accuracy = np.mean(y_true == y_pred)
        
        # Binary stats (Genuine vs Counterfeit)
        true_is_genuine = np.array(["real_" in self.class_names[idx] for idx in y_true])
        pred_is_genuine = np.array(["real_" in self.class_names[idx] for idx in y_pred])
        
        false_genuines = np.sum((~true_is_genuine) & pred_is_genuine)
        false_counterfeits = np.sum(true_is_genuine & (~pred_is_genuine))
        
        # Confidence distribution
        below_80 = np.sum(confidences < 0.80) / len(confidences) * 100 if len(confidences) > 0 else 0
        above_80 = np.sum(confidences >= 0.80) / len(confidences) * 100 if len(confidences) > 0 else 0
        
        avg_conf = np.mean(confidences) if len(confidences) > 0 else 0
        min_conf = np.min(confidences) if len(confidences) > 0 else 0
        max_conf = np.max(confidences) if len(confidences) > 0 else 0
        
        # Precision, Recall, F1 for "Genuine" as positive class
        true_pos = np.sum(true_is_genuine & pred_is_genuine)
        false_pos = false_genuines
        false_neg = false_counterfeits
        
        precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
        recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "name": name,
            "total_samples": len(y_true),
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "average_confidence": float(avg_conf),
            "min_confidence": float(min_conf),
            "max_confidence": float(max_conf),
            "percentage_below_80": float(below_80),
            "percentage_above_80": float(above_80),
            "false_genuines": int(false_genuines),
            "false_counterfeits": int(false_counterfeits),
            "14_jpg_confidence": specific_14_conf,
            "processing_time_s": end_time - start_time
        }

    # Pipeline A: Current Production
    def pipeline_a_current_pil(self, path):
        pil_img = Image.open(path)
        pil_img = ImageOps.exif_transpose(pil_img)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        return self.preprocessor.normalize_for_cnn(pil_img)

    # Pipeline B: Pure Keras (baseline)
    def pipeline_b_pure_keras(self, path):
        img = tf.keras.utils.load_img(
            path,
            color_mode="rgb",
            target_size=(self.target_size, self.target_size),
            interpolation="nearest"
        )
        x = tf.keras.utils.img_to_array(img)
        return np.expand_dims(x, axis=0)

    # Pipeline C: Previous OpenCV (without deskew)
    def pipeline_c_opencv_no_deskew(self, path):
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb_img, (self.target_size, self.target_size), interpolation=cv2.INTER_LINEAR)
        img_array = np.array(resized, dtype=np.float32)
        return np.expand_dims(img_array, axis=0)

    # Pipeline D: OpenCV + Deskew
    def pipeline_d_opencv_with_deskew(self, path):
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        aligned_img = self.preprocessor.align_and_deskew(img)
        rgb_img = cv2.cvtColor(aligned_img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb_img, (self.target_size, self.target_size), interpolation=cv2.INTER_LINEAR)
        img_array = np.array(resized, dtype=np.float32)
        return np.expand_dims(img_array, axis=0)

def main():
    model_path = r"C:\PROJECTS\fakecurrency\backend\src\modules\ai_engine\models\checkpoints\stage2\best_stage2.keras"
    dataset_dir = r"C:\PROJECTS\fakecurrency\dataset\split\val"
    
    evaluator = PipelineEvaluator(model_path, dataset_dir)
    paths, labels = evaluator.get_image_paths()
    print(f"Found {len(paths)} validation images.")
    
    results = []
    
    # Run pipelines
    res_a = evaluator.evaluate_pipeline("Pipeline A (Current PIL)", evaluator.pipeline_a_current_pil, paths, labels)
    results.append(res_a)
    
    res_b = evaluator.evaluate_pipeline("Pipeline B (Pure Keras)", evaluator.pipeline_b_pure_keras, paths, labels)
    results.append(res_b)
    
    res_c = evaluator.evaluate_pipeline("Pipeline C (OpenCV No Deskew)", evaluator.pipeline_c_opencv_no_deskew, paths, labels)
    results.append(res_c)
    
    res_d = evaluator.evaluate_pipeline("Pipeline D (OpenCV + Deskew)", evaluator.pipeline_d_opencv_with_deskew, paths, labels)
    results.append(res_d)
    
    # Save results
    output_path = "pipeline_evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nEvaluation complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
