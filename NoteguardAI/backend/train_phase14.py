import os
import glob
import math
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.utils.class_weight import compute_class_weight
import json

BASE_DATA_DIR = os.path.join("C:\\PROJECTS\\fakecurrency\\dataset\\split")
OUTPUT_CHECKPOINT_DIR = os.path.join("C:\\PROJECTS\\fakecurrency\\backend\\src\\modules\\ai_engine\\models\\checkpoints\\phase14_denomination")
OUTPUT_LOG_DIR = os.path.join("C:\\PROJECTS\\fakecurrency\\backend\\src\\modules\\ai_engine\\models\\logs\\phase14_denomination")

os.makedirs(OUTPUT_CHECKPOINT_DIR, exist_ok=True)
os.makedirs(OUTPUT_LOG_DIR, exist_ok=True)

DENOM_CLASSES = [
    "denom_10", "denom_20", "denom_50", "denom_100",
    "denom_200", "denom_500", "denom_2000"
]
DENOM_TO_IDX = {denom: idx for idx, denom in enumerate(DENOM_CLASSES)}

class DenominationDataGenerator(tf.keras.utils.Sequence):
    def __init__(self, split_name, batch_size=32, target_size=(224, 224), augment=False, shuffle=True):
        self.split_name = split_name
        self.batch_size = batch_size
        self.target_size = target_size
        self.augment = augment
        self.shuffle = shuffle
        
        self.datagen = None
        if self.augment:
            self.datagen = ImageDataGenerator(
                brightness_range=[0.8, 1.2],
                rotation_range=15,
                width_shift_range=0.1,
                height_shift_range=0.1,
                zoom_range=0.1
            )
            
        self.samples = []
        self._load_manifest()
        
        if self.shuffle:
            np.random.shuffle(self.samples)

    def _load_manifest(self):
        split_dir = os.path.join(BASE_DATA_DIR, self.split_name)
        for class_folder in os.listdir(split_dir):
            class_path = os.path.join(split_dir, class_folder)
            if os.path.isdir(class_path):
                denom = class_folder.split("_")[-1]
                mapped_label = f"denom_{denom}"
                class_idx = DENOM_TO_IDX[mapped_label]
                for img_file in os.listdir(class_path):
                    if img_file.endswith(('.jpg', '.png', '.jpeg')):
                        self.samples.append({
                            "filename": os.path.join(class_path, img_file),
                            "class_idx": class_idx,
                            "label_name": mapped_label
                        })

    def __len__(self):
        return math.ceil(len(self.samples) / self.batch_size)
        
    def __getitem__(self, idx):
        batch_samples = self.samples[idx * self.batch_size:(idx + 1) * self.batch_size]
        
        batch_x = []
        batch_y = []
        
        for sample in batch_samples:
            img = tf.keras.preprocessing.image.load_img(sample["filename"], target_size=self.target_size)
            img = tf.keras.preprocessing.image.img_to_array(img)
            
            if self.augment and self.datagen:
                img = self.datagen.random_transform(img)
                
            batch_x.append(img)
            batch_y.append(sample["class_idx"])
            
        batch_x = np.array(batch_x, dtype=np.float32)
        batch_y = tf.keras.utils.to_categorical(batch_y, num_classes=len(DENOM_CLASSES))
        
        return batch_x, batch_y

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.samples)
            
    def get_classes(self):
        return np.array([s["class_idx"] for s in self.samples])

    def print_counts(self):
        counts = {}
        for s in self.samples:
            counts[s["label_name"]] = counts.get(s["label_name"], 0) + 1
        print(f"[{self.split_name.upper()} Counts]")
        for c in DENOM_CLASSES:
            print(f"  {c}: {counts.get(c, 0)}")

def build_denomination_model():
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False
    
    inputs = tf.keras.Input(shape=(224, 224, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    outputs = tf.keras.layers.Dense(7, activation='softmax')(x)
    
    model = tf.keras.Model(inputs, outputs)
    return model, base_model

def get_callbacks(stage_name):
    checkpoint = ModelCheckpoint(
        filepath=os.path.join(OUTPUT_CHECKPOINT_DIR, f"best_{stage_name}_denomination.keras"),
        monitor='val_loss',
        save_best_only=True,
        verbose=1
    )
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=8 if stage_name == 'stage1' else 12,
        restore_best_weights=True,
        verbose=1
    )
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=3 if stage_name == 'stage1' else 5,
        min_lr=1e-7,
        verbose=1
    )
    return [checkpoint, early_stop, reduce_lr]

def run_training():
    print("=== NOTEGUARD AI PHASE 14 DENOMINATION TRAINING ===")
    
    train_gen = DenominationDataGenerator("train", batch_size=32, augment=True, shuffle=True)
    val_gen = DenominationDataGenerator("val", batch_size=32, augment=False, shuffle=False)
    test_gen = DenominationDataGenerator("test", batch_size=32, augment=False, shuffle=False)
    
    train_gen.print_counts()
    val_gen.print_counts()
    test_gen.print_counts()
    
    y_train = train_gen.get_classes()
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(y_train),
        y=y_train
    )
    class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
    print("\n[Class Weights]")
    for i, w in class_weight_dict.items():
        print(f"{DENOM_CLASSES[i]}: {w:.3f}")
        
    print("\n--- STAGE 1: FROZEN BACKBONE ---")
    model, base_model = build_denomination_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history_s1 = model.fit(
        train_gen,
        epochs=30,
        validation_data=val_gen,
        class_weight=class_weight_dict,
        callbacks=get_callbacks('stage1'),
        verbose=1
    )
    
    print("\n--- STAGE 2: FINE TUNING ---")
    base_model.trainable = True
    for layer in base_model.layers[:100]:
        layer.trainable = False
        
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history_s2 = model.fit(
        train_gen,
        epochs=40,
        initial_epoch=len(history_s1.history['loss']),
        validation_data=val_gen,
        class_weight=class_weight_dict,
        callbacks=get_callbacks('stage2'),
        verbose=1
    )
    
    history_data = {
        "stage1": history_s1.history,
        "stage2": history_s2.history
    }
    for stage in history_data:
        for metric, values in history_data[stage].items():
            history_data[stage][metric] = [float(v) for v in values]
            
    history_file = os.path.join(OUTPUT_LOG_DIR, "training_history.json")
    with open(history_file, 'w') as f:
        json.dump(history_data, f, indent=4)
        
    print("\nTraining Complete.")

if __name__ == "__main__":
    run_training()
