import numpy as np
import tensorflow as tf
from src.modules.ai_engine.training.config import training_config
import cv2

class ModelPredictor:
    """
    Executes single-image CNN model inference, computing classification scores 
    and Top-K confidence matrices. Used during development and validation.
    """
    def __init__(self, model_path: str):
        self.config = training_config
        self.model = tf.keras.models.load_model(model_path)

    def preprocess_image(self, file_path: str) -> np.ndarray:
        """Loads and resizes an image file to match MobileNetV2 input dimensions."""
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError(f"Could not load image: {file_path}")
            
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.config.IMAGE_SIZE, self.config.IMAGE_SIZE))
        
        # Add batch dimension
        img_array = np.expand_dims(img, axis=0).astype(np.float32)
        return img_array

    def predict_image(self, file_path: str, top_k: int = 3) -> dict:
        """
        Runs inference on an image and returns predictions.
        """
        img_tensor = self.preprocess_image(file_path)
        predictions = self.model.predict(img_tensor)
        
        probabilities = predictions[0]
        max_idx = np.argmax(probabilities)
        pred_label = self.config.CLASS_NAMES[max_idx]
        confidence = float(probabilities[max_idx])
        
        # Parse authenticity and denomination from class label string
        is_authentic = "real" in pred_label
        denomination_str = pred_label.split("_")[-1]
        denomination = int(denomination_str) if denomination_str.isdigit() else 0

        # Calculate Top-K
        top_k_indices = np.argsort(probabilities)[::-1][:top_k]
        top_k_predictions = [
            {
                "class_label": self.config.CLASS_NAMES[idx],
                "confidence": float(probabilities[idx])
            }
            for idx in top_k_indices
        ]

        return {
            "prediction": {
                "class_label": pred_label,
                "is_authentic": is_authentic,
                "denomination": denomination,
                "confidence": confidence
            },
            "top_k_predictions": top_k_predictions
        }
