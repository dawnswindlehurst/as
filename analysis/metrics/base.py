"""Base metrics calculator class."""
from typing import Dict, List, Optional
from datetime import datetime
from database.models import Bet


class MetricsCalculator:
    """Base class for metrics calculation."""
    
    def __init__(self, bets: Optional[List[Bet]] = None):
        """Initialize metrics calculator.
        
        Args:
            bets: List of bet objects to calculate metrics for
        """
        self.bets = bets or []
    
    def filter_bets(
        self,
        sport: Optional[str] = None,
        market: Optional[str] = None,
        model: Optional[str] = None,
        confidence_range: Optional[tuple] = None,
        odds_range: Optional[tuple] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Bet]:
        """Filter bets by various criteria.
        
        Args:
            sport: Filter by sport/game
            market: Filter by market type
            model: Filter by model type
            confidence_range: Tuple of (min, max) confidence
            odds_range: Tuple of (min, max) odds
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Filtered list of bets
        """
        filtered = self.bets
        
        if sport:
            filtered = [b for b in filtered if hasattr(b.match, 'game') and b.match.game == sport]
        
        if market:
            filtered = [b for b in filtered if b.market_type == market]
        
        if confidence_range:
            min_conf, max_conf = confidence_range
            filtered = [b for b in filtered if min_conf <= b.confidence < max_conf]
        
        if odds_range:
            min_odds, max_odds = odds_range
            filtered = [b for b in filtered if min_odds <= b.odds < max_odds]
        
        if start_date:
            filtered = [b for b in filtered if b.created_at >= start_date]
        
        if end_date:
            filtered = [b for b in filtered if b.created_at <= end_date]
        
        return filtered
    
    def calculate(self) -> Dict:
        """Calculate metrics. To be overridden by subclasses.
        
        Returns:
            Dictionary with calculated metrics
        """
        raise NotImplementedError("Subclasses must implement calculate()")
