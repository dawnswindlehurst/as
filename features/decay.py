"""Time decay functions for features."""
import math
from datetime import datetime, timedelta
from config.constants import DECAY_HALF_LIFE_DAYS


def exponential_decay(days_ago: int, half_life: int = DECAY_HALF_LIFE_DAYS) -> float:
    """Calculate exponential decay weight based on time.
    
    Args:
        days_ago: Number of days since the data point
        half_life: Half-life in days
        
    Returns:
        Decay weight (0-1)
    """
    return math.exp(-math.log(2) * days_ago / half_life)


def linear_decay(days_ago: int, max_days: int = 180) -> float:
    """Calculate linear decay weight.
    
    Args:
        days_ago: Number of days since the data point
        max_days: Maximum days to consider
        
    Returns:
        Decay weight (0-1)
    """
    if days_ago >= max_days:
        return 0.0
    return 1.0 - (days_ago / max_days)


def calculate_weighted_average(values: list, weights: list) -> float:
    """Calculate weighted average.
    
    Args:
        values: List of values
        weights: List of weights
        
    Returns:
        Weighted average
    """
    if not values or not weights or len(values) != len(weights):
        return 0.0
    
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    
    return sum(v * w for v, w in zip(values, weights)) / total_weight
