"""Market registry."""
from typing import Dict, Type, Optional
from markets.base import MarketBase, MatchWinner, Handicap, TotalMaps


class MarketRegistry:
    """Registry for market types."""
    
    def __init__(self):
        self._markets: Dict[str, Type[MarketBase]] = {
            "match_winner": MatchWinner,
            "handicap": Handicap,
            "total_maps": TotalMaps,
        }
    
    def get(self, market_type: str) -> Optional[MarketBase]:
        """Get market instance.
        
        Args:
            market_type: Market type name
            
        Returns:
            Market instance or None
        """
        if market_type in self._markets:
            return self._markets[market_type]()
        return None
    
    def list_markets(self) -> list:
        """List all registered markets.
        
        Returns:
            List of market type names
        """
        return list(self._markets.keys())


# Global registry instance
market_registry = MarketRegistry()
