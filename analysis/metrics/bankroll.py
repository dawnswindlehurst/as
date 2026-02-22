"""Bankroll management metrics."""
from typing import Dict, List
import numpy as np
from .base import MetricsCalculator
from database.models import Bet


class BankrollMetrics(MetricsCalculator):
    """Calculate bankroll management metrics."""
    
    def __init__(self, bets: List[Bet] = None, initial_bankroll: float = 1000.0):
        """Initialize bankroll metrics.
        
        Args:
            bets: List of bets
            initial_bankroll: Starting bankroll amount
        """
        super().__init__(bets)
        self.initial_bankroll = initial_bankroll
    
    def calculate(self) -> Dict:
        """Calculate bankroll metrics.
        
        Returns:
            Dictionary with:
            - current_bankroll: Current bankroll amount
            - bankroll_growth: Growth percentage
            - units_won: Profit in units (stake = 1 unit)
            - kelly_suggested: Average Kelly criterion stake
            - break_even_winrate: Required win rate to break even
            - expected_value_per_bet: Average EV per bet
            - roi_if_flat: ROI if using flat betting
            - equity_curve: List of bankroll values over time
        """
        if not self.bets:
            return self._empty_metrics()
        
        # Filter settled bets
        settled_bets = sorted(
            [b for b in self.bets if b.status in ['won', 'lost'] and b.settled_at],
            key=lambda x: x.settled_at
        )
        
        if not settled_bets:
            return self._empty_metrics()
        
        # Calculate current bankroll
        total_profit = sum(b.profit for b in settled_bets if b.profit)
        current_bankroll = self.initial_bankroll + total_profit
        
        # Bankroll growth
        bankroll_growth = ((current_bankroll - self.initial_bankroll) / self.initial_bankroll) * 100
        
        # Units won (assuming stake = 1 unit)
        avg_stake = np.mean([b.stake for b in settled_bets])
        units_won = total_profit / avg_stake if avg_stake > 0 else 0
        
        # Kelly suggested stake
        kelly_suggested = self._calculate_kelly_average(settled_bets)
        
        # Break-even win rate
        break_even_wr = self._calculate_break_even_winrate(settled_bets)
        
        # Expected value per bet
        ev_per_bet = self._calculate_ev_per_bet(settled_bets)
        
        # ROI if flat betting
        total_stake = sum(b.stake for b in settled_bets)
        roi_flat = (total_profit / total_stake * 100) if total_stake > 0 else 0
        
        # Equity curve
        equity_curve = self._build_equity_curve(settled_bets)
        
        return {
            'current_bankroll': round(current_bankroll, 2),
            'bankroll_growth': round(bankroll_growth, 2),
            'units_won': round(units_won, 2),
            'kelly_suggested': round(kelly_suggested, 2),
            'break_even_winrate': round(break_even_wr, 2),
            'expected_value_per_bet': round(ev_per_bet, 2),
            'roi_if_flat': round(roi_flat, 2),
            'equity_curve': equity_curve,
        }
    
    def _calculate_kelly_average(self, bets: List[Bet]) -> float:
        """Calculate average Kelly criterion stake.
        
        Kelly formula: (edge / odds) where edge = model_prob - implied_prob
        
        Args:
            bets: List of settled bets
            
        Returns:
            Average Kelly stake as percentage of bankroll
        """
        kelly_stakes = []
        
        for bet in bets:
            # Kelly = (bp - q) / b
            # where b = odds - 1, p = win probability, q = 1 - p
            if bet.odds > 1:
                b = bet.odds - 1
                p = bet.model_probability
                q = 1 - p
                kelly = (b * p - q) / b
                
                # Clamp to reasonable range (0-10% of bankroll)
                kelly = max(0, min(kelly, 0.10))
                kelly_stakes.append(kelly)
        
        return np.mean(kelly_stakes) * 100 if kelly_stakes else 0.0  # As percentage
    
    def _calculate_break_even_winrate(self, bets: List[Bet]) -> float:
        """Calculate the win rate needed to break even.
        
        Break-even WR = 1 / average_odds
        
        Args:
            bets: List of settled bets
            
        Returns:
            Break-even win rate as percentage
        """
        avg_odds = np.mean([b.odds for b in bets])
        break_even = (1 / avg_odds * 100) if avg_odds > 0 else 0
        return break_even
    
    def _calculate_ev_per_bet(self, bets: List[Bet]) -> float:
        """Calculate expected value per bet.
        
        EV = (win_prob * win_amount) - (lose_prob * lose_amount)
        
        Args:
            bets: List of settled bets
            
        Returns:
            Average EV per bet in currency
        """
        ev_values = []
        
        for bet in bets:
            win_prob = bet.model_probability
            lose_prob = 1 - win_prob
            win_amount = bet.stake * (bet.odds - 1)
            lose_amount = bet.stake
            
            ev = (win_prob * win_amount) - (lose_prob * lose_amount)
            ev_values.append(ev)
        
        return np.mean(ev_values) if ev_values else 0.0
    
    def _build_equity_curve(self, bets: List[Bet]) -> List[Dict]:
        """Build equity curve data.
        
        Args:
            bets: Sorted list of settled bets
            
        Returns:
            List of {date, bankroll} dictionaries
        """
        equity_curve = [{'date': None, 'bankroll': self.initial_bankroll}]
        current_bankroll = self.initial_bankroll
        
        for bet in bets:
            current_bankroll += bet.profit if bet.profit else 0
            equity_curve.append({
                'date': bet.settled_at.isoformat() if bet.settled_at else None,
                'bankroll': round(current_bankroll, 2)
            })
        
        return equity_curve
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics dictionary."""
        return {
            'current_bankroll': self.initial_bankroll,
            'bankroll_growth': 0.0,
            'units_won': 0.0,
            'kelly_suggested': 0.0,
            'break_even_winrate': 0.0,
            'expected_value_per_bet': 0.0,
            'roi_if_flat': 0.0,
            'equity_curve': [{'date': None, 'bankroll': self.initial_bankroll}],
        }
