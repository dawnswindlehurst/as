"""Bet settler - settle completed bets."""
from typing import List
from datetime import datetime
from database.db import get_db
from database.models import Bet, Match
from utils.logger import log


class BetSettler:
    """Settle completed bets based on match results."""
    
    def __init__(self):
        pass
    
    def settle_bets(self):
        """Settle all unsettled bets for finished matches."""
        with get_db() as db:
            # Get unsettled bets with finished matches
            unsettled_bets = db.query(Bet).join(Match).filter(
                Bet.status == "pending",
                Bet.confirmed == True,
                Match.finished == True
            ).all()
            
            log.info(f"Settling {len(unsettled_bets)} bets")
            
            for bet in unsettled_bets:
                self._settle_bet(bet)
    
    def _settle_bet(self, bet: Bet):
        """Settle a single bet.
        
        Args:
            bet: Bet object
        """
        match = bet.match
        
        if not match or not match.finished:
            return
        
        # Determine if bet won
        is_win = self._check_bet_result(bet, match)
        
        if is_win:
            bet.status = "won"
            bet.profit = (bet.odds - 1.0) * bet.stake
        else:
            bet.status = "lost"
            bet.profit = -bet.stake
        
        bet.settled_at = datetime.utcnow()
        
        log.info(f"Settled bet {bet.id}: {bet.status} (profit: {bet.profit:.2f})")
    
    def _check_bet_result(self, bet: Bet, match: Match) -> bool:
        """Check if bet won.
        
        Args:
            bet: Bet object
            match: Match object
            
        Returns:
            True if bet won
        """
        if bet.market_type == "match_winner":
            if bet.selection == "team1":
                return match.winner == match.team1
            elif bet.selection == "team2":
                return match.winner == match.team2
        
        # TODO: Implement other market types
        
        return False
    
    def get_settlement_stats(self) -> dict:
        """Get settlement statistics.
        
        Returns:
            Dictionary with settlement stats
        """
        with get_db() as db:
            total_bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).count()
            
            won_bets = db.query(Bet).filter(
                Bet.status == "won"
            ).count()
            
            total_profit = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).with_entities(
                db.func.sum(Bet.profit)
            ).scalar() or 0.0
            
            return {
                "total_settled": total_bets,
                "won": won_bets,
                "lost": total_bets - won_bets,
                "win_rate": won_bets / total_bets if total_bets > 0 else 0.0,
                "total_profit": total_profit,
            }
