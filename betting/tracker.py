"""Bet tracker - track active bets."""
from typing import List, Dict, Optional
from datetime import datetime
from database.db import get_db
from database.models import Bet
from utils.logger import log


class BetTracker:
    """Track active and pending bets."""
    
    def __init__(self):
        pass
    
    def get_pending_bets(self) -> List[Bet]:
        """Get all pending bets.
        
        Returns:
            List of pending bets
        """
        with get_db() as db:
            return db.query(Bet).filter(Bet.status == "pending").all()
    
    def get_confirmed_bets(self) -> List[Bet]:
        """Get all confirmed bets.
        
        Returns:
            List of confirmed bets
        """
        with get_db() as db:
            return db.query(Bet).filter(Bet.confirmed == True).all()
    
    def get_unsettled_bets(self) -> List[Bet]:
        """Get all unsettled confirmed bets.
        
        Returns:
            List of unsettled bets
        """
        with get_db() as db:
            return db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status == "pending"
            ).all()
    
    def confirm_bet(self, bet_id: int):
        """Confirm a bet.
        
        Args:
            bet_id: Bet ID
        """
        with get_db() as db:
            bet = db.query(Bet).filter(Bet.id == bet_id).first()
            if bet:
                bet.confirmed = True
                log.info(f"Confirmed bet {bet_id}")
    
    def cancel_bet(self, bet_id: int):
        """Cancel/ignore a bet suggestion.
        
        Args:
            bet_id: Bet ID
        """
        with get_db() as db:
            bet = db.query(Bet).filter(Bet.id == bet_id).first()
            if bet:
                bet.status = "void"
                log.info(f"Cancelled bet {bet_id}")
    
    def update_closing_odds(self, bet_id: int, closing_odds: float):
        """Update closing odds for CLV tracking.
        
        Args:
            bet_id: Bet ID
            closing_odds: Closing odds
        """
        with get_db() as db:
            bet = db.query(Bet).filter(Bet.id == bet_id).first()
            if bet:
                bet.closing_odds = closing_odds
                bet.clv = (1.0 / bet.odds) - (1.0 / closing_odds)
                log.info(f"Updated closing odds for bet {bet_id}: CLV = {bet.clv:.4f}")
