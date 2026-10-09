import os
import cv2
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
import hashlib
import json
import csv
from collections import defaultdict
from PIL import Image

BASE_DATA_DIR = os.path.join("C:\\PROJECTS\\fakecurrency\\dataset\\split")
CHECKPOINT_PATH = os.path.join("C:\\PROJECTS\\fakecurrency\\backend\\src\\modules\\ai_engine\\models\\checkpoints\\stage2\\best_stage2.keras")
OUTPUT_DIR = os.path.join("C:\\PROJECTS\\fakecurrency\\models\\evaluation\\phase15_investigation")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CLASSES_14 = [
    "fake_10", "fake_20", "fake_50", "fake_100", "fake_200", "fake_500", "fake_2000",
    "real_10", "real_20", "real_50", "real_100", "real_200", "real_500", "real_2000"
]
DENOMS = ["10", "20", "50", "100", "200", "500", "2000"]
AUTH = ["fake", "real"]

def get_hashes(split_name):
    split_dir = os.path.join(BASE_DATA_DIR, split_name)
    hashes = set()
    for c in os.listdir(split_dir):
        cp = os.path.join(split_dir, c)
        if os.path.isdir(cp):
            for f in os.listdir(cp):
                if f.endswith(('.jpg', '.png', '.jpeg')):
                    with open(os.path.join(cp, f), 'rb') as file:
                        hashes.add(hashlib.sha256(file.read()).hexdigest())
    return hashes

def verify_leakage():
    print("Verifying Data Leakage...")
    train_h = get_hashes("train")
    val_h = get_hashes("val")
    test_h = get_hashes("test")
    
    t_v = len(train_h.intersection(val_h))
    t_t = len(train_h.intersection(test_h))
    v_t = len(val_h.intersection(test_h))
    
    print(f"Train Intersection Val: {t_v}")
    print(f"Train Intersection Test: {t_t}")
    print(f"Val Intersection Test: {v_t}")
    if t_v == 0 and t_t == 0 and v_t == 0:
        print("LEAKAGE VERIFICATION PASSED.")
    else:
        print("LEAKAGE VERIFICATION FAILED.")

def get_brightness(img_path):
    try:
        img = Image.open(img_path).convert('L')
        stat = np.mean(np.array(img))
        return stat
    except:
        return 0.0

def load_data(split_name):
    samples = []
    split_dir = os.path.join(BASE_DATA_DIR, split_name)
    for c in CLASSES_14:
        cp = os.path.join(split_dir, c)
        if os.path.isdir(cp):
            for f in os.listdir(cp):
                if f.endswith(('.jpg', '.png', '.jpeg')):
                    samples.append({
                        "path": os.path.join(cp, f),
                        "true_14": c,
                        "true_denom": c.split("_")[1],
                        "true_auth": c.split("_")[0]
                    })
    return samples

def build_distribution_analysis():
    print("Building Distribution Analysis...")
    with open(os.path.join(OUTPUT_DIR, "class_distribution_analysis.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Split", "Class_14", "Denomination", "Authenticity", "Is_Augmented", "Count"])
        
        for split in ["train", "val"]:
            samples = load_data(split)
            counts = defaultdict(int)
            for s in samples:
                is_aug = "aug_" in os.path.basename(s["path"])
                key = (split, s["true_14"], s["true_denom"], s["true_auth"], is_aug)
                counts[key] += 1
            
            for k, v in counts.items():
                writer.writerow([k[0], k[1], k[2], k[3], k[4], v])

def evaluate_test():
    print("Evaluating Test Set...")
    model = tf.keras.models.load_model(CHECKPOINT_PATH)
    test_samples = load_data("test")
    
    predictions = []
    batch_size = 32
    
    for i in range(0, len(test_samples), batch_size):
        batch = test_samples[i:i+batch_size]
        batch_x = []
        for s in batch:
            img = tf.keras.preprocessing.image.load_img(s["path"], target_size=(224, 224))
            batch_x.append(tf.keras.preprocessing.image.img_to_array(img))
        
        batch_x = np.array(batch_x, dtype=np.float32)
        preds = model.predict(batch_x, verbose=0)
        
        for j, s in enumerate(batch):
            pred_idx = np.argmax(preds[j])
            conf = preds[j][pred_idx]
            pred_14 = CLASSES_14[pred_idx]
            pred_denom = pred_14.split("_")[1]
            pred_auth = pred_14.split("_")[0]
            
            w, h = 0, 0
            brightness = 0.0
            try:
                with Image.open(s["path"]) as im:
                    w, h = im.size
                brightness = get_brightness(s["path"])
            except:
                pass
                
            predictions.append({
                "path": s["path"],
                "true_14": s["true_14"], "pred_14": pred_14,
                "true_denom": s["true_denom"], "pred_denom": pred_denom,
                "true_auth": s["true_auth"], "pred_auth": pred_auth,
                "confidence": conf,
                "w": w, "h": h, "brightness": brightness
            })
            
    return predictions

