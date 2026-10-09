import tensorflow as tf
from src.modules.ai_engine.training.model_builder import ModelBuilder
from src.modules.ai_engine.training.config import training_config
import os
import numpy as np

def test_keras_load_img():
    model_path = r"C:\PROJECTS\fakecurrency\backend\src\modules\ai_engine\models\checkpoints\stage2\best_stage2.keras"
    model = tf.keras.models.load_model(model_path)
    
    img_path = r"c:\PROJECTS\fakecurrency\dataset\split\val\real_2000\14.jpg"
    
    # EXACT Keras flow_from_directory logic
    img = tf.keras.utils.load_img(
        img_path,
        color_mode="rgb",
        target_size=(224, 224),
        interpolation="nearest"
    )
    
    x = tf.keras.utils.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    
    predictions = model.predict(x, verbose=0)
    predicted_idx = np.argmax(predictions[0])
    confidence = predictions[0][predicted_idx]
    
    print(f"Keras load_img confidence: {confidence}")

if __name__ == "__main__":
    test_keras_load_img()
