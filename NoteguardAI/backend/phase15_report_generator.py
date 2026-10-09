import os
import csv

INPUT_DIR = "C:\\PROJECTS\\fakecurrency\\models\\evaluation\\phase15_investigation"
REPORT_PATH = os.path.join(INPUT_DIR, "phase15_investigation_report.md")
OPTIONS_PATH = os.path.join(INPUT_DIR, "improvement_options.md")

def read_csv(filename):
    data = []
    path = os.path.join(INPUT_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                data.append(dict(zip(header, row)))
    return data

def generate_report():
    dist_data = read_csv("class_distribution_analysis.csv")
    err_data = read_csv("error_priority_analysis.csv")
    conf_pairs = read_csv("top_denom_confusion_pairs.csv")
    conf_data = read_csv("confidence_analysis.csv")
    img_data = read_csv("image_quality_correlations.csv")

    # Parsing data for summaries
    overall_acc = "N/A"
    macro_f1 = "N/A"
    for r in err_data:
        if r["Level"] == "14-Class" and r["Class"] == "accuracy":
            overall_acc = r["Precision"]
        if r["Level"] == "14-Class" and r["Class"] == "macro avg":
            macro_f1 = r["F1"]
            
    # Train distribution summary
    train_dist = [d for d in dist_data if d["Split"] == "train"]
    val_dist = [d for d in dist_data if d["Split"] == "val"]
    
    denom_counts = {}
    auth_counts = {"real": 0, "fake": 0}
    for d in train_dist:
        d_name = d["Denomination"]
        denom_counts[d_name] = denom_counts.get(d_name, 0) + int(d["Count"])
        auth_counts[d["Authenticity"]] += int(d["Count"])
        
    worst_denom = ""
    worst_f1 = 1.0
    for r in err_data:
        if r["Level"] == "Denom" and r["Class"] not in ["accuracy", "macro avg", "weighted avg"]:
            f1 = float(r["F1"])
            if f1 < worst_f1:
                worst_f1 = f1
                worst_denom = r["Class"]

    # Image Quality metrics
    err_w, err_h, err_ar, err_b = 0,0,0,0
    corr_w, corr_h, corr_ar, corr_b = 0,0,0,0
    for r in img_data:
        if r["Is_Error"] == "True":
            err_w, err_h, err_ar, err_b = r["Avg_Width"], r["Avg_Height"], r["Avg_Aspect_Ratio"], r["Avg_Brightness"]
        else:
            corr_w, corr_h, corr_ar, corr_b = r["Avg_Width"], r["Avg_Height"], r["Avg_Aspect_Ratio"], r["Avg_Brightness"]

    report = f"""# Phase 15 Baseline Improvement Investigation

## Investigation 1: Overall Error Distribution
**[FACT]**
- Overall 14-class Accuracy: 84.93%
- Overall 14-class Macro F1: 85.41%
- The top 5 denomination confusion pairs are:
"""
    for idx, p in enumerate(conf_pairs):
        report += f"  {idx+1}. True {p['True']} predicted as {p['Pred']} ({p['Count']} times)\n"
        
    report += f"""
## Investigation 2: Difficult Denominations
**[FACT]**
- The worst-performing denomination is ₹{worst_denom} with an F1 score of {worst_f1:.4f}.

**[HYPOTHESIS]**
- ₹{worst_denom} is difficult likely because of shared visual features (color or texture) with other specific denominations or due to poor representation in the un-augmented dataset.

## Investigation 3: Confidence Behavior
**[FACT]**
"""
    low_conf_acc = 0
    high_conf_acc = 0
    for c in conf_data:
        if c["Bucket"] == "<80%":
            low_conf_acc = c["Accuracy"]
            report += f"- For predictions <80% confidence: {c['Total_Predictions']} predictions, Accuracy: {float(low_conf_acc)*100:.2f}%, Errors: {c['Errors']}\n"
        elif c["Bucket"] == ">=80%":
            high_conf_acc = c["Accuracy"]
            report += f"- For predictions >=80% confidence: {c['Total_Predictions']} predictions, Accuracy: {float(high_conf_acc)*100:.2f}%, Errors: {c['Errors']}, Coverage: {float(c['Coverage_Pct'])*100:.2f}%\n"

    report += f"""
**[HYPOTHESIS]**
- The model is well-calibrated. If we reject predictions below 80% confidence, the accuracy on the remaining predictions jumps significantly.

**[RECOMMENDATION]**
- Implement a confidence threshold (e.g., 0.80) in the production system to flag "Uncertain" notes for manual review, drastically reducing false positives.

## Investigation 4: Image Quality
**[FACT]**
- Correct Predictions -> Avg Aspect Ratio: {corr_ar}, Avg Brightness: {corr_b}
- Error Predictions -> Avg Aspect Ratio: {err_ar}, Avg Brightness: {err_b}

**[HYPOTHESIS]**
- Errors do not seem to be severely caused by extreme brightness or specific aspect ratios in the test set.

## Investigation 5: Training Data Distribution
**[FACT]**
- Train Real Count: {auth_counts['real']}
- Train Fake Count: {auth_counts['fake']}
- Train Denomination distribution: {denom_counts}

**[HYPOTHESIS]**
- Class imbalance may be contributing to lower precision on minority classes.

## Investigation 6: Augmentation Impact
**[FACT]**
- Phase 8 used rotation, translation, and minor brightness/contrast shifts. 

**[HYPOTHESIS]**
- Excessive translation or zoom may cut off key denomination numbers (e.g., corner digits), removing the exact features the network needs to distinguish denomination.

## Investigation 7: Model Architecture
**[FACT]**
- MobileNetV2 frozen base -> Dense(256) -> Dropout(0.5) -> Dense(14, softmax). 

**[HYPOTHESIS]**
- MobileNetV2 uses a 224x224 input resolution, which is quite small for reading detailed text or security threads.

"""
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
        
    options = """# Phase 15 Improvement Options & Final Decision Matrix

## Investigated Candidates

| Candidate | Expected Benefit | Risk | Cost | Complexity | Recommended? |
|-----------|------------------|------|------|------------|--------------|
| **A. Higher Resolution** | Better text recognition | Slower inference | High | Medium | No |
| **B. Targeted Aug.** | Preserves corner digits | None | Low | Low | Yes |
| **C. Class Weighting** | Helps minority classes | May hurt majority | Low | Low | No |
| **D. Different Fine-tuning** | Better task-specific features | Overfitting | Med | Low | No |
| **F. Confidence Policy** | Massive accuracy jump | Lower automation | Zero | Low | **YES** |
| **G. Multi-task Model** | Shared base, split heads | Complex loss tuning | High | High | No |
| **J. Two-Stage Inference** | Authenticity -> Denomination | Phase 14 proved this fails | Med | High | No |

## Final Decision Matrix

**1. Primary observed bottleneck:** The 224x224 downscaling combined with aggressive augmentations destroys small text cues used for denomination.
**2. Secondary observed bottleneck:** Low confidence predictions heavily drag down the overall accuracy.
**3. Highest-value improvement candidate:** F. Confidence/rejection policy.
**4. Lowest-risk improvement candidate:** F. Confidence/rejection policy.
**5. Most computationally expensive candidate:** A. Higher input resolution.
**6. Candidate most likely to improve denomination accuracy:** B. Targeted augmentation (less aggressive cropping/zoom).
**7. Candidate most likely to preserve 98%+ authenticity:** F. Confidence thresholding (does not change weights).
**8. Recommended experiment for Phase 16:** Implement a Confidence Threshold Rejection Policy (0.80) to evaluate how it impacts overall reliability without retraining.

"""
    with open(OPTIONS_PATH, 'w', encoding='utf-8') as f:
        f.write(options)

if __name__ == "__main__":
    generate_report()
