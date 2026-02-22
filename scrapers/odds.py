"""Odds scraper - aggregate odds from multiple bookmakers."""
from typing import List, Dict, Optional
from datetime import datetime
from bookmakers.registry import bookmaker_registry


class OddsScraper:
    """Scraper for aggregating odds from multiple bookmakers."""
    
    def __init__(self):
        self.bookmakers = bookmaker_registry.get_all()
    
    def fetch_odds(self, match_id: str, market_type: str = "match_winner") -> List[Dict]:
        """Fetch odds for a match from all bookmakers.
        
        Args:
            match_id: Match identifier
            market_type: Market type
            
        Returns:
            List of odds dictionaries from different bookmakers
        """
        odds_list = []
        
        for bookmaker in self.bookmakers:
            try:
                odds = bookmaker.get_odds(match_id, market_type)
                if odds:
                    odds_list.append(odds)
            except Exception as e:
                # Log error but continue with other bookmakers
                pass
        
        return odds_list
    
    def get_best_odds(self, match_id: str, market_type: str, selection: str) -> Optional[Dict]:
        """Find best odds for a selection across all bookmakers.
        
        Args:
            match_id: Match identifier
            market_type: Market type
            selection: Selection (e.g., 'team1', 'team2')
            
        Returns:
            Dictionary with best odds and bookmaker
        """
        odds_list = self.fetch_odds(match_id, market_type)
        
        if not odds_list:
            return None
        
        best_odds = None
        best_value = 0.0
        
        for odds in odds_list:
            value = odds.get(f"{selection}_odds", 0.0)
            if value and value > best_value:
                best_value = value
                best_odds = {
                    "bookmaker": odds["bookmaker"],
                    "odds": value,
                    "market_type": market_type,
                    "selection": selection,
                }
        
        return best_odds
