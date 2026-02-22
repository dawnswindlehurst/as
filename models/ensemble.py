"""Ensemble model combining multiple models."""
import numpy as np
from typing import Dict, List
from models.elo import ELOModel
from models.glicko import GlickoModel


class EnsembleModel:
    """Ensemble model that combines predictions from multiple models."""
    
    def __init__(self, weights: Dict[str, float] = None):
        """Initialize ensemble model.
        
        Args:
            weights: Dictionary of model weights (must sum to 1.0)
        """
        self.weights = weights or {
            "elo": 0.2,
            "glicko": 0.25,
            "logistic": 0.25,
            "xgboost": 0.3,
        }
        
        # Ensure weights sum to 1.0
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0):
            # Normalize weights
            self.weights = {k: v / total for k, v in self.weights.items()}
    
    def predict(self, predictions: List[Dict]) -> Dict[str, float]:
        """Combine predictions from multiple models.
        
        Args:
            predictions: List of prediction dictionaries from different models
            
        Returns:
            Ensemble prediction dictionary
        """
        team1_probs = []
        team2_probs = []
        weights_used = []
        
        for pred in predictions:
            model_name = pred.get("model")
            if model_name in self.weights:
                weight = self.weights[model_name]
                team1_probs.append(pred["team1_win_prob"] * weight)
                team2_probs.append(pred["team2_win_prob"] * weight)
                weights_used.append(weight)
        
        # Normalize if not all models provided predictions
        if weights_used:
            total_weight = sum(weights_used)
            ensemble_team1 = sum(team1_probs) / total_weight
            ensemble_team2 = sum(team2_probs) / total_weight
        else:
            # Fallback to simple average
            ensemble_team1 = np.mean([p["team1_win_prob"] for p in predictions])
            ensemble_team2 = np.mean([p["team2_win_prob"] for p in predictions])
        
        return {
            "team1_win_prob": ensemble_team1,
            "team2_win_prob": ensemble_team2,
            "model": "ensemble",
            "num_models": len(predictions),
            "weights": self.weights,
        }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Update model weights.
        
        Args:
            new_weights: New weight dictionary
        """
        total = sum(new_weights.values())
        self.weights = {k: v / total for k, v in new_weights.items()}
