"""Metrics aggregator to combine all metrics calculators."""
from typing import Dict, List, Optional
from datetime import datetime
from database.models import Bet
from database.db import get_db

from .basic import BasicMetrics
from .risk import RiskMetrics
from .calibration import CalibrationMetrics
from .clv import CLVMetrics
from .streaks import StreakMetrics
from .bankroll import BankrollMetrics


class MetricsAggregator:
    """Aggregate all metrics calculations."""
    
    def __init__(
        self, 
        bets: Optional[List[Bet]] = None,
        initial_bankroll: float = 1000.0,
        risk_free_rate: float = 0.0
    ):
        """Initialize metrics aggregator.
        
        Args:
            bets: List of bets to analyze (if None, loads from database)
            initial_bankroll: Initial bankroll amount for paper trading
            risk_free_rate: Annual risk-free rate for risk calculations
        """
        if bets is None:
            bets = self._load_bets_from_db()
        
        self.bets = bets
        self.initial_bankroll = initial_bankroll
        self.risk_free_rate = risk_free_rate
        
        # Initialize all metrics calculators
        self.basic = BasicMetrics(bets)
        self.risk = RiskMetrics(bets)
        self.calibration = CalibrationMetrics(bets)
        self.clv = CLVMetrics(bets)
        self.streaks = StreakMetrics(bets)
        self.bankroll = BankrollMetrics(bets, initial_bankroll)
    
    def calculate_all(self) -> Dict:
        """Calculate all metrics.
        
        Returns:
            Dictionary containing all calculated metrics
        """
        return {
            'basic': self.basic.calculate(),
            'risk': self.risk.calculate(self.risk_free_rate),
            'calibration': self.calibration.calculate(),
            'clv': self.clv.calculate(),
            'streaks': self.streaks.calculate(),
            'bankroll': self.bankroll.calculate(),
            'metadata': {
                'total_bets': len(self.bets),
                'settled_bets': len([b for b in self.bets if b.status in ['won', 'lost']]),
                'pending_bets': len([b for b in self.bets if b.status == 'pending']),
                'initial_bankroll': self.initial_bankroll,
            }
        }
    
    def calculate_by_sport(self, sports: List[str]) -> Dict:
        """Calculate metrics segmented by sport.
        
        Args:
            sports: List of sport names to analyze
            
        Returns:
            Dictionary with metrics for each sport
        """
        results = {}
        
        for sport in sports:
            sport_bets = [
                b for b in self.bets 
                if hasattr(b.match, 'game') and b.match.game == sport
            ]
            
            if sport_bets:
                aggregator = MetricsAggregator(
                    sport_bets, 
                    self.initial_bankroll, 
                    self.risk_free_rate
                )
                results[sport] = aggregator.calculate_all()
        
        return results
    
    def calculate_by_market(self, markets: List[str]) -> Dict:
        """Calculate metrics segmented by market type.
        
        Args:
            markets: List of market types to analyze
            
        Returns:
            Dictionary with metrics for each market
        """
        results = {}
        
        for market in markets:
            market_bets = [b for b in self.bets if b.market_type == market]
            
            if market_bets:
                aggregator = MetricsAggregator(
                    market_bets, 
                    self.initial_bankroll, 
                    self.risk_free_rate
                )
                results[market] = aggregator.calculate_all()
        
        return results
    
    def calculate_by_confidence_range(self, ranges: List[tuple]) -> Dict:
        """Calculate metrics segmented by confidence ranges.
        
        Args:
            ranges: List of (min, max, label) tuples
            
        Returns:
            Dictionary with metrics for each range
        """
        results = {}
        
        for range_tuple in ranges:
            min_conf, max_conf = range_tuple[0], range_tuple[1]
            label = range_tuple[2] if len(range_tuple) > 2 else f"{min_conf}-{max_conf}"
            
            range_bets = [
                b for b in self.bets 
                if min_conf <= b.confidence < max_conf
            ]
            
            if range_bets:
                aggregator = MetricsAggregator(
                    range_bets, 
                    self.initial_bankroll, 
                    self.risk_free_rate
                )
                results[label] = aggregator.calculate_all()
        
        return results
    
    def calculate_by_odds_range(self, ranges: List[tuple]) -> Dict:
        """Calculate metrics segmented by odds ranges.
        
        Args:
            ranges: List of (min, max, label) tuples
            
        Returns:
            Dictionary with metrics for each range
        """
        results = {}
        
        for range_tuple in ranges:
            min_odds, max_odds = range_tuple[0], range_tuple[1]
            label = range_tuple[2] if len(range_tuple) > 2 else f"{min_odds}-{max_odds}"
            
            range_bets = [
                b for b in self.bets 
                if min_odds <= b.odds < max_odds
            ]
            
            if range_bets:
                aggregator = MetricsAggregator(
                    range_bets, 
                    self.initial_bankroll, 
                    self.risk_free_rate
                )
                results[label] = aggregator.calculate_all()
        
        return results
    
    def _load_bets_from_db(self) -> List[Bet]:
        """Load all confirmed bets from database.
        
        Returns:
            List of Bet objects
        """
        with get_db() as db:
            bets = db.query(Bet).filter(Bet.confirmed == True).all()
            return list(bets)
