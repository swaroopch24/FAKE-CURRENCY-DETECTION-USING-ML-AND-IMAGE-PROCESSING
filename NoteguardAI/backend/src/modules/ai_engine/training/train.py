import os
import argparse
import tensorflow as tf
from src.modules.ai_engine.training.config import training_config
from src.modules.ai_engine.training.trainer import NoteGuardModelTrainer
from src.modules.ai_engine.training.evaluate import ModelEvaluator

def set_seeds(seed: int = 42):
    """Sets random seeds to guarantee reproducibility during weights training."""
    import random
    import numpy as np
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)

def parse_args():
    parser = argparse.ArgumentParser(description="NoteGuard AI CNN Model Training Entrypoint")
    parser.add_argument("--data-dir", type=str, required=True, help="Directory containing train/val/test splits")
    parser.add_argument("--output-dir", type=str, default=training_config.OUTPUT_MODEL_DIR, help="Export path for final model weights")
    parser.add_argument("--seed", type=int, default=training_config.SEED, help="Random seed value")
    return parser.parse_args()

def main():
    args = parse_args()
    set_seeds(args.seed)

    print(f"=== Starting NoteGuard AI CNN Development Pipeline (Seed: {args.seed}) ===")
    print(f"Dataset path: {args.data_dir}")
    print(f"Export directory: {args.output_dir}")

    # Set paths in configuration
    training_config.DATASET_SPLITS_DIR = args.data_dir
    training_config.OUTPUT_MODEL_DIR = args.output_dir

    # Instantiate and execute training pipeline
    trainer = NoteGuardModelTrainer()
    model = trainer.execute_training(args.data_dir)

    # Save final model
    os.makedirs(args.output_dir, exist_ok=True)
    final_model_path = os.path.join(args.output_dir, "noteguard_final_mobilenetv2.h5")
    model.save(final_model_path)
    print(f"\nFinal training weights saved to: {final_model_path}")

    # Skipped test evaluation during Phase 28 Experiment 1 to protect the test set

    print("\nCNN development pipeline completed successfully.")

if __name__ == "__main__":
    main()
