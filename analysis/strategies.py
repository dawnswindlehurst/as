"""Strategy analysis."""
from typing import Dict, List
from database.db import get_db
from database.models import Bet
from utils.helpers import calculate_roi


class StrategyAnalyzer:
    """Analyze different betting strategies."""
    
    def __init__(self):
        pass
    
    def analyze_by_edge_range(self, edge_ranges: List[tuple]) -> Dict:
        """Analyze bets by edge ranges.
        
        Args:
            edge_ranges: List of (min, max) edge tuples
            
        Returns:
            Dictionary with analysis for each edge range
        """
        results = {}
        
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            for low, high in edge_ranges:
                range_bets = [b for b in bets if low <= b.edge < high]
                
                if range_bets:
                    results[f"{low:.1%}-{high:.1%}"] = self._calculate_stats(range_bets)
        
        return results
    
    def analyze_by_market_type(self) -> Dict:
        """Analyze bets by market type.
        
        Returns:
            Dictionary with analysis for each market type
        """
        results = {}
        
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            market_types = set(b.market_type for b in bets)
            
            for market_type in market_types:
                market_bets = [b for b in bets if b.market_type == market_type]
                results[market_type] = self._calculate_stats(market_bets)
        
        return results
    
    def analyze_favorites_vs_underdogs(self) -> Dict:
        """Analyze performance on favorites vs underdogs.
        
        Returns:
            Dictionary with comparison
        """
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            # Favorites are odds < 2.0, underdogs are odds >= 2.0
            favorites = [b for b in bets if b.odds < 2.0]
            underdogs = [b for b in bets if b.odds >= 2.0]
            
            return {
                "favorites": self._calculate_stats(favorites),
                "underdogs": self._calculate_stats(underdogs),
            }
    
    def _calculate_stats(self, bets: List[Bet]) -> Dict:
        """Calculate statistics for a list of bets.
        
        Args:
            bets: List of bets
            
        Returns:
            Statistics dictionary
        """
        if not bets:
            return {
                "total_bets": 0,
                "win_rate": 0.0,
                "roi": 0.0,
            }
        
        total_stake = sum(b.stake for b in bets)
        total_profit = sum(b.profit for b in bets)
        won_bets = sum(1 for b in bets if b.status == "won")
        
        return {
            "total_bets": len(bets),
            "won_bets": won_bets,
            "lost_bets": len(bets) - won_bets,
            "win_rate": won_bets / len(bets),
            "total_stake": total_stake,
            "total_profit": total_profit,
            "roi": calculate_roi(total_profit, total_stake),
        }
