"""Pinnacle reference for CLV tracking."""
from typing import Dict, Optional
from bookmakers.registry import bookmaker_registry


class PinnacleReference:
    """Use Pinnacle as sharp market reference for CLV calculation."""
    
    def __init__(self):
        self.pinnacle = bookmaker_registry.get("Pinnacle")
    
    def get_closing_odds(self, match_id: str, market_type: str) -> Optional[Dict]:
        """Get Pinnacle closing odds.
        
        Args:
            match_id: Match ID
            market_type: Market type
            
        Returns:
            Closing odds dictionary
        """
        if not self.pinnacle:
            return None
        
        # TODO: Implement actual closing odds fetching
        # This would need to track odds over time and identify closing line
        return None
    
    def calculate_clv(self, bet_odds: float, closing_odds: float) -> float:
        """Calculate Closing Line Value.
        
        Args:
            bet_odds: Odds when bet was placed
            closing_odds: Pinnacle closing odds
            
        Returns:
            CLV as decimal
        """
        if closing_odds <= 0:
            return 0.0
        
        bet_prob = 1.0 / bet_odds
        closing_prob = 1.0 / closing_odds
        
        return bet_prob - closing_prob
    
    def calculate_clv_percent(self, bet_odds: float, closing_odds: float) -> float:
        """Calculate CLV as percentage.
        
        Args:
            bet_odds: Odds when bet was placed
            closing_odds: Pinnacle closing odds
            
        Returns:
            CLV as percentage
        """
        return self.calculate_clv(bet_odds, closing_odds) * 100
