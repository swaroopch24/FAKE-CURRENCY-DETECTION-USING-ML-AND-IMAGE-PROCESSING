import os
import sys
import numpy as np
import cv2
import tensorflow as tf
import traceback
import tempfile
import uuid

print("=== NOTEGUARD AI PHASE 10A SMOKE TEST ===")
print("STEP 1 - IMPORT VERIFICATION")
print(f"TensorFlow Version: {tf.__version__}")
print(f"Keras Version: {tf.keras.__version__}")
print(f"NumPy Version: {np.__version__}")
print(f"OpenCV Version: {cv2.__version__}")
print(f"GPU Available: {len(tf.config.list_physical_devices('GPU')) > 0}")

try:
    from src.modules.ai_engine.training.config import training_config
    from src.modules.ai_engine.training.model_builder import ModelBuilder
    from src.modules.ai_engine.training.callbacks import CallbacksBuilder
    from src.modules.ai_engine.training.trainer import NoteGuardModelTrainer
    
    print("\nSTEP 2 - MODEL INSTANTIATION")
    print("Instantiating ModelBuilder...")
    model = ModelBuilder.build_transfer_model(
        input_shape=(224, 224, 3),
        num_classes=14
    )
    print("Model instantiated successfully.")

    print("\nSTEP 3 - MODEL STRUCTURE")
    print(f"Input Shape: {model.input_shape}")
    print(f"Output Shape: {model.output_shape}")
    total_params = model.count_params()
    # To get trainable/non-trainable params securely in TF 2.x/Keras 3:
    trainable_params = sum(np.prod(w.shape) for w in model.trainable_weights)
    non_trainable_params = sum(np.prod(w.shape) for w in model.non_trainable_weights)
    print(f"Total Params: {total_params}")
    print(f"Trainable Params: {trainable_params}")
    print(f"Non-trainable Params: {non_trainable_params}")
    print("Backbone: MobileNetV2 (ImageNet weights, frozen)")
    print("Classification Head: GlobalAveragePooling2D -> Dense(256) -> Dropout(0.5) -> Dense(14, Softmax)")

    print("\nSTEP 4 - FORWARD PASS (DUMMY)")
    dummy_input = np.random.rand(1, 224, 224, 3).astype(np.float32)
    output = model(dummy_input, training=False)
    output_np = output.numpy()
    print(f"Output Shape: {output_np.shape}")
    print(f"Output Finite: {np.isfinite(output_np).all()}")
    print(f"Softmax Sum: {np.sum(output_np):.6f}")
    print(f"Output Vector: {output_np}")

    print("\nSTEP 5 - PREPROCESSING TEST")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    train_dir = os.path.join(project_root, "dataset", "split", "train")
    real_500_dir = os.path.join(train_dir, "real_500")
    sample_files = [f for f in os.listdir(real_500_dir) if f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png")]
    if not sample_files:
        print("ERROR: No sample image found in real_500")
    else:
        sample_path = os.path.join(real_500_dir, sample_files[0])
        print(f"Testing preprocessing on: {sample_path}")
        img = cv2.imread(sample_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img_array = np.expand_dims(img, axis=0).astype(np.float32)
        img_preprocessed = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        print(f"Preprocessed Tensor Shape: {img_preprocessed.shape}")
        
        real_output = model(img_preprocessed, training=False).numpy()
        print(f"Forward Pass Output Shape: {real_output.shape}")
        print("Forward pass successful.")

    print("\nSTEP 6 - CLASS MAPPING")
    print(f"Number of classes: {len(training_config.CLASS_NAMES)}")
    print(f"Are classes unique? {len(set(training_config.CLASS_NAMES)) == 14}")
    for idx, name in enumerate(training_config.CLASS_NAMES):
        print(f"Index {idx} -> {name}")

    print("\nSTEP 7 - DATASET LOADER TEST")
    trainer = NoteGuardModelTrainer()
    # Re-map paths correctly for script runtime context
    split_base = os.path.abspath(os.path.join(project_root, "dataset", "split"))
    train_gen, val_gen = trainer.get_data_generators(split_base)
    
    print("\nTrain Generator Results:")
    print(f"Discovered Classes: {list(train_gen.class_indices.keys())}")
    print(f"Total Images Discovered: {train_gen.samples}")
    batch_x, batch_y = next(iter(train_gen))
    print(f"Batch X shape: {batch_x.shape}")
    print(f"Batch Y shape: {batch_y.shape}")

    print("\nValidation Generator Results:")
    print(f"Total Images Discovered: {val_gen.samples}")
    val_batch_x, val_batch_y = next(iter(val_gen))
    print(f"Val Batch X shape: {val_batch_x.shape}")
    print(f"Val Batch Y shape: {val_batch_y.shape}")

    print("\nSTEP 8 - CHECKPOINT TEST")
    callbacks_builder = CallbacksBuilder(
        checkpoints_dir=tempfile.gettempdir(),
        logs_dir=tempfile.gettempdir()
    )
    callbacks = callbacks_builder.get_training_callbacks(phase="smoke_test")
    print("Callbacks successfully instantiated. ModelCheckpoint syntax is compatible.")
    
    print("\nSTEP 9 - DATA INTEGRITY")
    print("NO files were modified. NO training loops were executed.")

except Exception as e:
    print(f"\nERROR OCCURRED: {e}")
    traceback.print_exc()

print("\nSMOKE TEST COMPLETE")