def build_error_priority(predictions):
    print("Building Error Priority Analysis...")
    y_true_14 = [s["true_14"] for s in predictions]
    y_pred_14 = [s["pred_14"] for s in predictions]
    
    y_true_denom = [s["true_denom"] for s in predictions]
    y_pred_denom = [s["pred_denom"] for s in predictions]
    
    y_true_auth = [s["true_auth"] for s in predictions]
    y_pred_auth = [s["pred_auth"] for s in predictions]
    
    rep_14 = classification_report(y_true_14, y_pred_14, target_names=CLASSES_14, output_dict=True, zero_division=0)
    rep_denom = classification_report(y_true_denom, y_pred_denom, target_names=DENOMS, output_dict=True, zero_division=0)
    
    with open(os.path.join(OUTPUT_DIR, "error_priority_analysis.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Level", "Class", "Precision", "Recall", "F1", "Support"])
        for c in CLASSES_14:
            if c in rep_14:
                writer.writerow(["14-Class", c, rep_14[c]['precision'], rep_14[c]['recall'], rep_14[c]['f1-score'], rep_14[c]['support']])
        for c in DENOMS:
            if c in rep_denom:
                writer.writerow(["Denom", c, rep_denom[c]['precision'], rep_denom[c]['recall'], rep_denom[c]['f1-score'], rep_denom[c]['support']])
                
    # Confusion pairs
    cm = confusion_matrix(y_true_denom, y_pred_denom, labels=DENOMS)
    pairs = []
    for i in range(len(DENOMS)):
        for j in range(len(DENOMS)):
            if i != j and cm[i][j] > 0:
                pairs.append((DENOMS[i], DENOMS[j], cm[i][j]))
    pairs.sort(key=lambda x: x[2], reverse=True)
    
    with open(os.path.join(OUTPUT_DIR, "top_denom_confusion_pairs.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["True", "Pred", "Count"])
        for p in pairs[:5]:
            writer.writerow(p)

    cm_auth = confusion_matrix(y_true_auth, y_pred_auth, labels=AUTH)
    with open(os.path.join(OUTPUT_DIR, "auth_confusion.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["True\\Pred"] + AUTH)
        for i, r in enumerate(cm_auth):
            writer.writerow([AUTH[i]] + list(r))
            
    cm_denom_full = confusion_matrix(y_true_denom, y_pred_denom, labels=DENOMS)
    with open(os.path.join(OUTPUT_DIR, "denom_confusion_matrix.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["True\\Pred"] + DENOMS)
        for i, r in enumerate(cm_denom_full):
            writer.writerow([DENOMS[i]] + list(r))

def build_confidence_analysis(predictions):
    print("Building Confidence Analysis...")
    
    buckets = [
        {"name": "<50%", "cond": lambda x: x < 0.50},
        {"name": "50-80%", "cond": lambda x: 0.50 <= x < 0.80},
        {"name": "80-90%", "cond": lambda x: 0.80 <= x < 0.90},
        {"name": ">90%", "cond": lambda x: x >= 0.90},
        {"name": "<80%", "cond": lambda x: x < 0.80},
        {"name": ">=80%", "cond": lambda x: x >= 0.80},
    ]
    
    with open(os.path.join(OUTPUT_DIR, "confidence_analysis.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Bucket", "Total_Predictions", "Correct", "Errors", "Accuracy", "Coverage_Pct"])
        
        total_preds = len(predictions)
        for b in buckets:
            in_bucket = [p for p in predictions if b["cond"](p["confidence"])]
            correct = [p for p in in_bucket if p["true_14"] == p["pred_14"]]
            total_b = len(in_bucket)
            acc = len(correct)/total_b if total_b > 0 else 0
            errs = total_b - len(correct)
            cov = total_b / total_preds
            writer.writerow([b["name"], total_b, len(correct), errs, f"{acc:.4f}", f"{cov:.4f}"])

def build_image_quality_analysis(predictions):
    print("Building Image Quality Analysis...")
    with open(os.path.join(OUTPUT_DIR, "image_quality_correlations.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Is_Error", "Avg_Width", "Avg_Height", "Avg_Aspect_Ratio", "Avg_Brightness", "Count"])
        
        correct = [p for p in predictions if p["true_14"] == p["pred_14"]]
        errors = [p for p in predictions if p["true_14"] != p["pred_14"]]
        
        def agg(subset, is_err):
            if not subset: return [is_err, 0, 0, 0, 0, 0]
            aw = np.mean([p["w"] for p in subset])
            ah = np.mean([p["h"] for p in subset])
            aar = np.mean([p["w"]/p["h"] if p["h"]>0 else 0 for p in subset])
            ab = np.mean([p["brightness"] for p in subset])
            return [is_err, f"{aw:.1f}", f"{ah:.1f}", f"{aar:.3f}", f"{ab:.1f}", len(subset)]
            
        writer.writerow(agg(correct, False))
        writer.writerow(agg(errors, True))
        
def main():
    verify_leakage()
    build_distribution_analysis()
    predictions = evaluate_test()
    build_error_priority(predictions)
    build_confidence_analysis(predictions)
    build_image_quality_analysis(predictions)
    print("Investigation Phase 1 data generated.")

if __name__ == "__main__":
    main()
