"""Base class for game implementations."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class GameBase(ABC):
    """Abstract base class for game integrations.
    
    Each game should inherit from this class and implement
    the required methods. This enables plug & play functionality.
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.category = "pc"  # Override in mobile games
        self.has_maps = False
        self.has_draft = False
    
    @abstractmethod
    def get_upcoming_matches(self) -> List[Dict]:
        """Fetch upcoming matches for this game.
        
        Returns:
            List of match dictionaries
        """
        pass
    
    @abstractmethod
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get detailed information about a specific match.
        
        Args:
            match_id: Unique match identifier
            
        Returns:
            Match details dictionary or None
        """
        pass
    
    @abstractmethod
    def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get team statistics.
        
        Args:
            team_name: Team name
            
        Returns:
            Team statistics dictionary or None
        """
        pass
    
    def get_supported_markets(self) -> List[str]:
        """Get list of supported market types for this game.
        
        Returns:
            List of market types
        """
        markets = ["match_winner", "handicap"]
        
        if self.has_maps:
            markets.extend(["total_maps", "map_winner"])
        
        return markets
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(category={self.category})"
