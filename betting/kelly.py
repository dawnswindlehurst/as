"""Kelly Criterion for bet sizing."""
import math
from typing import Dict, Optional
from config.settings import KELLY_FRACTION


class KellyCriterion:
    """Kelly Criterion for optimal bet sizing."""
    
    def __init__(self, kelly_fraction: float = KELLY_FRACTION, max_bet_percent: float = 0.1):
        """Initialize Kelly Criterion.
        
        Args:
            kelly_fraction: Fraction of Kelly to use (0-1, typically 0.25)
            max_bet_percent: Maximum percentage of bankroll per bet (default 0.1 = 10%)
        """
        self.kelly_fraction = kelly_fraction
        self.max_bet_percent = max_bet_percent
    
    def calculate_stake(
        self, bankroll: float, probability: float, odds: float
    ) -> float:
        """Calculate optimal stake using Kelly Criterion.
        
        Args:
            bankroll: Total bankroll
            probability: Win probability (0-1)
            odds: Decimal odds
            
        Returns:
            Stake amount
        """
        if probability <= 0 or probability >= 1 or odds <= 1:
            return 0.0
        
        # Kelly formula: f = (bp - q) / b
        # where:
        # f = fraction of bankroll to bet
        # b = odds - 1 (net odds)
        # p = probability of winning
        # q = probability of losing (1 - p)
        
        b = odds - 1.0
        p = probability
        q = 1.0 - p
        
        kelly_percent = (b * p - q) / b
        
        # Apply fractional Kelly
        fractional_kelly = kelly_percent * self.kelly_fraction
        
        # Don't bet if Kelly is negative (no edge)
        if fractional_kelly <= 0:
            return 0.0
        
        # Cap at maximum percentage of bankroll
        fractional_kelly = min(fractional_kelly, self.max_bet_percent)
        
        return bankroll * fractional_kelly
    
    def calculate_kelly_percent(
        self, probability: float, odds: float
    ) -> float:
        """Calculate Kelly percentage (without bankroll).
        
        Args:
            probability: Win probability (0-1)
            odds: Decimal odds
            
        Returns:
            Kelly percentage (0-1)
        """
        if probability <= 0 or probability >= 1 or odds <= 1:
            return 0.0
        
        b = odds - 1.0
        p = probability
        q = 1.0 - p
        
        kelly_percent = (b * p - q) / b
        
        return max(0.0, kelly_percent * self.kelly_fraction)
