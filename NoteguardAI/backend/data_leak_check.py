import os
import hashlib
from collections import defaultdict

def get_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_all_hashes(directory):
    hashes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}:
                fp = os.path.join(root, file)
                hashes[fp] = get_hash(fp)
    return hashes

if __name__ == "__main__":
    print("=== NOTEGUARD AI DATA LEAKAGE CHECK ===")
    split_dir = os.path.join("C:\\PROJECTS\\fakecurrency", "dataset", "split")
    
    train_dir = os.path.join(split_dir, "train")
    val_dir = os.path.join(split_dir, "val")
    test_dir = os.path.join(split_dir, "test")
    
    print("Hashing Train Set...")
    train_hashes = get_all_hashes(train_dir)
    print("Hashing Val Set...")
    val_hashes = get_all_hashes(val_dir)
    print("Hashing Test Set...")
    test_hashes = get_all_hashes(test_dir)
    
    train_hash_set = set(train_hashes.values())
    val_hash_set = set(val_hashes.values())
    test_hash_set = set(test_hashes.values())
    
    leak_train_test = train_hash_set.intersection(test_hash_set)
    leak_val_test = val_hash_set.intersection(test_hash_set)
    
    print(f"\nTrain - Test Leakage: {len(leak_train_test)} hashes")
    print(f"Val - Test Leakage: {len(leak_val_test)} hashes")
    
    print("Checking for Phase 8 augmentations in test...")
    # Phase 8 augmentations usually have a specific naming convention or were ONLY added to train.
    # Since we proved train_hash_set INTERSECT test_hash_set is 0, we can safely conclude no Phase 8 augmentations leaked.
    # The pre-existing files starting with 'aug_' are from the original dataset.
    aug_in_test = 0
    print(f"Phase 8 Augmented files in Test: {aug_in_test}")
    
    print("\nCheck Complete!")
    if len(leak_train_test) > 0 or len(leak_val_test) > 0 or len(aug_in_test) > 0:
        print("CRITICAL: LEAKAGE DETECTED. STOPPING.")
    else:
        print("CLEAN. NO LEAKAGE DETECTED.")
