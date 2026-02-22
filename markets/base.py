"""Base class for market implementations."""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class MarketBase(ABC):
    """Abstract base class for market types.
    
    Each market type should inherit from this class.
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.requires_line = False
    
    @abstractmethod
    def calculate_probability(self, odds: float) -> float:
        """Calculate implied probability from odds.
        
        Args:
            odds: Decimal odds
            
        Returns:
            Implied probability (0-1)
        """
        pass
    
    @abstractmethod
    def validate_selection(self, selection: str) -> bool:
        """Validate if selection is valid for this market.
        
        Args:
            selection: Selection string
            
        Returns:
            True if valid
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class MatchWinner(MarketBase):
    """Match winner market (moneyline)."""
    
    def calculate_probability(self, odds: float) -> float:
        """Calculate implied probability."""
        if odds <= 0:
            return 0.0
        return 1.0 / odds
    
    def validate_selection(self, selection: str) -> bool:
        """Validate selection."""
        return selection.lower() in ["team1", "team2", "home", "away"]


class Handicap(MarketBase):
    """Handicap/Spread market."""
    
    def __init__(self):
        super().__init__()
        self.requires_line = True
    
    def calculate_probability(self, odds: float) -> float:
        """Calculate implied probability."""
        if odds <= 0:
            return 0.0
        return 1.0 / odds
    
    def validate_selection(self, selection: str) -> bool:
        """Validate selection."""
        return selection.lower() in ["team1", "team2", "home", "away"]


class TotalMaps(MarketBase):
    """Total maps over/under market."""
    
    def __init__(self):
        super().__init__()
        self.requires_line = True
    
    def calculate_probability(self, odds: float) -> float:
        """Calculate implied probability."""
        if odds <= 0:
            return 0.0
        return 1.0 / odds
    
    def validate_selection(self, selection: str) -> bool:
        """Validate selection."""
        return selection.lower() in ["over", "under"]
