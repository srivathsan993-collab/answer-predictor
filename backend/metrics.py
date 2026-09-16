import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, log_loss, confusion_matrix

def calculate_metrics(y_true, y_pred, y_prob=None, top_3_preds=None):
    metrics = {}
    
    # Basic metrics
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    metrics['precision'] = precision_score(y_true, y_pred, average='macro', zero_division=0)
    metrics['recall'] = recall_score(y_true, y_pred, average='macro', zero_division=0)
    metrics['f1'] = f1_score(y_true, y_pred, average='micro', zero_division=0)
    metrics['macro_f1'] = f1_score(y_true, y_pred, average='macro', zero_division=0)
    metrics['weighted_f1'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    # Class-wise metrics
    class_precision = precision_score(y_true, y_pred, average=None, labels=['A','B','C','D','E'], zero_division=0)
    class_recall = recall_score(y_true, y_pred, average=None, labels=['A','B','C','D','E'], zero_division=0)
    class_f1 = f1_score(y_true, y_pred, average=None, labels=['A','B','C','D','E'], zero_division=0)
    
    # Support (counts)
    support = {cls: list(y_true).count(cls) for cls in ['A','B','C','D','E']}
    
    metrics['class_metrics'] = {
        cls: {
            'precision': float(class_precision[i]),
            'recall': float(class_recall[i]),
            'f1': float(class_f1[i]),
            'support': support[cls]
        }
        for i, cls in enumerate(['A','B','C','D','E'])
    }
    
    # Log loss
    if y_prob is not None:
        try:
            # Need to format y_prob properly matching ['A','B','C','D','E']
            # y_prob should be shape (N, 5)
            metrics['log_loss'] = log_loss(y_true, y_prob, labels=['A','B','C','D','E'])
        except Exception:
            metrics['log_loss'] = None
    else:
        metrics['log_loss'] = None
        
    # Top-1 Accuracy is same as accuracy
    metrics['top_1_accuracy'] = metrics['accuracy']
    
    # Top-3 Accuracy and MAP@3
    if top_3_preds is not None:
        top_3_correct = 0
        map3 = 0.0
        
        for yt, top3 in zip(y_true, top_3_preds):
            if yt in top3:
                top_3_correct += 1
                rank = top3.index(yt) + 1
                map3 += 1.0 / rank
                
        metrics['top_3_accuracy'] = top_3_correct / len(y_true) if len(y_true) > 0 else 0
        metrics['map_at_3'] = map3 / len(y_true) if len(y_true) > 0 else 0
    else:
        metrics['top_3_accuracy'] = None
        metrics['map_at_3'] = None
        
    # RMSE (Encoded Classes)
    label_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
    y_true_enc = np.array([label_map.get(y, 0) for y in y_true])
    y_pred_enc = np.array([label_map.get(y, 0) for y in y_pred])
    
    rmse = np.sqrt(np.mean((y_true_enc - y_pred_enc)**2))
    metrics['rmse_encoded'] = float(rmse)
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=['A','B','C','D','E'])
    metrics['confusion_matrix'] = cm.tolist()
    
    # Format all metrics to float for JSON serialization
    for k, v in metrics.items():
        if isinstance(v, (np.float32, np.float64)):
            metrics[k] = float(v)
            
    return metrics
