"""Logistic regression model."""
import numpy as np
from typing import Dict, List, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


class LogisticModel:
    """Logistic regression model using multiple features."""
    
    def __init__(self):
        self.model = LogisticRegression(random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the logistic regression model.
        
        Args:
            X: Feature matrix
            y: Target vector (0 or 1)
        """
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
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
        
        X_scaled = self.scaler.transform(X.reshape(1, -1))
        proba = self.model.predict_proba(X_scaled)[0]
        
        return {
            "team1_win_prob": proba[1],  # Probability of class 1
            "team2_win_prob": proba[0],  # Probability of class 0
            "model": "logistic",
        }
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature coefficients.
        
        Returns:
            Feature coefficients or None if not trained
        """
        if not self.is_trained:
            return None
        return self.model.coef_[0]
