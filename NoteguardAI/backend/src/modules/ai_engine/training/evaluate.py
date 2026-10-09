import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from src.modules.ai_engine.training.config import training_config
from src.modules.ai_engine.training.metrics import ModelEvaluatorMetrics

class ModelEvaluator:
    """
    Runs metrics evaluation against test datasets and exports validation reports.
    """
    def __init__(self):
        self.config = training_config

    def evaluate_test_set(self, model: tf.keras.models.Model, data_dir: str) -> dict:
        """
        Runs predictions on the test set partition and computes detailed metrics.
        """
        test_datagen = ImageDataGenerator()
        test_generator = test_datagen.flow_from_directory(
            directory=os.path.join(data_dir, "test"),
            target_size=(self.config.IMAGE_SIZE, self.config.IMAGE_SIZE),
            batch_size=self.config.BATCH_SIZE,
            class_mode="categorical",
            classes=self.config.CLASS_NAMES,
            seed=self.config.SEED,
            shuffle=False
        )

        print("\n=== Running Predictions on Test Dataset ===")
        predictions = model.predict(test_generator, verbose=1)
        y_pred = np.argmax(predictions, axis=1)
        y_true = test_generator.classes

        # Calculate metrics using Evaluator helper class
        metrics = ModelEvaluatorMetrics.calculate_classification_metrics(y_true, y_pred)
        cm = ModelEvaluatorMetrics.generate_confusion_matrix(y_true, y_pred, self.config.NUM_CLASSES)
        
        # Add confusion matrix table to report payload
        metrics["confusion_matrix"] = cm.tolist()
        metrics["classes_evaluated"] = self.config.CLASS_NAMES

        return metrics

    def save_evaluation_report(self, metrics: dict, output_path: str):
        """Saves generated classification matrix to disk as JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(metrics, f, indent=4)
        print(f"Evaluation report registered at {output_path}")
        
    @staticmethod
    def load_saved_model(model_path: str) -> tf.keras.models.Model:
        """Helper to load standard Keras weight configurations."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        return tf.keras.models.load_model(model_path)
