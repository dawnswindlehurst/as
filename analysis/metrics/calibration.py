"""Calibration metrics for model assessment."""
from typing import Dict, List, Tuple
import numpy as np
from .base import MetricsCalculator
from database.models import Bet


class CalibrationMetrics(MetricsCalculator):
    """Calculate model calibration metrics."""
    
    def calculate(self) -> Dict:
        """Calculate calibration metrics.
        
        Returns:
            Dictionary with:
            - brier_score: Mean squared error of probabilities
            - log_loss: Cross-entropy loss
            - calibration_error: Mean calibration error
            - overround_beat_rate: % of times we beat bookmaker margin
            - calibration_bins: Data for calibration curve
        """
        if not self.bets:
            return self._empty_metrics()
        
        # Filter settled bets
        settled_bets = [b for b in self.bets if b.status in ['won', 'lost']]
        
        if not settled_bets:
            return self._empty_metrics()
        
        # Extract probabilities and outcomes
        predicted_probs = []
        actual_outcomes = []
        
        for bet in settled_bets:
            predicted_probs.append(bet.model_probability)
            actual_outcomes.append(1 if bet.status == 'won' else 0)
        
        predicted = np.array(predicted_probs)
        actual = np.array(actual_outcomes)
        
        # Brier Score
        brier = np.mean((predicted - actual) ** 2)
        
        # Log Loss
        epsilon = 1e-15  # To avoid log(0)
        predicted_clipped = np.clip(predicted, epsilon, 1 - epsilon)
        log_loss = -np.mean(actual * np.log(predicted_clipped) + (1 - actual) * np.log(1 - predicted_clipped))
        
        # Calibration Error (binned)
        calibration_error, calibration_bins = self._calculate_calibration_error(predicted, actual)
        
        # Overround Beat Rate
        overround_beat_rate = self._calculate_overround_beat_rate(settled_bets)
        
        return {
            'brier_score': round(brier, 4),
            'log_loss': round(log_loss, 4),
            'calibration_error': round(calibration_error, 4),
            'overround_beat_rate': round(overround_beat_rate, 2),
            'calibration_bins': calibration_bins,
        }
    
    def _calculate_calibration_error(
        self, 
        predicted: np.ndarray, 
        actual: np.ndarray,
        n_bins: int = 10
    ) -> Tuple[float, List[Dict]]:
        """Calculate Expected Calibration Error (ECE).
        
        Args:
            predicted: Predicted probabilities
            actual: Actual outcomes (0 or 1)
            n_bins: Number of bins for calibration
            
        Returns:
            Tuple of (calibration_error, bin_data)
        """
        bins = np.linspace(0, 1, n_bins + 1)
        bin_data = []
        total_error = 0
        total_count = 0
        
        for i in range(n_bins):
            # Find predictions in this bin
            in_bin = (predicted >= bins[i]) & (predicted < bins[i + 1])
            
            if np.sum(in_bin) > 0:
                bin_predicted = np.mean(predicted[in_bin])
                bin_actual = np.mean(actual[in_bin])
                bin_count = np.sum(in_bin)
                bin_error = abs(bin_predicted - bin_actual)
                
                total_error += bin_error * bin_count
                total_count += bin_count
                
                bin_data.append({
                    'bin_start': bins[i],
                    'bin_end': bins[i + 1],
                    'predicted': bin_predicted,
                    'actual': bin_actual,
                    'count': int(bin_count),
                    'error': bin_error,
                })
        
        ece = total_error / total_count if total_count > 0 else 0
        return ece, bin_data
    
    def _calculate_overround_beat_rate(self, bets: List[Bet]) -> float:
        """Calculate how often we beat the bookmaker's margin.
        
        The overround (bookmaker margin) is when the sum of implied probabilities
        exceeds 1.0. We beat it when our edge is positive.
        
        Args:
            bets: List of settled bets
            
        Returns:
            Percentage of bets with positive edge
        """
        if not bets:
            return 0.0
        
        positive_edge_count = sum(1 for bet in bets if bet.edge > 0)
        return (positive_edge_count / len(bets)) * 100
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics dictionary."""
        return {
            'brier_score': 0.0,
            'log_loss': 0.0,
            'calibration_error': 0.0,
            'overround_beat_rate': 0.0,
            'calibration_bins': [],
        }
