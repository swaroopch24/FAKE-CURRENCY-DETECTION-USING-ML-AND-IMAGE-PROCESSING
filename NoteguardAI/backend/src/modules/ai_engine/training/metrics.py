import numpy as np

class ModelEvaluatorMetrics:
    """
    Computes performance metrics (Precision, Recall, F1, Confusion Matrix) 
    from model predictions and ground-truth arrays.
    """
    @staticmethod
    def calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        """
        Computes metric variables. Expects y_true and y_pred to be 1D class indexes.
        """
        classes = np.unique(y_true)
        num_classes = len(classes)
        
        # Calculate overall accuracy
        accuracy = np.mean(y_true == y_pred)
        
        precision_list = []
        recall_list = []
        f1_list = []

        # Multi-class macro-averaging calculations
        for c in range(14):  # Match our 14 class index limits
            tp = np.sum((y_true == c) & (y_pred == c))
            fp = np.sum((y_true != c) & (y_pred == c))
            fn = np.sum((y_true == c) & (y_pred != c))

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            precision_list.append(precision)
            recall_list.append(recall)
            f1_list.append(f1)

        return {
            "accuracy": float(accuracy),
            "macro_precision": float(np.mean(precision_list)),
            "macro_recall": float(np.mean(recall_list)),
            "macro_f1": float(np.mean(f1_list)),
            "per_class_f1": [float(x) for x in f1_list]
        }

    @staticmethod
    def generate_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int = 14) -> np.ndarray:
        """
        Generates a raw confusion matrix index grid.
        """
        cm = np.zeros((num_classes, num_classes), dtype=int)
        for i in range(len(y_true)):
            true_label = int(y_true[i])
            pred_label = int(y_pred[i])
            if 0 <= true_label < num_classes and 0 <= pred_label < num_classes:
                cm[true_label, pred_label] += 1
        return cm
