"""XGBoost machine learning model."""
import numpy as np
from typing import Dict, Optional
import xgboost as xgb


class XGBoostModel:
    """XGBoost model for match prediction."""
    
    def __init__(self, **params):
        default_params = {
            "objective": "binary:logistic",
            "max_depth": 6,
            "learning_rate": 0.1,
            "n_estimators": 100,
            "random_state": 42,
        }
        default_params.update(params)
        
        self.model = xgb.XGBClassifier(**default_params)
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the XGBoost model.
        
        Args:
            X: Feature matrix
            y: Target vector (0 or 1)
        """
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> Dict[str, float]:
        """Predict match outcome.
        
        Args:
            X: Feature vector (single prediction)
            
        Returns:
            Dictionary with predictions
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        proba = self.model.predict_proba(X.reshape(1, -1))[0]
        
        return {
            "team1_win_prob": proba[1],  # Probability of class 1
            "team2_win_prob": proba[0],  # Probability of class 0
            "model": "xgboost",
        }
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature importance scores.
        
        Returns:
            Feature importance array or None if not trained
        """
        if not self.is_trained:
            return None
        return self.model.feature_importances_
