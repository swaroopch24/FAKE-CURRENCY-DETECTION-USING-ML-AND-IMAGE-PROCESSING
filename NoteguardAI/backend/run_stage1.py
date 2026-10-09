import os
import json
from src.modules.ai_engine.training.trainer import NoteGuardModelTrainer
from src.modules.ai_engine.training.model_builder import ModelBuilder
from src.modules.ai_engine.training.config import training_config

def run_stage1():
    print("=== NOTEGUARD AI: PHASE 10B - STAGE 1 TRAINING ===")
    trainer = NoteGuardModelTrainer()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    split_base = os.path.join(project_root, "dataset", "split")
    
    train_gen, val_gen = trainer.get_data_generators(split_base)
    
    model = ModelBuilder.build_transfer_model(
        input_shape=(224, 224, 3),
        num_classes=14,
        learning_rate=1e-3
    )
    
    callbacks_p1 = trainer.callbacks_builder.get_training_callbacks(phase="feature_extractor", stage_name="stage1")
    
    history_s1 = model.fit(
        train_gen,
        epochs=20,
        validation_data=val_gen,
        callbacks=callbacks_p1,
        verbose=1
    )
    
    history_data = {"stage1": history_s1.history}
    for metric, values in history_data["stage1"].items():
        history_data["stage1"][metric] = [float(v) for v in values]
        
    history_file = os.path.join(training_config.LOGS_DIR, "training_history_stage1.json")
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    with open(history_file, 'w') as f:
        json.dump(history_data, f, indent=4)
        
    print(f"\nStage 1 complete! History saved to {history_file}")

if __name__ == "__main__":
    run_stage1()
