import os
import json
from src.modules.ai_engine.training.trainer import NoteGuardModelTrainer
from src.modules.ai_engine.training.model_builder import ModelBuilder
from src.modules.ai_engine.training.config import training_config
import tensorflow as tf

def run_stage2():
    print("=== NOTEGUARD AI: PHASE 10B - STAGE 2 FINE TUNING ===")
    trainer = NoteGuardModelTrainer()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    split_base = os.path.join(project_root, "dataset", "split")
    
    train_gen, val_gen = trainer.get_data_generators(split_base)
    
    # Load best stage 1 model
    stage1_model_path = os.path.join(training_config.OUTPUT_MODEL_DIR, "stage1", "best_stage1.keras")
    if not os.path.exists(stage1_model_path):
        print(f"ERROR: Stage 1 model not found at {stage1_model_path}")
        return
        
    print(f"Loading Stage 1 model from {stage1_model_path}")
    model = tf.keras.models.load_model(stage1_model_path)
    
    print(f"Unfreezing layers past {training_config.FINE_TUNE_AT}...")
    model = ModelBuilder.setup_fine_tuning(
        model=model,
        fine_tune_at=training_config.FINE_TUNE_AT,
        learning_rate=1e-5
    )
    
    callbacks_p2 = trainer.callbacks_builder.get_training_callbacks(phase="fine_tuning", stage_name="stage2")
    
    # We will assume Stage 1 finished at epoch ~N, but for Keras history we can just start at 0 for Stage 2 
    # to avoid plotting issues, or just resume. We'll start at 0 for simplicity.
    history_s2 = model.fit(
        train_gen,
        epochs=20,
        validation_data=val_gen,
        callbacks=callbacks_p2,
        verbose=1
    )
    
    history_data = {"stage2": history_s2.history}
    for metric, values in history_data["stage2"].items():
        history_data["stage2"][metric] = [float(v) for v in values]
        
    history_file = os.path.join(training_config.LOGS_DIR, "training_history_stage2.json")
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    with open(history_file, 'w') as f:
        json.dump(history_data, f, indent=4)
        
    print(f"\nStage 2 complete! History saved to {history_file}")

if __name__ == "__main__":
    run_stage2()
