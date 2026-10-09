import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

from src.modules.ai_engine.training.config import training_config

def build_data_pipelines(data_dir, batch_size=32):
    train_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(data_dir, "train"),
        labels="inferred",
        label_mode="categorical",
        class_names=training_config.CLASS_NAMES,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=True,
        seed=42
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(data_dir, "val"),
        labels="inferred",
        label_mode="categorical",
        class_names=training_config.CLASS_NAMES,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=False,
        seed=42
    )

    test_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(data_dir, "test"),
        labels="inferred",
        label_mode="categorical",
        class_names=training_config.CLASS_NAMES,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=False,
        seed=42
    )

    # Data augmentation pipeline using native TF ops (no scipy required)
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.08),
        layers.RandomTranslation(0.05, 0.05),
        layers.RandomZoom(0.08),
    ], name="data_augmentation")

    train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    test_ds = test_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds, test_ds

def build_production_model(num_classes=14):
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False

    inputs = layers.Input(shape=(224, 224, 3), name="input_image")
    # Preprocessing scaling layer for MobileNetV2 [-1, 1]
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="classification_head")(x)

    model = models.Model(inputs, outputs, name="NoteGuard_MobileNetV2")
    return model, base_model

def train_and_evaluate():
    print("=== NOTEGUARD AI: PRODUCTION MODEL TRAINING ON BALANCED DATASET ===")
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(project_root, "dataset", "split")
    
    target_model_path = os.path.join(
        training_config.BASE_DIR, 
        "models", 
        "evaluation", 
        "phase28_model_improvement", 
        "experiment_1_targeted_augmentation", 
        "stage2", 
        "best_stage2.keras"
    )
    os.makedirs(os.path.dirname(target_model_path), exist_ok=True)

    train_ds, val_ds, test_ds = build_data_pipelines(data_dir, batch_size=32)

    model, base_model = build_production_model(num_classes=len(training_config.CLASS_NAMES))

    # --- STAGE 1: Top layers ---
    print("\n--- STAGE 1: FEATURE EXTRACTOR TRAINING (12 Epochs) ---")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    callbacks_s1 = [
        EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=2, min_lr=1e-6, verbose=1)
    ]

    history_s1 = model.fit(
        train_ds,
        epochs=12,
        validation_data=val_ds,
        callbacks=callbacks_s1,
        verbose=1
    )

    # --- STAGE 2: Fine-Tuning ---
    print("\n--- STAGE 2: FINE-TUNING BASE LAYERS (18 Epochs) ---")
    base_model.trainable = True
    for layer in base_model.layers[:100]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=2e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    callbacks_s2 = [
        ModelCheckpoint(filepath=target_model_path, monitor="val_loss", save_best_only=True, verbose=1),
        EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=2, min_lr=1e-7, verbose=1)
    ]

    history_s2 = model.fit(
        train_ds,
        epochs=18,
        validation_data=val_ds,
        callbacks=callbacks_s2,
        verbose=1
    )

    model.save(target_model_path)
    print(f"\nProduction model successfully saved to: {target_model_path}")

    # --- STAGE 3: Final Test Evaluation ---
    print("\n=== EVALUATING ON UNSEEN 488-IMAGE TEST SET ===")
    y_trues = []
    y_preds = []
    
    for batch_x, batch_y in test_ds:
        preds = model.predict(batch_x, verbose=0)
        y_preds.extend(np.argmax(preds, axis=1))
        y_trues.extend(np.argmax(batch_y.numpy(), axis=1))

    y_true = np.array(y_trues)
    y_pred = np.array(y_preds)

    acc_14 = np.mean(y_true == y_pred)
    print(f"\n14-Class Test Accuracy: {acc_14:.2%}")

    # Authenticity
    true_auth = np.array(["real_" in training_config.CLASS_NAMES[i] for i in y_true])
    pred_auth = np.array(["real_" in training_config.CLASS_NAMES[i] for i in y_pred])
    auth_acc = np.mean(true_auth == pred_auth)
    false_reals = int(np.sum((~true_auth) & pred_auth))
    false_fakes = int(np.sum(true_auth & (~pred_auth)))

    print(f"Authenticity Accuracy:  {auth_acc:.2%}")
    print(f"False-REAL Count:       {false_reals}")
    print(f"False-FAKE Count:       {false_fakes}")

    # Denomination
    true_denom = np.array([training_config.CLASS_NAMES[i].split("_")[1] for i in y_true])
    pred_denom = np.array([training_config.CLASS_NAMES[i].split("_")[1] for i in y_pred])
    denom_acc = np.mean(true_denom == pred_denom)
    print(f"Denomination Accuracy:  {denom_acc:.2%}")

    print("\nPer-Class Accuracy:")
    for idx, cname in enumerate(training_config.CLASS_NAMES):
        mask = (y_true == idx)
        if np.sum(mask) > 0:
            c_acc = np.mean(y_pred[mask] == idx)
            print(f"  {cname:12s}: {c_acc:.2%} ({np.sum(y_pred[mask] == idx)}/{np.sum(mask)})")

    # Clear ModelLoader cache
    from src.modules.ai_engine.loaders import ModelLoader
    ModelLoader().clear_model()
    print("\nModelLoader cached instance reset. Live API is now powered by the new trained weights!")

if __name__ == "__main__":
    train_and_evaluate()
