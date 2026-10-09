import os
import hashlib
from collections import defaultdict
from pathlib import Path
import json

def get_sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    split_dir = Path("dataset/split")
    
    splits = ["train", "val", "test"]
    stats = {s: defaultdict(int) for s in splits}
    
    hashes = {s: set() for s in splits}
    files = {s: set() for s in splits}
    
    features_found = False
    
    # 1. Traverse and collect data
    for s in splits:
        s_path = split_dir / s
        if not s_path.exists():
            continue
            
        for root, dirs, filenames in os.walk(s_path):
            if "features" in root.lower() or "feature" in root.lower():
                features_found = True
                
            for fname in filenames:
                fpath = Path(root) / fname
                
                # Class name is the immediate parent directory
                class_name = fpath.parent.name
                stats[s][class_name] += 1
                
                fhash = get_sha256(fpath)
                hashes[s].add(fhash)
                files[s].add(fpath.name)
                
    # 2. Check for overlaps
    train_val_overlap = hashes["train"].intersection(hashes["val"])
    train_test_overlap = hashes["train"].intersection(hashes["test"])
    val_test_overlap = hashes["val"].intersection(hashes["test"])
    
    # 3. Print report
    print("=== PHASE 7 VERIFICATION REPORT ===")
    
    classes = set()
    for s in splits:
        classes.update(stats[s].keys())
    
    classes = sorted(list(classes))
    
    for cls in classes:
        t = stats["train"][cls]
        v = stats["val"][cls]
        te = stats["test"][cls]
        total = t + v + te
        
        t_pct = (t / total * 100) if total > 0 else 0
        v_pct = (v / total * 100) if total > 0 else 0
        te_pct = (te / total * 100) if total > 0 else 0
        
        print(f"{cls}: Total={total} | Train={t} ({t_pct:.1f}%) | Val={v} ({v_pct:.1f}%) | Test={te} ({te_pct:.1f}%)")
        
    print("\n--- OVERLAP & VALIDATION ---")
    print(f"Overlap Train/Val (hashes): {len(train_val_overlap)}")
    print(f"Overlap Train/Test (hashes): {len(train_test_overlap)}")
    print(f"Overlap Val/Test (hashes): {len(val_test_overlap)}")
    print(f"Features found in splits: {features_found}")
    
    print("\n--- DIRECTORY CHECKS ---")
    for s in splits:
        print(f"{(split_dir / s).as_posix()} exists: {(split_dir / s).exists()}")

if __name__ == '__main__':
    main()
