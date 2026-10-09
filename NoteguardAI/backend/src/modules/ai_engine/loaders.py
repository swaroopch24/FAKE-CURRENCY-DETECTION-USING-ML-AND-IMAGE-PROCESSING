import os
import threading
from src.modules.ai_engine.exceptions import ModelLoadException
from src.config import settings

class ModelLoader:
    """
    Thread-safe, lazy model loading wrapper.
    Caches model instances in memory and validates model health status.
    """
    _instance = None
    _lock = threading.Lock()
    _model = None

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelLoader, cls).__new__(cls)
            return cls._instance

    def load_model(self, model_path: str = None) -> "tf.keras.models.Model":
        """
        Thread-safe, lazy model loading function.
        Loads the model if it hasn't been cached, using double-checked locking.
        """
        if self._model is not None:
            return self._model

        with self._lock:
            # Double-check
            if self._model is not None:
                return self._model

            # Resolve default model weights path if not provided
            if model_path is None:
                from src.modules.ai_engine.training.config import training_config
                model_path = os.path.join(
                    training_config.BASE_DIR, 
                    "models", 
                    "evaluation", 
                    "phase28_model_improvement", 
                    "experiment_1_targeted_augmentation", 
                    "stage2", 
                    "best_stage2.keras"
                )

            # Fallback path logic in case final model doesn't exist yet
            if not os.path.exists(model_path):
                raise ModelLoadException(
                    f"Target CNN model weights file not found at: {model_path}. "
                    "This checkpoint is locked and must exist for Phase 18 inference."
                )

            try:
                import tensorflow as tf
            except ImportError:
                raise ModelLoadException(
                    "TensorFlow is not installed in the current environment. "
                    "Cannot load CNN weights in mock mode."
                )

            try:
                print(f"Loading NoteGuard AI Model from {model_path}...")
                # Load Keras model into memory
                self._model = tf.keras.models.load_model(model_path)
                print("Model loaded successfully.")
                return self._model
            except Exception as e:
                raise ModelLoadException(f"Failed to load TensorFlow model structure: {str(e)}")

    def is_loaded(self) -> bool:
        """Checks model availability state."""
        return self._model is not None

    def clear_model(self):
        """Clears cached model weights (e.g. for reloading or memory cleanup)."""
        with self._lock:
            self._model = None
            print("Model weights unloaded from memory.")
            
    def get_metadata(self) -> dict:
        """Returns metadata about the active model."""
        if not self.is_loaded():
            return {"status": "unloaded"}
        return {
            "status": "loaded",
            "model_name": "NoteGuard_MobileNetV2",
            "input_shape": list(self._model.input_shape),
            "output_classes_count": self._model.output_shape[-1]
        }
pip_lock = threading.Lock()
