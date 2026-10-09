import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from src.modules.ai_engine.training.config import training_config

class ModelBuilder:
    """
    Builds and compiles MobileNetV2 Transfer Learning configurations.
    """
    @staticmethod
    def build_transfer_model(
        input_shape: tuple[int, int, int] = (224, 224, 3),
        num_classes: int = 14,
        learning_rate: float = 1e-3
    ) -> models.Model:
        """
        Builds the base MobileNetV2 network, freezes base weights, and attaches 
        a high-density classification head.
        """
        # Base model loading with frozen pre-trained weights
        base_model = MobileNetV2(
            input_shape=input_shape,
            include_top=False,
            weights="imagenet"
        )
        base_model.trainable = False

        # Build network pipeline
        inputs = layers.Input(shape=input_shape)
        
        # Preprocessing scaling layer required for MobileNetV2 [-1, 1] range
        x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
        
        x = base_model(x, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(256, activation="relu")(x)
        x = layers.Dropout(0.5)(x)  # Strong dropout to mitigate overfitting on fakes
        
        # Softmax outputs matching 14 target categories
        outputs = layers.Dense(num_classes, activation="softmax", name="classification_head")(x)
        
        model = models.Model(inputs, outputs, name="NoteGuard_MobileNetV2")
        
        # Compile
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss="categorical_crossentropy",
            metrics=["accuracy", tf.keras.metrics.Precision(name="precision"), tf.keras.metrics.Recall(name="recall")]
        )
        
        return model

    @staticmethod
    def setup_fine_tuning(
        model: models.Model,
        fine_tune_at: int = 100,
        learning_rate: float = 1e-5
    ) -> models.Model:
        """
        Unfreezes base network layers beyond the specified index to run fine-tuning.
        """
        # Safely find the base model in the layers hierarchy
        base_model = None
        for layer in model.layers:
            if hasattr(layer, 'layers'):  # Identifies the nested functional model (MobileNetV2)
                base_model = layer
                break
                
        if not base_model:
            raise ValueError("Could not find the base model for fine tuning.")
            
        base_model.trainable = True
        
        # Freeze all layers up to fine_tune_at
        for layer in base_model.layers[:fine_tune_at]:
            layer.trainable = False
            
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss="categorical_crossentropy",
            metrics=["accuracy", tf.keras.metrics.Precision(name="precision"), tf.keras.metrics.Recall(name="recall")]
        )
        return model
