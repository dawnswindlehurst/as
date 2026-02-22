"""bet365 bookmaker implementation."""
from typing import Dict, List, Optional
from bookmakers.base import BookmakerBase


class Bet365(BookmakerBase):
    """bet365 bookmaker implementation."""
    
    def __init__(self):
        super().__init__()
        self.type = "traditional"
    
    def get_odds(self, match_id: str, market_type: str) -> Optional[Dict]:
        """Fetch odds from bet365.
        
        Args:
            match_id: Match identifier
            market_type: Market type
            
        Returns:
            Odds dictionary
        """
        # TODO: Implement actual scraping/API integration
        return {
            "bookmaker": "bet365",
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
        # TODO: Implement actual scraping/API integration
        return ["match_winner", "handicap", "total_maps"]
