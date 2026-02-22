"""Poisson model for totals/props."""
import numpy as np
from typing import Dict
from scipy.stats import poisson


class PoissonModel:
    """Poisson model for predicting totals (rounds, maps, etc.)."""
    
    def __init__(self):
        pass
    
    def predict_total(
        self, team1_avg: float, team2_avg: float, line: float
    ) -> Dict[str, float]:
        """Predict over/under for a total line.
        
        Args:
            team1_avg: Team 1's average for the metric
            team2_avg: Team 2's average for the metric
            line: Total line
            
        Returns:
            Dictionary with predictions
        """
        # Combined expected value
        expected_total = team1_avg + team2_avg
        
        # Calculate probability of over/under using Poisson
        # This is a simplification - actual implementation would be more sophisticated
        prob_over = 1.0 - poisson.cdf(line, expected_total)
        prob_under = poisson.cdf(line, expected_total)
        
        return {
            "over_prob": prob_over,
            "under_prob": prob_under,
            "expected_total": expected_total,
            "model": "poisson",
        }
    
    def predict_exact_score(
        self, team1_avg: float, team2_avg: float
    ) -> Dict[str, float]:
        """Predict most likely score.
        
        Args:
            team1_avg: Team 1's average score
            team2_avg: Team 2's average score
            
        Returns:
            Dictionary with score predictions
        """
        # Most likely scores
        team1_likely = int(round(team1_avg))
        team2_likely = int(round(team2_avg))
        
        return {
            "team1_expected_score": team1_avg,
            "team2_expected_score": team2_avg,
            "team1_most_likely": team1_likely,
            "team2_most_likely": team2_likely,
            "model": "poisson",
        }
