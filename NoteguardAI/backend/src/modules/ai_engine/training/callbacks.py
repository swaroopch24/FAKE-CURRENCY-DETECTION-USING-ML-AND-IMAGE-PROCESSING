import os
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard
from src.modules.ai_engine.training.config import training_config

class CallbacksBuilder:
    """
    Constructs standard Keras callback queues for training stability and monitoring.
    """
    def __init__(self, checkpoints_dir: str = None, logs_dir: str = None):
        self.checkpoints_dir = checkpoints_dir or training_config.OUTPUT_MODEL_DIR
        self.logs_dir = logs_dir or training_config.LOGS_DIR
        
        os.makedirs(self.checkpoints_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def get_training_callbacks(self, phase: str = "feature_extractor", stage_name: str = "stage1") -> list:
        """
        Creates callbacks configuration.
        """
        stage_dir = os.path.join(self.checkpoints_dir, stage_name)
        os.makedirs(stage_dir, exist_ok=True)
        
        # Save explicitly named checkpoint
        checkpoint_path = os.path.join(stage_dir, f"best_{stage_name}.keras")

        callbacks = [
            # Checkpoint callback saving only when val loss improves
            ModelCheckpoint(
                filepath=checkpoint_path,
                monitor="val_loss",
                save_best_only=True,
                mode="min",
                verbose=1
            ),
            # Early stopping to check overfitting
            EarlyStopping(
                monitor="val_loss",
                patience=5 if phase == "feature_extractor" else 7,
                restore_best_weights=True,
                verbose=1
            ),
            # Auto learning rate reduction
            ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.2,
                patience=3,
                min_lr=1e-6,
                verbose=1
            ),
            # TensorBoard logging metrics hook
            TensorBoard(
                log_dir=os.path.join(self.logs_dir, phase),
                histogram_freq=1,
                update_freq="epoch"
            )
        ]
        return callbacks
