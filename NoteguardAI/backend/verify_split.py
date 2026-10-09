import os
import hashlib
from collections import defaultdict

def get_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

split_dir = '../dataset/split'
splits = ['train', 'val', 'test']
classes = [
    'real_10', 'fake_10', 'real_20', 'fake_20', 'real_50', 'fake_50',
    'real_100', 'fake_100', 'real_200', 'fake_200', 'real_500', 'fake_500',
    'real_2000', 'fake_2000'
]

counts = {s: defaultdict(int) for s in splits}
hashes = {s: set() for s in splits}
total_counts = {s: 0 for s in splits}
augmented_count = 0
features_count = 0

for s in splits:
    s_dir = os.path.join(split_dir, s)
    if not os.path.exists(s_dir):
        continue
    for c in os.listdir(s_dir):
        c_dir = os.path.join(s_dir, c)
        if not os.path.isdir(c_dir):
            continue
        if 'features' in c.lower() or 'feature' in c.lower():
            features_count += len(os.listdir(c_dir))
        for f in os.listdir(c_dir):
            f_path = os.path.join(c_dir, f)
            if not os.path.isfile(f_path):
                continue
            if f.startswith('aug_'):
                augmented_count += 1
            counts[s][c] += 1
            total_counts[s] += 1
            hashes[s].add(get_hash(f_path))

print(f"Total Train: {total_counts['train']}")
print(f"Total Val: {total_counts['val']}")
print(f"Total Test: {total_counts['test']}")

print("\n| Class | Train | Validation | Test | Total | Train % | Val % | Test % |")
print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
for c in classes:
    tr = counts['train'][c]
    va = counts['val'][c]
    te = counts['test'][c]
    tot = tr + va + te
    tr_p = (tr / tot * 100) if tot > 0 else 0
    va_p = (va / tot * 100) if tot > 0 else 0
    te_p = (te / tot * 100) if tot > 0 else 0
    print(f"| {c} | {tr} | {va} | {te} | {tot} | {tr_p:.1f}% | {va_p:.1f}% | {te_p:.1f}% |")

print("\nLeakage Check:")
print(f"Train ∩ Validation = {len(hashes['train'].intersection(hashes['val']))}")
print(f"Train ∩ Test = {len(hashes['train'].intersection(hashes['test']))}")
print(f"Validation ∩ Test = {len(hashes['val'].intersection(hashes['test']))}")

print("\nOther Checks:")
print(f"Augmented images found: {augmented_count}")
print(f"Feature images found: {features_count}")
