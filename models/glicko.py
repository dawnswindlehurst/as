"""Glicko-2 rating system implementation."""
import math
from typing import Dict, Tuple, List
from config.constants import GLICKO_INITIAL_RATING, GLICKO_INITIAL_RD, GLICKO_INITIAL_SIGMA


class GlickoModel:
    """Glicko-2 rating system - improvement over ELO with rating deviation."""
    
    def __init__(self, tau: float = 0.5):
        self.tau = tau  # System constant
        self.initial_rating = GLICKO_INITIAL_RATING
        self.initial_rd = GLICKO_INITIAL_RD
        self.initial_sigma = GLICKO_INITIAL_SIGMA
    
    def _g(self, rd: float) -> float:
        """Calculate g(RD) function."""
        return 1.0 / math.sqrt(1.0 + (3.0 * rd * rd) / (math.pi * math.pi))
    
    def _e(self, rating: float, opponent_rating: float, opponent_rd: float) -> float:
        """Calculate E function (expected score)."""
        return 1.0 / (1.0 + math.exp(-self._g(opponent_rd) * (rating - opponent_rating)))
    
    def expected_score(
        self, rating_a: float, rd_a: float, rating_b: float, rd_b: float
    ) -> float:
        """Calculate expected score for team A.
        
        Args:
            rating_a: Team A's rating
            rd_a: Team A's rating deviation
            rating_b: Team B's rating
            rd_b: Team B's rating deviation
            
        Returns:
            Expected score (probability of A winning)
        """
        return self._e(rating_a, rating_b, rd_b)
    
    def predict_match(
        self, rating_a: float, rd_a: float, rating_b: float, rd_b: float
    ) -> Dict[str, float]:
        """Predict match outcome.
        
        Args:
            rating_a: Team A's rating
            rd_a: Team A's rating deviation
            rating_b: Team B's rating
            rd_b: Team B's rating deviation
            
        Returns:
            Dictionary with predictions
        """
        prob_a = self.expected_score(rating_a, rd_a, rating_b, rd_b)
        prob_b = 1.0 - prob_a
        
        return {
            "team1_win_prob": prob_a,
            "team2_win_prob": prob_b,
            "confidence_a": 1.0 / (1.0 + rd_a / 100.0),  # Lower RD = higher confidence
            "confidence_b": 1.0 / (1.0 + rd_b / 100.0),
            "model": "glicko",
        }
    
    def update_ratings(
        self,
        rating: float,
        rd: float,
        sigma: float,
        results: List[Tuple[float, float, float]],
    ) -> Tuple[float, float, float]:
        """Update Glicko-2 ratings after matches.
        
        Args:
            rating: Current rating
            rd: Current rating deviation
            sigma: Current volatility
            results: List of (opponent_rating, opponent_rd, score) tuples
            
        Returns:
            Tuple of (new_rating, new_rd, new_sigma)
        """
        # Simplified Glicko-2 update
        # Full implementation would be more complex
        
        if not results:
            # Rating deviation increases with inactivity
            new_rd = min(math.sqrt(rd * rd + sigma * sigma), self.initial_rd)
            return rating, new_rd, sigma
        
        # Calculate variance and rating change
        variance_inv = 0.0
        delta = 0.0
        
        for opp_rating, opp_rd, score in results:
            e = self._e(rating, opp_rating, opp_rd)
            g_rd = self._g(opp_rd)
            
            variance_inv += g_rd * g_rd * e * (1 - e)
            delta += g_rd * (score - e)
        
        if variance_inv > 0:
            variance = 1.0 / variance_inv
            delta *= variance
            
            # Update rating and RD
            new_rd = 1.0 / math.sqrt(1.0 / (rd * rd) + 1.0 / variance)
            new_rating = rating + new_rd * new_rd * delta / variance
        else:
            new_rating = rating
            new_rd = rd
        
        return new_rating, new_rd, sigma
