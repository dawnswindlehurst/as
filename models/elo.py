"""ELO rating system implementation."""
import math
from typing import Dict, Tuple
from config.constants import ELO_K_FACTOR, ELO_INITIAL_RATING


class ELOModel:
    """ELO rating system for esports."""
    
    def __init__(self, k_factor: float = ELO_K_FACTOR):
        self.k_factor = k_factor
        self.initial_rating = ELO_INITIAL_RATING
    
    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score for team A.
        
        Args:
            rating_a: Team A's rating
            rating_b: Team B's rating
            
        Returns:
            Expected score (probability of A winning)
        """
        return 1.0 / (1.0 + math.pow(10, (rating_b - rating_a) / 400.0))
    
    def update_ratings(
        self, rating_a: float, rating_b: float, score_a: float
    ) -> Tuple[float, float]:
        """Update ratings after a match.
        
        Args:
            rating_a: Team A's current rating
            rating_b: Team B's current rating
            score_a: Actual score for team A (1 for win, 0 for loss, 0.5 for draw)
            
        Returns:
            Tuple of (new_rating_a, new_rating_b)
        """
        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = 1.0 - expected_a
        
        new_rating_a = rating_a + self.k_factor * (score_a - expected_a)
        new_rating_b = rating_b + self.k_factor * ((1 - score_a) - expected_b)
        
        return new_rating_a, new_rating_b
    
    def predict_match(self, rating_a: float, rating_b: float) -> Dict[str, float]:
        """Predict match outcome.
        
        Args:
            rating_a: Team A's rating
            rating_b: Team B's rating
            
        Returns:
            Dictionary with predictions
        """
        prob_a = self.expected_score(rating_a, rating_b)
        prob_b = 1.0 - prob_a
        
        return {
            "team1_win_prob": prob_a,
            "team2_win_prob": prob_b,
            "model": "elo",
        }
