"""Closing Line Value (CLV) analysis."""
from typing import Dict, List
from database.db import get_db
from database.models import Bet
from edge.pinnacle_ref import PinnacleReference


class CLVAnalyzer:
    """Analyze Closing Line Value."""
    
    def __init__(self):
        self.pinnacle_ref = PinnacleReference()
    
    def calculate_clv_stats(self) -> Dict:
        """Calculate overall CLV statistics.
        
        Returns:
            Dictionary with CLV stats
        """
        with get_db() as db:
            bets_with_clv = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.clv.isnot(None)
            ).all()
            
            if not bets_with_clv:
                return {
                    "total_bets": 0,
                    "avg_clv": 0.0,
                    "positive_clv_rate": 0.0,
                }
            
            total = len(bets_with_clv)
            avg_clv = sum(b.clv for b in bets_with_clv) / total
            positive_clv = sum(1 for b in bets_with_clv if b.clv > 0)
            
            return {
                "total_bets": total,
                "avg_clv": avg_clv,
                "avg_clv_percent": avg_clv * 100,
                "positive_clv_count": positive_clv,
                "negative_clv_count": total - positive_clv,
                "positive_clv_rate": positive_clv / total,
            }
    
    def analyze_clv_by_confidence(self, ranges: List[tuple]) -> Dict:
        """Analyze CLV by confidence ranges.
        
        Args:
            ranges: List of (min, max) confidence tuples
            
        Returns:
            Dictionary with CLV by confidence range
        """
        results = {}
        
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.clv.isnot(None)
            ).all()
            
            for low, high in ranges:
                range_bets = [b for b in bets if low <= b.confidence < high]
                
                if range_bets:
                    avg_clv = sum(b.clv for b in range_bets) / len(range_bets)
                    positive = sum(1 for b in range_bets if b.clv > 0)
                    
                    results[f"{low:.0%}-{high:.0%}"] = {
                        "count": len(range_bets),
                        "avg_clv": avg_clv,
                        "avg_clv_percent": avg_clv * 100,
                        "positive_clv_rate": positive / len(range_bets),
                    }
        
        return results
    
    def get_clv_correlation_with_results(self) -> Dict:
        """Analyze correlation between CLV and actual results.
        
        Returns:
            Dictionary with correlation analysis
        """
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.clv.isnot(None),
                Bet.status.in_(["won", "lost"])
            ).all()
            
            if not bets:
                return {}
            
            positive_clv_bets = [b for b in bets if b.clv > 0]
            negative_clv_bets = [b for b in bets if b.clv <= 0]
            
            positive_clv_wins = sum(1 for b in positive_clv_bets if b.status == "won")
            negative_clv_wins = sum(1 for b in negative_clv_bets if b.status == "won")
            
            return {
                "positive_clv": {
                    "total": len(positive_clv_bets),
                    "wins": positive_clv_wins,
                    "win_rate": positive_clv_wins / len(positive_clv_bets) if positive_clv_bets else 0,
                },
                "negative_clv": {
                    "total": len(negative_clv_bets),
                    "wins": negative_clv_wins,
                    "win_rate": negative_clv_wins / len(negative_clv_bets) if negative_clv_bets else 0,
                },
            }
