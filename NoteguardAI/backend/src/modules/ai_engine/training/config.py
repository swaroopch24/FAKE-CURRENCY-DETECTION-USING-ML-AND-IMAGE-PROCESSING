import os

class TrainingConfig:
    """
    Hyperparameter and path configurations for NoteGuard AI CNN Model Training.
    """
    # Image constraints
    IMAGE_SIZE: int = 224  # MobileNetV2 standard input size
    CHANNELS: int = 3
    
    # --- PHASE 9 ARCHITECTURE REDESIGN ---
    
    # Denominations strictly used for binary authenticity training
    SUPPORTED_AUTHENTICITY_DENOMINATIONS: list[str] = ["10", "20", "50", "100", "200", "500", "2000"]
    
    # Denominations excluded from authenticity training (None at this phase)
    EXCLUDED_FROM_AUTHENTICITY: list[str] = []
    
    # Special status markers for downstream inference logic
    SPECIAL_STATUS_DENOMINATIONS: dict = {
        "2000": "withdrawn_from_circulation"
    }
    
    # Future feature-analysis dataset markers
    FEATURE_ANALYSIS_DATASETS: list[str] = ["features"]
    
    # Model target classes explicitly and deterministically defined (14 classes)
    CLASS_NAMES: list[str] = [
        "fake_10",
        "fake_20",
        "fake_50",
        "fake_100",
        "fake_200",
        "fake_500",
        "fake_2000",
        "real_10",
        "real_20",
        "real_50",
        "real_100",
        "real_200",
        "real_500",
        "real_2000"
    ]
    
    NUM_CLASSES: int = len(CLASS_NAMES)
    
    # Core training hyperparameters
    BATCH_SIZE: int = 32
    INITIAL_EPOCHS: int = 20  # Phase 1: Feature extractor training
    FINE_TUNE_EPOCHS: int = 20  # Phase 2: Fine-tuning base layers
    TOTAL_EPOCHS: int = INITIAL_EPOCHS + FINE_TUNE_EPOCHS
    
    # Learning Rates
    INITIAL_LEARNING_RATE: float = 1e-3
    FINE_TUNE_LEARNING_RATE: float = 1e-5
    
    # Base network parameters
    FINE_TUNE_AT: int = 100  # Freeze MobileNetV2 layers up to this index
    
    # Utility paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATASET_SPLITS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), "dataset", "splits")
    OUTPUT_MODEL_DIR: str = os.path.join(BASE_DIR, "models", "checkpoints")
    FINAL_MODEL_DIR: str = os.path.join(BASE_DIR, "models", "final")
    LOGS_DIR: str = os.path.join(BASE_DIR, "models", "logs")
    
    # Environment config
    SEED: int = 42

    # --- PHASE 17/18 INFERENCE & SAFETY DECISION ENGINE ---
    
    # Determines threshold for a prediction to be ACCEPTED vs UNABLE_TO_DETERMINE
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.80"))
    
    # Metadata for API responses and versioning
    MODEL_NAME: str = "NoteGuard-14Class-MobileNetV2"
    MODEL_VERSION: str = "1.0-stage2"


training_config = TrainingConfig()
