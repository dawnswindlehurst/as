"""Pinnacle bookmaker - sharp market reference."""
from typing import Dict, List, Optional
from bookmakers.base import BookmakerBase


class Pinnacle(BookmakerBase):
    """Pinnacle bookmaker implementation.
    
    Pinnacle is used as the sharp market reference due to:
    - Low margins
    - High limits
    - Professional bettor friendly
    """
    
    def __init__(self):
        super().__init__()
        self.type = "traditional"
        self.is_sharp_reference = True
    
    def get_odds(self, match_id: str, market_type: str) -> Optional[Dict]:
        """Fetch odds from Pinnacle.
        
        Args:
            match_id: Match identifier
            market_type: Market type
            
        Returns:
            Odds dictionary
        """
        # TODO: Implement actual API integration
        # For now, returns mock data structure
        return {
            "bookmaker": "Pinnacle",
            "match_id": match_id,
            "market_type": market_type,
            "team1_odds": None,
            "team2_odds": None,
            "timestamp": None,
        }
    
    def get_available_markets(self, match_id: str) -> List[str]:
        """Get available markets for a match.
        
        Args:
            match_id: Match identifier
            
        Returns:
            List of market types
        """
        # TODO: Implement actual API integration
        return ["match_winner", "handicap", "total_maps"]
