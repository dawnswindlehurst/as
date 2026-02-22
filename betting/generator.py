"""Bet generator - create bet suggestions."""
from typing import List, Dict
from datetime import datetime
from database.db import get_db
from database.models import Bet
from config.settings import PAPER_TRADING_STAKE
from utils.logger import log


class BetGenerator:
    """Generate bet suggestions from opportunities."""
    
    def __init__(self, default_stake: float = PAPER_TRADING_STAKE):
        self.default_stake = default_stake
    
    def generate_bets(self, opportunities: List[Dict]) -> List[Dict]:
        """Generate bet suggestions from opportunities.
        
        Args:
            opportunities: List of betting opportunities
            
        Returns:
            List of bet dictionaries
        """
        bets = []
        
        for opp in opportunities:
            bet = self._create_bet(opp)
            if bet:
                bets.append(bet)
        
        log.info(f"Generated {len(bets)} bet suggestions")
        return bets
    
    def _create_bet(self, opportunity: Dict) -> Dict:
        """Create a bet from an opportunity.
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            Bet dictionary
        """
        return {
            "match_id": opportunity.get("match_id"),
            "bookmaker": opportunity.get("bookmaker"),
            "market_type": opportunity.get("market_type", "match_winner"),
            "selection": opportunity.get("selection"),
            "odds": opportunity.get("market_odds"),
            "stake": self.default_stake,
            "model_probability": opportunity.get("model_probability"),
            "implied_probability": opportunity.get("market_probability"),
            "edge": opportunity.get("edge"),
            "confidence": opportunity.get("model_probability"),
            "status": "pending",
            "confirmed": False,
            "created_at": datetime.utcnow(),
        }
    
    def save_bets(self, bets: List[Dict]):
        """Save bets to database.
        
        Args:
            bets: List of bet dictionaries
        """
        with get_db() as db:
            for bet_data in bets:
                bet = Bet(**bet_data)
                db.add(bet)
            
            log.info(f"Saved {len(bets)} bets to database")
