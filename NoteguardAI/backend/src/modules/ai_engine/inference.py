import threading
import numpy as np
from src.modules.ai_engine.loaders import ModelLoader, pip_lock
from src.modules.ai_engine.exceptions import InferenceException
from src.modules.ai_engine.training.config import training_config

class AIInferenceService:
    """
    Thread-safe, lazy-initialized CNN inference executor.
    Runs predictions on preprocessed image tensors, calculating raw probabilities.
    """
    def __init__(self, model_path: str = None):
        self.model_loader = ModelLoader()
        self.model_path = model_path
        # Re-use the import-level lock for prediction safety
        self.lock = pip_lock
        
    def _get_active_model(self):
        """Lazy model loading wrapper."""
        return self.model_loader.load_model(self.model_path)

    def execute_prediction(self, preprocessed_tensor: np.ndarray) -> dict:
        """
        Executes model predict pipeline inside a thread-safe context.
        Returns the raw prediction data for the DecisionEngine to process.
        """
        model = self._get_active_model()

        with self.lock:
            try:
                # Run the prediction
                predictions = model.predict(preprocessed_tensor, verbose=0)
            except Exception as e:
                raise InferenceException(f"TensorFlow execution failure: {str(e)}")

        probabilities = predictions[0]
        max_idx = np.argmax(probabilities)
        pred_label = training_config.CLASSES[max_idx] if hasattr(training_config, "CLASSES") else training_config.CLASS_NAMES[max_idx]
        confidence = float(probabilities[max_idx])
        
        # Binary authenticities
        p_real = sum(float(p) for i, p in enumerate(probabilities) if "real" in (training_config.CLASSES[i] if hasattr(training_config, "CLASSES") else training_config.CLASS_NAMES[i]))
        p_fake = sum(float(p) for i, p in enumerate(probabilities) if "fake" in (training_config.CLASSES[i] if hasattr(training_config, "CLASSES") else training_config.CLASS_NAMES[i]))

        return {
            "class_label": pred_label,
            "confidence": confidence,
            "p_real": p_real,
            "p_fake": p_fake,
            "raw_probabilities": probabilities.tolist()
        }
