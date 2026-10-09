import os
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps

from src.modules.ai_engine.inference import AIInferenceService
from src.modules.ai_engine.decision import DecisionEngine
from src.modules.ai_engine.schemas import DecisionState, Authenticity

def run_step1_diagnostic():
    base_dir = r"C:\PROJECTS\fakecurrency"
    dataset_dir = os.path.join(base_dir, "dataset", "split", "val")
    model_path = os.path.join(base_dir, "backend", "src", "modules", "ai_engine", "models", "evaluation", "phase28_model_improvement", "experiment_1_targeted_augmentation", "stage2", "best_stage2.keras")
    
    class_names = [
        "fake_10", "fake_20", "fake_50", "fake_100", "fake_200", "fake_500", "fake_2000",
        "real_10", "real_20", "real_50", "real_100", "real_200", "real_500", "real_2000"
    ]
    
    print("Loading inference service and decision engine...")
    inference_service = AIInferenceService(model_path)
    decision_engine = DecisionEngine()
    
    # Pre-warm model to avoid timing out or lagging on first call
    dummy_input = np.zeros((1, 224, 224, 3), dtype=np.float32)
    inference_service.execute_prediction(dummy_input)
    
    total = 0
    correct_auth = 0
    correct_denom = 0
    false_real = 0
    false_fake = 0
    
    utd_count = 0
    
    # Distributions
    auth_confidences = []
    denom_confidences = []
    
    for c_idx, c in enumerate(class_names):
        cdir = os.path.join(dataset_dir, c)
        if not os.path.isdir(cdir): continue
        is_true_real = c.startswith("real_")
        true_denom_val = int(c.split("_")[1])
        
        for f in os.listdir(cdir):
            fpath = os.path.join(cdir, f)
            img = Image.open(fpath)
            img = ImageOps.exif_transpose(img)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = img.resize((224, 224), resample=Image.Resampling.NEAREST)
            img_array = np.array(img, dtype=np.float32)
            img_batch = np.expand_dims(img_array, axis=0)
            
            # Step 1: Raw inference
            raw_result = inference_service.execute_prediction(img_batch)
            
            # Step 2: Pass through new Decision Engine
            decision = decision_engine.evaluate(raw_result)
            
            total += 1
            
            if decision["status"] == DecisionState.UNABLE_TO_DETERMINE:
                utd_count += 1
                # To calculate raw accuracy regardless of threshold, we look at raw_result
                auth_conf = max(raw_result["p_real"], raw_result["p_fake"])
                is_pred_real = raw_result["p_real"] >= raw_result["p_fake"]
                pred_denom = int(raw_result["class_label"].split("_")[1])
                denom_conf = raw_result["confidence"]
            else:
                res = decision["result"]
                auth_conf = res.confidence # We temporarily mapped auth conf to confidence
                is_pred_real = (res.authenticity == Authenticity.AUTHENTIC)
                pred_denom = res.denomination
                denom_conf = raw_result["confidence"] # We need the raw denom conf
                
            auth_confidences.append(auth_conf)
            denom_confidences.append(denom_conf)
            
            if is_pred_real == is_true_real:
                correct_auth += 1
            else:
                if is_pred_real and not is_true_real:
                    false_real += 1
                elif not is_pred_real and is_true_real:
                    false_fake += 1
                    
            if pred_denom == true_denom_val:
                correct_denom += 1

    print("=== STEP 1 ACTUAL DECISION ENGINE DIAGNOSTIC ===")
    print(f"Total Evaluated: {total}")
    print(f"Authenticity Accuracy: {correct_auth / total:.2%}")
    print(f"False-REAL Count: {false_real}")
    print(f"False-FAKE Count: {false_fake}")
    print(f"UTD Count: {utd_count}")
    print(f"UTD Rate: {utd_count / total:.2%}")
    print(f"Denomination Accuracy: {correct_denom / total:.2%}")
    print(f"Avg Authenticity Confidence: {np.mean(auth_confidences):.4f}")
    print(f"Avg Denomination Confidence: {np.mean(denom_confidences):.4f}")

if __name__ == '__main__':
    run_step1_diagnostic()
