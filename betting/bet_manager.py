"""Bet manager for tracking bets and calculating P&L."""
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from config.settings import DATA_DIR, PAPER_TRADING_STAKE, PAPER_TRADING_CURRENCY
from utils.logger import log


class BetStatus(Enum):
    """Bet status enumeration."""
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    VOID = "void"
    PUSH = "push"


class BetType(Enum):
    """Bet type enumeration."""
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    OVER_UNDER = "over_under"
    PROP = "prop"


class BetManager:
    """Manager for tracking bets and calculating profit/loss.
    
    Handles bet placement, settlement, and performance analytics
    for paper trading.
    """
    
    def __init__(self, bets_file: Optional[Path] = None):
        """Initialize the bet manager.
        
        Args:
            bets_file: Path to bets storage file
        """
        self.bets_file = bets_file or DATA_DIR / "bets.json"
        self.bets: List[Dict[str, Any]] = []
        self._bet_counter = 0  # Monotonic counter for unique IDs
        self.load_bets()
    
    def load_bets(self):
        """Load bets from storage file."""
        if self.bets_file.exists():
            try:
                with open(self.bets_file, 'r', encoding='utf-8') as f:
                    self.bets = json.load(f)
                # Set counter to highest existing ID + 1
                if self.bets:
                    max_counter = max(
                        int(bet['bet_id'].split('_')[1]) 
                        for bet in self.bets 
                        if 'bet_id' in bet and '_' in bet['bet_id']
                    )
                    self._bet_counter = max_counter + 1
                log.info(f"Loaded {len(self.bets)} bets from storage")
            except Exception as e:
                log.error(f"Failed to load bets: {e}")
                self.bets = []
        else:
            log.info("Bets file not found, starting fresh")
            self.bets = []
    
    def save_bets(self):
        """Save bets to storage file."""
        try:
            self.bets_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.bets_file, 'w', encoding='utf-8') as f:
                json.dump(self.bets, f, indent=2, ensure_ascii=False)
            log.debug(f"Saved {len(self.bets)} bets to storage")
        except Exception as e:
            log.error(f"Failed to save bets: {e}")
    
    def add_bet(
        self,
        event_id: str,
        event_name: str,
        sport: str,
        bet_type: str,
        selection: str,
        odds: float,
        stake: Optional[float] = None,
        bookmaker: str = "Paper",
        **metadata
    ) -> str:
        """Add a new bet.
        
        Args:
            event_id: Unique event identifier
            event_name: Event description
            sport: Sport (nba, soccer, tennis, etc.)
            bet_type: Type of bet (moneyline, spread, over_under, prop)
            selection: What was bet on
            odds: Decimal odds
            stake: Bet stake (defaults to PAPER_TRADING_STAKE)
            bookmaker: Bookmaker name
            **metadata: Additional bet metadata
            
        Returns:
            Bet ID
        """
        bet_id = f"bet_{self._bet_counter}_{int(datetime.now().timestamp())}"
        self._bet_counter += 1
        
        bet = {
            "bet_id": bet_id,
            "event_id": event_id,
            "event_name": event_name,
            "sport": sport,
            "bet_type": bet_type,
            "selection": selection,
            "odds": odds,
            "stake": stake or PAPER_TRADING_STAKE,
            "currency": PAPER_TRADING_CURRENCY,
            "bookmaker": bookmaker,
            "status": BetStatus.PENDING.value,
            "placed_at": datetime.now().isoformat(),
            "settled_at": None,
            "pnl": 0.0,
            **metadata
        }
        
        self.bets.append(bet)
        self.save_bets()
        
        log.info(f"Added bet {bet_id}: {selection} @ {odds} on {event_name}")
        return bet_id
    
    def settle_bet(self, bet_id: str, status: str, result: Optional[str] = None):
        """Settle a bet.
        
        Args:
            bet_id: Bet identifier
            status: Bet outcome (won, lost, void, push)
            result: Optional result description
        """
        bet = self.get_bet(bet_id)
        if not bet:
            log.warning(f"Bet {bet_id} not found")
            return
        
        if bet["status"] != BetStatus.PENDING.value:
            log.warning(f"Bet {bet_id} already settled")
            return
        
        bet["status"] = status
        bet["settled_at"] = datetime.now().isoformat()
        
        if result:
            bet["result"] = result
        
        # Calculate P&L
        if status == BetStatus.WON.value:
            bet["pnl"] = bet["stake"] * (bet["odds"] - 1)
        elif status == BetStatus.LOST.value:
            bet["pnl"] = -bet["stake"]
        else:  # void or push
            bet["pnl"] = 0.0
        
        self.save_bets()
        log.info(f"Settled bet {bet_id} as {status}, P&L: {bet['pnl']:.2f}")
    
    def get_bet(self, bet_id: str) -> Optional[Dict[str, Any]]:
        """Get a bet by ID.
        
        Args:
            bet_id: Bet identifier
            
        Returns:
            Bet dictionary or None
        """
        for bet in self.bets:
            if bet["bet_id"] == bet_id:
                return bet
        return None
    
    def get_pending_bets(self, sport: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all pending bets.
        
        Args:
            sport: Optional sport filter
            
        Returns:
            List of pending bets
        """
        pending = [
            bet for bet in self.bets
            if bet["status"] == BetStatus.PENDING.value
        ]
        
        if sport:
            pending = [bet for bet in pending if bet["sport"] == sport]
        
        return pending
    
    def get_settled_bets(self, sport: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all settled bets.
        
        Args:
            sport: Optional sport filter
            
        Returns:
            List of settled bets
        """
        settled = [
            bet for bet in self.bets
            if bet["status"] != BetStatus.PENDING.value
        ]
        
        if sport:
            settled = [bet for bet in settled if bet["sport"] == sport]
        
        return settled
    
    def calculate_total_pnl(self, sport: Optional[str] = None) -> float:
        """Calculate total profit/loss.
        
        Args:
            sport: Optional sport filter
            
        Returns:
            Total P&L
        """
        bets_to_sum = self.bets
        if sport:
            bets_to_sum = [bet for bet in self.bets if bet["sport"] == sport]
        
        return sum(bet.get("pnl", 0.0) for bet in bets_to_sum)
    
    def get_statistics(self, sport: Optional[str] = None) -> Dict[str, Any]:
        """Get betting statistics.
        
        Args:
            sport: Optional sport filter
            
        Returns:
            Dictionary with statistics
        """
        bets_to_analyze = self.bets
        if sport:
            bets_to_analyze = [bet for bet in self.bets if bet["sport"] == sport]
        
        settled = [bet for bet in bets_to_analyze if bet["status"] != BetStatus.PENDING.value]
        won = [bet for bet in settled if bet["status"] == BetStatus.WON.value]
        lost = [bet for bet in settled if bet["status"] == BetStatus.LOST.value]
        
        total_bets = len(bets_to_analyze)
        total_settled = len(settled)
        total_won = len(won)
        total_lost = len(lost)
        
        win_rate = (total_won / total_settled * 100) if total_settled > 0 else 0.0
        
        total_staked = sum(bet["stake"] for bet in settled)
        total_pnl = sum(bet.get("pnl", 0.0) for bet in settled)
        roi = (total_pnl / total_staked * 100) if total_staked > 0 else 0.0
        
        avg_odds_won = sum(bet["odds"] for bet in won) / len(won) if won else 0.0
        avg_odds_lost = sum(bet["odds"] for bet in lost) / len(lost) if lost else 0.0
        
        return {
            "total_bets": total_bets,
            "settled_bets": total_settled,
            "pending_bets": total_bets - total_settled,
            "won": total_won,
            "lost": total_lost,
            "win_rate": win_rate,
            "total_staked": total_staked,
            "total_pnl": total_pnl,
            "roi": roi,
            "avg_odds_won": avg_odds_won,
            "avg_odds_lost": avg_odds_lost,
            "currency": PAPER_TRADING_CURRENCY,
        }
    
    def get_bets_by_sport(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group bets by sport.
        
        Returns:
            Dictionary mapping sport to list of bets
        """
        by_sport = {}
        for bet in self.bets:
            sport = bet.get("sport", "unknown")
            if sport not in by_sport:
                by_sport[sport] = []
            by_sport[sport].append(bet)
        return by_sport
    
    def get_recent_bets(self, limit: int = 10, sport: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get most recent bets.
        
        Args:
            limit: Maximum number of bets to return
            sport: Optional sport filter
            
        Returns:
            List of recent bets
        """
        bets_to_show = self.bets
        if sport:
            bets_to_show = [bet for bet in self.bets if bet["sport"] == sport]
        
        # Sort by placed_at descending
        sorted_bets = sorted(
            bets_to_show,
            key=lambda x: x.get("placed_at", ""),
            reverse=True
        )
        
        return sorted_bets[:limit]


# Global bet manager instance
bet_manager = BetManager()
