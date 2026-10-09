import os
import glob
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps

def reconcile():
    base_dir = r"C:\PROJECTS\fakecurrency"
    dataset_dir = os.path.join(base_dir, "dataset", "split", "val")
    model_path = os.path.join(base_dir, "backend", "src", "modules", "ai_engine", "models", "evaluation", "phase28_model_improvement", "experiment_1_targeted_augmentation", "stage2", "best_stage2.keras")
    
    # 1. Exact number of image files under dataset/split/val
    all_files = []
    class_names = [
        "fake_10", "fake_20", "fake_50", "fake_100", "fake_200", "fake_500", "fake_2000",
        "real_10", "real_20", "real_50", "real_100", "real_200", "real_500", "real_2000"
    ]
    
    file_counts = {}
    for c in class_names:
        cdir = os.path.join(dataset_dir, c)
        if os.path.isdir(cdir):
            files = [f for f in os.listdir(cdir) if os.path.isfile(os.path.join(cdir, f))]
            file_counts[c] = len(files)
            for f in files:
                all_files.append(os.path.join(c, f))
                
    total_files = len(all_files)
    unique_files = len(set(all_files))
    
    print("=== RECONCILIATION REPORT ===")
    print(f"1. Exact number of image files under dataset/split/val: {total_files}")
    print(f"   Unique filenames: {unique_files}")
    
    print("\n2. Exact count per each of the 14 classes:")
    sum_counts = 0
    for c in class_names:
        print(f"   {c}: {file_counts.get(c, 0)}")
        sum_counts += file_counts.get(c, 0)
        
    print(f"\n3. Sum of all class counts: {sum_counts}")
    
    if sum_counts != 637:
        print("WARNING: SUM IS NOT 637!")
    
    # Reload model and do exact prediction
    model = tf.keras.models.load_model(model_path)
    
    eval_count = 0
    correct = 0
    incorrect = 0
    conf_lt_80 = 0
    conf_ge_80 = 0
    false_real = 0
    false_fake = 0
    
    denom_results = {denom: {"total": 0, "correct_denom": 0, "ge_80": 0, "lt_80": 0} for denom in ["10", "20", "50", "100", "200", "500", "2000"]}
    
    for c_idx, c in enumerate(class_names):
        cdir = os.path.join(dataset_dir, c)
        if not os.path.isdir(cdir): continue
        is_fake_true = c.startswith("fake_")
        true_denom = c.split("_")[1]
        
        for f in os.listdir(cdir):
            fpath = os.path.join(cdir, f)
            img = Image.open(fpath)
            img = ImageOps.exif_transpose(img)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = img.resize((224, 224), resample=Image.Resampling.NEAREST)
            img_array = np.array(img, dtype=np.float32)
            img_batch = np.expand_dims(img_array, axis=0)
            
            preds = model.predict(img_batch, verbose=0)
            pred_idx = np.argmax(preds[0])
            pred_c = class_names[pred_idx]
            conf = float(preds[0][pred_idx])
            
            is_fake_pred = pred_c.startswith("fake_")
            pred_denom = pred_c.split("_")[1]
            
            eval_count += 1
            if pred_idx == c_idx:
                correct += 1
            else:
                incorrect += 1
                
            if conf < 0.80:
                conf_lt_80 += 1
            else:
                conf_ge_80 += 1
                
            if is_fake_true and not is_fake_pred:
                false_real += 1
            elif not is_fake_true and is_fake_pred:
                false_fake += 1
                
            denom_results[true_denom]["total"] += 1
            if true_denom == pred_denom:
                denom_results[true_denom]["correct_denom"] += 1
            
            if conf >= 0.80:
                denom_results[true_denom]["ge_80"] += 1
            else:
                denom_results[true_denom]["lt_80"] += 1

    print(f"\n4. Exact number of predictions evaluated: {eval_count}")
    print(f"5. Exact number of correct predictions: {correct}")
    print(f"6. Exact number of incorrect predictions: {incorrect}")
    print(f"7. Exact number of confidence < 0.80 predictions: {conf_lt_80}")
    print(f"8. Exact number of confidence >= 0.80 predictions: {conf_ge_80}")
    print(f"9. Exact UNABLE_TO_DETERMINE count: {conf_lt_80}")
    print(f"10. Exact False-REAL count: {false_real}")
    print(f"11. Exact False-FAKE count: {false_fake}")
    
    print("\n--- RECALCULATED DENOMINATION METRICS ---")
    for d, stats in denom_results.items():
        total = stats["total"]
        if total == 0: continue
        acc = stats["correct_denom"] / total
        rej = stats["lt_80"] / total
        cov = stats["ge_80"] / total
        print(f"Denomination {d}: Total={total}, Correct Denom={stats['correct_denom']}, Denom Acc={acc:.2%}, Rejection (UTD)={rej:.2%}, >=0.80 Coverage={cov:.2%}")

if __name__ == '__main__':
    reconcile()
