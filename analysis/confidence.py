"""Confidence-based analysis."""
from typing import Dict, List
from config.constants import CONFIDENCE_RANGES
from database.db import get_db
from database.models import Bet
from utils.helpers import calculate_roi


class ConfidenceAnalyzer:
    """Analyze betting performance by confidence ranges."""
    
    def __init__(self):
        self.confidence_ranges = CONFIDENCE_RANGES
    
    def analyze_by_confidence(self) -> Dict:
        """Analyze bets by confidence ranges.
        
        Returns:
            Dictionary with analysis for each confidence range
        """
        results = {}
        
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            for low, high in self.confidence_ranges:
                range_bets = [b for b in bets if low <= b.confidence < high]
                
                if range_bets:
                    results[f"{low:.0%}-{high:.0%}"] = self._calculate_range_stats(range_bets)
        
        return results
    
    def _calculate_range_stats(self, bets: List[Bet]) -> Dict:
        """Calculate statistics for a confidence range.
        
        Args:
            bets: List of bets in the range
            
        Returns:
            Statistics dictionary
        """
        total_stake = sum(b.stake for b in bets)
        total_profit = sum(b.profit for b in bets)
        won_bets = sum(1 for b in bets if b.status == "won")
        
        avg_confidence = sum(b.confidence for b in bets) / len(bets)
        avg_odds = sum(b.odds for b in bets) / len(bets)
        avg_edge = sum(b.edge for b in bets) / len(bets)
        
        return {
            "total_bets": len(bets),
            "won_bets": won_bets,
            "lost_bets": len(bets) - won_bets,
            "win_rate": won_bets / len(bets),
            "avg_confidence": avg_confidence,
            "avg_odds": avg_odds,
            "avg_edge": avg_edge,
            "total_stake": total_stake,
            "total_profit": total_profit,
            "roi": calculate_roi(total_profit, total_stake),
        }
    
    def get_optimal_confidence_range(self) -> Dict:
        """Find the most profitable confidence range.
        
        Returns:
            Dictionary with optimal range information
        """
        analysis = self.analyze_by_confidence()
        
        if not analysis:
            return {}
        
        # Find range with best ROI
        best_range = max(analysis.items(), key=lambda x: x[1]["roi"])
        
        return {
            "range": best_range[0],
            **best_range[1],
        }
