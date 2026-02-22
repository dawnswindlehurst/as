"""Helper functions and utilities."""
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np


def get_confidence_range(confidence: float) -> Tuple[float, float]:
    """Get the confidence range bucket for a given confidence value.
    
    Args:
        confidence: Confidence value between 0 and 1
        
    Returns:
        Tuple of (lower_bound, upper_bound) for the confidence range
    """
    from config.constants import CONFIDENCE_RANGES
    
    for lower, upper in CONFIDENCE_RANGES:
        if lower <= confidence < upper:
            return (lower, upper)
    
    # Handle 100% case
    if confidence >= 0.95:
        return (0.95, 1.00)
    
    # Default to lowest range
    return (0.55, 0.60)


def format_odds(decimal_odds: float) -> str:
    """Format decimal odds for display.
    
    Args:
        decimal_odds: Decimal odds value
        
    Returns:
        Formatted odds string
    """
    return f"{decimal_odds:.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a decimal value as percentage.
    
    Args:
        value: Decimal value (0-1)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_currency(value: float, currency: str = "BRL") -> str:
    """Format a value as currency.
    
    Args:
        value: Currency value
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "BRL":
        return f"R$ {value:,.2f}"
    else:
        return f"{currency} {value:,.2f}"


def calculate_roi(profit: float, stake: float) -> float:
    """Calculate Return on Investment.
    
    Args:
        profit: Total profit
        stake: Total stake
        
    Returns:
        ROI as decimal
    """
    if stake == 0:
        return 0.0
    return profit / stake


def calculate_implied_probability(decimal_odds: float) -> float:
    """Calculate implied probability from decimal odds.
    
    Args:
        decimal_odds: Decimal odds
        
    Returns:
        Implied probability (0-1)
    """
    if decimal_odds <= 0:
        return 0.0
    return 1.0 / decimal_odds


def calculate_edge(model_prob: float, market_prob: float) -> float:
    """Calculate betting edge.
    
    Args:
        model_prob: Model's probability estimate
        market_prob: Market implied probability
        
    Returns:
        Edge as decimal
    """
    return model_prob - market_prob


def calculate_ev(probability: float, decimal_odds: float, stake: float = 1.0) -> float:
    """Calculate expected value.
    
    Args:
        probability: Win probability (0-1)
        decimal_odds: Decimal odds
        stake: Stake amount
        
    Returns:
        Expected value
    """
    return (probability * (decimal_odds - 1) * stake) - ((1 - probability) * stake)


def moving_average(values: List[float], window: int) -> List[float]:
    """Calculate moving average.
    
    Args:
        values: List of values
        window: Window size
        
    Returns:
        List of moving averages
    """
    if len(values) < window:
        return values
    
    return list(np.convolve(values, np.ones(window) / window, mode='valid'))


def get_streak_info(results: List[bool]) -> dict:
    """Analyze streak information from results.
    
    Args:
        results: List of boolean results (True = win, False = loss)
        
    Returns:
        Dictionary with streak information
    """
    if not results:
        return {
            "current_streak": 0,
            "current_streak_type": None,
            "longest_win_streak": 0,
            "longest_loss_streak": 0,
        }
    
    current_streak = 1
    current_type = results[-1]
    longest_win = 0
    longest_loss = 0
    temp_win = 0
    temp_loss = 0
    
    for result in results:
        if result:
            temp_win += 1
            temp_loss = 0
            longest_win = max(longest_win, temp_win)
        else:
            temp_loss += 1
            temp_win = 0
            longest_loss = max(longest_loss, temp_loss)
    
    # Count current streak
    for i in range(len(results) - 1, -1, -1):
        if results[i] == current_type:
            current_streak = len(results) - i
        else:
            break
    
    return {
        "current_streak": current_streak,
        "current_streak_type": "win" if current_type else "loss",
        "longest_win_streak": longest_win,
        "longest_loss_streak": longest_loss,
    }


def days_between(date1: datetime, date2: datetime) -> int:
    """Calculate days between two dates.
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        Number of days
    """
    return abs((date2 - date1).days)


def parse_team_name(name: str) -> str:
    """Normalize team name for consistent matching.
    
    Args:
        name: Team name
        
    Returns:
        Normalized team name
    """
    # Remove common prefixes/suffixes
    name = name.strip()
    name = name.replace("Esports", "").replace("Gaming", "").replace("eSports", "")
    name = name.strip()
    return name
