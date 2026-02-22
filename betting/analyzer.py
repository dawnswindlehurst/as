"""Bet analyzer - analyze betting performance."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database.db import get_db
from database.models import Bet
from sqlalchemy import func
from utils.helpers import calculate_roi


class BetAnalyzer:
    """Analyze betting performance."""
    
    def __init__(self):
        pass
    
    def get_overall_stats(self) -> Dict:
        """Get overall betting statistics.
        
        Returns:
            Dictionary with overall stats
        """
        with get_db() as db:
            settled_bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            if not settled_bets:
                return self._empty_stats()
            
            total_stake = sum(b.stake for b in settled_bets)
            total_profit = sum(b.profit for b in settled_bets)
            won_bets = sum(1 for b in settled_bets if b.status == "won")
            
            avg_odds = sum(b.odds for b in settled_bets) / len(settled_bets)
            avg_edge = sum(b.edge for b in settled_bets) / len(settled_bets)
            
            # CLV stats
            bets_with_clv = [b for b in settled_bets if b.clv is not None]
            avg_clv = sum(b.clv for b in bets_with_clv) / len(bets_with_clv) if bets_with_clv else 0.0
            
            return {
                "total_bets": len(settled_bets),
                "won_bets": won_bets,
                "lost_bets": len(settled_bets) - won_bets,
                "win_rate": won_bets / len(settled_bets),
                "total_stake": total_stake,
                "total_profit": total_profit,
                "roi": calculate_roi(total_profit, total_stake),
                "avg_odds": avg_odds,
                "avg_edge": avg_edge,
                "avg_clv": avg_clv,
            }
    
    def get_stats_by_game(self) -> Dict[str, Dict]:
        """Get statistics by game.
        
        Returns:
            Dictionary of {game: stats}
        """
        stats_by_game = {}
        
        with get_db() as db:
            bets = db.query(Bet).join(Bet.match).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            games = set(b.match.game for b in bets if b.match)
            
            for game in games:
                game_bets = [b for b in bets if b.match and b.match.game == game]
                stats_by_game[game] = self._calculate_stats(game_bets)
        
        return stats_by_game
    
    def get_stats_by_confidence(self, ranges: List[tuple]) -> Dict:
        """Get statistics by confidence range.
        
        Args:
            ranges: List of (min, max) confidence tuples
            
        Returns:
            Dictionary with stats for each range
        """
        stats = {}
        
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            for low, high in ranges:
                range_bets = [b for b in bets if low <= b.confidence < high]
                if range_bets:
                    stats[f"{low:.0%}-{high:.0%}"] = self._calculate_stats(range_bets)
        
        return stats
    
    def get_stats_by_bookmaker(self) -> Dict[str, Dict]:
        """Get statistics by bookmaker.
        
        Returns:
            Dictionary of {bookmaker: stats}
        """
        stats_by_bookmaker = {}
        
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            bookmakers = set(b.bookmaker for b in bets)
            
            for bookmaker in bookmakers:
                bm_bets = [b for b in bets if b.bookmaker == bookmaker]
                stats_by_bookmaker[bookmaker] = self._calculate_stats(bm_bets)
        
        return stats_by_bookmaker
    
    def _calculate_stats(self, bets: List[Bet]) -> Dict:
        """Calculate statistics for a list of bets.
        
        Args:
            bets: List of Bet objects
            
        Returns:
            Statistics dictionary
        """
        if not bets:
            return self._empty_stats()
        
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
    
    def _empty_stats(self) -> Dict:
        """Return empty stats dictionary."""
        return {
            "total_bets": 0,
            "won_bets": 0,
            "lost_bets": 0,
            "win_rate": 0.0,
            "total_stake": 0.0,
            "total_profit": 0.0,
            "roi": 0.0,
        }
