"""Model calibration utilities."""
import numpy as np
from typing import List, Tuple, Dict
from sklearn.calibration import calibration_curve


class ModelCalibration:
    """Utilities for calibrating and analyzing model predictions."""
    
    def __init__(self):
        pass
    
    def calculate_calibration_curve(
        self, y_true: np.ndarray, y_pred: np.ndarray, n_bins: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate calibration curve.
        
        Args:
            y_true: True labels (0 or 1)
            y_pred: Predicted probabilities
            n_bins: Number of bins
            
        Returns:
            Tuple of (mean_predicted_prob, fraction_of_positives)
        """
        return calibration_curve(y_true, y_pred, n_bins=n_bins, strategy='uniform')
    
    def calculate_brier_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Brier score (lower is better).
        
        Args:
            y_true: True labels (0 or 1)
            y_pred: Predicted probabilities
            
        Returns:
            Brier score
        """
        return np.mean((y_pred - y_true) ** 2)
    
    def calculate_log_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate log loss (cross-entropy).
        
        Args:
            y_true: True labels (0 or 1)
            y_pred: Predicted probabilities
            
        Returns:
            Log loss
        """
        # Clip predictions to avoid log(0)
        y_pred = np.clip(y_pred, 1e-15, 1 - 1e-15)
        return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
    
    def analyze_calibration_by_confidence(
        self, y_true: np.ndarray, y_pred: np.ndarray, confidence_ranges: List[Tuple[float, float]]
    ) -> Dict[str, Dict]:
        """Analyze calibration for different confidence ranges.
        
        Args:
            y_true: True labels
            y_pred: Predicted probabilities
            confidence_ranges: List of (min, max) confidence tuples
            
        Returns:
            Dictionary with calibration stats for each range
        """
        results = {}
        
        for low, high in confidence_ranges:
            mask = (y_pred >= low) & (y_pred < high)
            
            if np.sum(mask) > 0:
                range_true = y_true[mask]
                range_pred = y_pred[mask]
                
                results[f"{low:.0%}-{high:.0%}"] = {
                    "count": int(np.sum(mask)),
                    "avg_predicted": float(np.mean(range_pred)),
                    "actual_win_rate": float(np.mean(range_true)),
                    "brier_score": float(self.calculate_brier_score(range_true, range_pred)),
                }
        
        return results
