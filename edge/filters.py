"""Bet filters for screening opportunities."""
from typing import Dict, List
from datetime import datetime, timedelta


class BetFilters:
    """Filters for screening betting opportunities."""
    
    def __init__(self):
        pass
    
    def filter_by_confidence(
        self, opportunities: List[Dict], min_confidence: float
    ) -> List[Dict]:
        """Filter opportunities by minimum confidence.
        
        Args:
            opportunities: List of opportunities
            min_confidence: Minimum model probability
            
        Returns:
            Filtered opportunities
        """
        return [
            opp for opp in opportunities
            if opp.get("model_probability", 0) >= min_confidence
        ]
    
    def filter_by_edge(
        self, opportunities: List[Dict], min_edge: float, max_edge: float = 1.0
    ) -> List[Dict]:
        """Filter opportunities by edge range.
        
        Args:
            opportunities: List of opportunities
            min_edge: Minimum edge
            max_edge: Maximum edge
            
        Returns:
            Filtered opportunities
        """
        return [
            opp for opp in opportunities
            if min_edge <= opp.get("edge", 0) <= max_edge
        ]
    
    def filter_by_bookmaker(
        self, opportunities: List[Dict], bookmakers: List[str]
    ) -> List[Dict]:
        """Filter opportunities by bookmaker.
        
        Args:
            opportunities: List of opportunities
            bookmakers: List of allowed bookmakers
            
        Returns:
            Filtered opportunities
        """
        return [
            opp for opp in opportunities
            if opp.get("bookmaker") in bookmakers
        ]
    
    def filter_by_game(
        self, opportunities: List[Dict], games: List[str]
    ) -> List[Dict]:
        """Filter opportunities by game.
        
        Args:
            opportunities: List of opportunities
            games: List of allowed games
            
        Returns:
            Filtered opportunities
        """
        return [
            opp for opp in opportunities
            if opp.get("game") in games
        ]
    
    def filter_by_time_to_match(
        self, opportunities: List[Dict], min_hours: float = 0, max_hours: float = 24
    ) -> List[Dict]:
        """Filter opportunities by time until match starts.
        
        Args:
            opportunities: List of opportunities
            min_hours: Minimum hours until match
            max_hours: Maximum hours until match
            
        Returns:
            Filtered opportunities
        """
        now = datetime.utcnow()
        filtered = []
        
        for opp in opportunities:
            match_time = opp.get("match_time")
            if not match_time:
                continue
            
            hours_until = (match_time - now).total_seconds() / 3600
            
            if min_hours <= hours_until <= max_hours:
                filtered.append(opp)
        
        return filtered
