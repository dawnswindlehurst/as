"""Bookmaker-specific analysis."""
from typing import Dict, List
from database.db import get_db
from database.models import Bet, Odds
from utils.helpers import calculate_roi


class BookmakerAnalyzer:
    """Analyze performance by bookmaker."""
    
    def __init__(self):
        pass
    
    def analyze_by_bookmaker(self) -> Dict:
        """Analyze bets by bookmaker.
        
        Returns:
            Dictionary with analysis for each bookmaker
        """
        results = {}
        
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            bookmakers = set(b.bookmaker for b in bets)
            
            for bookmaker in bookmakers:
                bm_bets = [b for b in bets if b.bookmaker == bookmaker]
                results[bookmaker] = self._calculate_bookmaker_stats(bm_bets)
        
        return results
    
    def _calculate_bookmaker_stats(self, bets: List[Bet]) -> Dict:
        """Calculate statistics for a bookmaker.
        
        Args:
            bets: List of bets with this bookmaker
            
        Returns:
            Statistics dictionary
        """
        if not bets:
            return {}
        
        total_stake = sum(b.stake for b in bets)
        total_profit = sum(b.profit for b in bets)
        won_bets = sum(1 for b in bets if b.status == "won")
        
        avg_odds = sum(b.odds for b in bets) / len(bets)
        avg_edge = sum(b.edge for b in bets) / len(bets)
        
        # CLV stats
        bets_with_clv = [b for b in bets if b.clv is not None]
        avg_clv = sum(b.clv for b in bets_with_clv) / len(bets_with_clv) if bets_with_clv else 0.0
        
        return {
            "total_bets": len(bets),
            "won_bets": won_bets,
            "lost_bets": len(bets) - won_bets,
            "win_rate": won_bets / len(bets),
            "avg_odds": avg_odds,
            "avg_edge": avg_edge,
            "avg_clv": avg_clv,
            "total_stake": total_stake,
            "total_profit": total_profit,
            "roi": calculate_roi(total_profit, total_stake),
        }
    
    def compare_opening_closing_odds(self, bookmaker: str) -> Dict:
        """Compare opening and closing odds for a bookmaker.
        
        Args:
            bookmaker: Bookmaker name
            
        Returns:
            Comparison statistics
        """
        with get_db() as db:
            opening_odds = db.query(Odds).filter(
                Odds.bookmaker == bookmaker,
                Odds.is_opening == True
            ).all()
            
            closing_odds = db.query(Odds).filter(
                Odds.bookmaker == bookmaker,
                Odds.is_closing == True
            ).all()
            
            return {
                "total_opening": len(opening_odds),
                "total_closing": len(closing_odds),
                "avg_opening_team1": sum(o.team1_odds for o in opening_odds if o.team1_odds) / len(opening_odds) if opening_odds else 0,
                "avg_closing_team1": sum(o.team1_odds for o in closing_odds if o.team1_odds) / len(closing_odds) if closing_odds else 0,
            }
    
    def get_best_bookmaker_by_game(self, game: str) -> Dict:
        """Find best bookmaker for a specific game.
        
        Args:
            game: Game name
            
        Returns:
            Best bookmaker information
        """
        with get_db() as db:
            bets = db.query(Bet).join(Bet.match).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"]),
                Bet.match.has(game=game)
            ).all()
            
            bookmakers = set(b.bookmaker for b in bets)
            bookmaker_stats = {}
            
            for bookmaker in bookmakers:
                bm_bets = [b for b in bets if b.bookmaker == bookmaker]
                bookmaker_stats[bookmaker] = self._calculate_bookmaker_stats(bm_bets)
            
            if not bookmaker_stats:
                return {}
            
            # Find bookmaker with best ROI
            best_bm = max(bookmaker_stats.items(), key=lambda x: x[1].get("roi", 0))
            
            return {
                "game": game,
                "best_bookmaker": best_bm[0],
                **best_bm[1],
            }
