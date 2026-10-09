import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from src.modules.ai_engine.training.config import training_config
from src.modules.ai_engine.training.model_builder import ModelBuilder
from src.modules.ai_engine.training.callbacks import CallbacksBuilder

class NoteGuardModelTrainer:
    """
    Executes MobileNetV2 CNN training routines, loading partition datasets,
    running transfer learning runs, and fine-tuning configurations.
    """
    def __init__(self):
        self.config = training_config
        self.callbacks_builder = CallbacksBuilder()

    def get_data_generators(self, data_dir: str):
        """
        Creates training and validation data generators using standard Keras pipelines.
        """
        # MobileNetV2 preprocessing is applied directly inside the model's lambda layer,
        # so generators only scale pixel matrices to normal ranges [0, 1] if not handled.
        # However, MobileNetV2 expects [-1, 1], which ModelBuilder handles.
        # Thus, generators only load images.
        train_datagen = ImageDataGenerator(
            rotation_range=15,
            brightness_range=[0.8, 1.2],
            width_shift_range=0.05,
            height_shift_range=0.05,
            fill_mode="nearest"
        )
        val_datagen = ImageDataGenerator()

        train_generator = train_datagen.flow_from_directory(
            directory=os.path.join(data_dir, "train"),
            target_size=(self.config.IMAGE_SIZE, self.config.IMAGE_SIZE),
            batch_size=self.config.BATCH_SIZE,
            class_mode="categorical",
            classes=self.config.CLASS_NAMES,
            seed=self.config.SEED,
            shuffle=True
        )

        val_generator = val_datagen.flow_from_directory(
            directory=os.path.join(data_dir, "val"),
            target_size=(self.config.IMAGE_SIZE, self.config.IMAGE_SIZE),
            batch_size=self.config.BATCH_SIZE,
            class_mode="categorical",
            classes=self.config.CLASS_NAMES,
            seed=self.config.SEED,
            shuffle=False
        )

        return train_generator, val_generator

    def execute_training(self, data_dir: str) -> tf.keras.models.Model:
        """
        Runs the complete two-phase training lifecycle:
        1. Feature Extractor Training (Top layers only)
        2. Fine-Tuning base MobileNetV2 layers
        """
        train_gen, val_gen = self.get_data_generators(data_dir)
        
        print("\n=== Stage 1: Initializing Base CNN Model ===")
        model = ModelBuilder.build_transfer_model(
            input_shape=(self.config.IMAGE_SIZE, self.config.IMAGE_SIZE, self.config.CHANNELS),
            num_classes=self.config.NUM_CLASSES,
            learning_rate=self.config.INITIAL_LEARNING_RATE
        )
        model.summary()

        print("\n=== Stage 2: Training Feature Extractor (Frozen Base) ===")
        callbacks_p1 = self.callbacks_builder.get_training_callbacks(phase="feature_extractor", stage_name="stage1")
        
        history_s1 = model.fit(
            train_gen,
            epochs=self.config.INITIAL_EPOCHS,
            validation_data=val_gen,
            callbacks=callbacks_p1,
            verbose=1
        )

        print("\n=== Stage 3: Unfreezing Base Layers for Fine-Tuning ===")
        model = ModelBuilder.setup_fine_tuning(
            model=model,
            fine_tune_at=self.config.FINE_TUNE_AT,
            learning_rate=self.config.FINE_TUNE_LEARNING_RATE
        )
        model.summary()

        print("\n=== Stage 4: Executing Fine-Tuning ===")
        callbacks_p2 = self.callbacks_builder.get_training_callbacks(phase="fine_tuning", stage_name="stage2")
        
        history_s2 = model.fit(
            train_gen,
            epochs=self.config.INITIAL_EPOCHS + self.config.FINE_TUNE_EPOCHS,
            initial_epoch=self.config.INITIAL_EPOCHS,
            validation_data=val_gen,
            callbacks=callbacks_p2,
            verbose=1
        )
        
        print("\n=== Stage 5: Saving Training History ===")
        import json
        history_data = {
            "stage1": history_s1.history,
            "stage2": history_s2.history
        }
        
        # Convert numpy types to native Python floats for JSON serialization
        for stage in history_data:
            for metric, values in history_data[stage].items():
                history_data[stage][metric] = [float(v) for v in values]
                
        history_file = os.path.join(self.config.LOGS_DIR, "training_history.json")
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=4)
        print(f"Training history saved to {history_file}")

        return model
