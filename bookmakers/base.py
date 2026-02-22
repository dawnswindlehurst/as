"""Base class for bookmaker implementations."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class BookmakerBase(ABC):
    """Abstract base class for bookmaker integrations.
    
    Each bookmaker should inherit from this class and implement
    the required methods. This enables plug & play functionality.
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.type = "traditional"  # Override in crypto bookmakers
    
    @abstractmethod
    def get_odds(self, match_id: str, market_type: str) -> Optional[Dict]:
        """Fetch odds for a specific match and market.
        
        Args:
            match_id: Unique match identifier
            market_type: Type of market (e.g., 'match_winner', 'handicap')
            
        Returns:
            Dictionary with odds data or None if unavailable
        """
        pass
    
    @abstractmethod
    def get_available_markets(self, match_id: str) -> List[str]:
        """Get list of available markets for a match.
        
        Args:
            match_id: Unique match identifier
            
        Returns:
            List of available market types
        """
        pass
    
    def is_available(self) -> bool:
        """Check if bookmaker is available/accessible.
        
        Returns:
            True if bookmaker is accessible
        """
        return True
    
    def get_margin(self, odds: Dict) -> float:
        """Calculate bookmaker margin from odds.
        
        Args:
            odds: Dictionary with odds values
            
        Returns:
            Margin as decimal
        """
        if not odds:
            return 0.0
        
        total_prob = 0.0
        for value in odds.values():
            if isinstance(value, (int, float)) and value > 0:
                total_prob += 1.0 / value
        
        return max(0.0, total_prob - 1.0)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.type})"
