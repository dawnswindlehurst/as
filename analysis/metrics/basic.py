"""Basic performance metrics."""
from typing import Dict, List
import numpy as np
from .base import MetricsCalculator
from database.models import Bet


class BasicMetrics(MetricsCalculator):
    """Calculate basic performance metrics."""
    
    def calculate(self) -> Dict:
        """Calculate basic metrics.
        
        Returns:
            Dictionary with:
            - win_rate: Win percentage
            - roi: Return on investment (%)
            - profit: Total profit
            - yield_per_bet: Average profit per bet
            - total_wagered: Total amount wagered
            - total_bets: Number of bets
            - average_odds: Average odds
            - average_stake: Average stake
        """
        if not self.bets:
            return {
                'win_rate': 0.0,
                'roi': 0.0,
                'profit': 0.0,
                'yield_per_bet': 0.0,
                'total_wagered': 0.0,
                'total_bets': 0,
                'average_odds': 0.0,
                'average_stake': 0.0,
            }
        
        # Filter only settled bets
        settled_bets = [b for b in self.bets if b.status in ['won', 'lost']]
        
        if not settled_bets:
            return {
                'win_rate': 0.0,
                'roi': 0.0,
                'profit': 0.0,
                'yield_per_bet': 0.0,
                'total_wagered': 0.0,
                'total_bets': len(self.bets),
                'average_odds': np.mean([b.odds for b in self.bets]) if self.bets else 0.0,
                'average_stake': np.mean([b.stake for b in self.bets]) if self.bets else 0.0,
            }
        
        # Calculate metrics
        won_bets = [b for b in settled_bets if b.status == 'won']
        total_stake = sum(b.stake for b in settled_bets)
        total_profit = sum(b.profit for b in settled_bets if b.profit is not None)
        
        win_rate = len(won_bets) / len(settled_bets) if settled_bets else 0.0
        roi = (total_profit / total_stake * 100) if total_stake > 0 else 0.0
        yield_per_bet = total_profit / len(settled_bets) if settled_bets else 0.0
        
        return {
            'win_rate': round(win_rate * 100, 2),  # As percentage
            'roi': round(roi, 2),
            'profit': round(total_profit, 2),
            'yield_per_bet': round(yield_per_bet, 2),
            'total_wagered': round(total_stake, 2),
            'total_bets': len(settled_bets),
            'average_odds': round(np.mean([b.odds for b in settled_bets]), 2),
            'average_stake': round(np.mean([b.stake for b in settled_bets]), 2),
        }
    
    def calculate_by_dimension(self, dimension: str, values: List) -> Dict:
        """Calculate basic metrics segmented by a dimension.
        
        Args:
            dimension: The dimension to segment by (e.g., 'sport', 'market')
            values: List of values for that dimension
            
        Returns:
            Dictionary with metrics for each value
        """
        results = {}
        
        for value in values:
            if dimension == 'sport':
                filtered_bets = [b for b in self.bets if hasattr(b.match, 'game') and b.match.game == value]
            elif dimension == 'market':
                filtered_bets = [b for b in self.bets if b.market_type == value]
            elif dimension == 'confidence_range':
                min_conf, max_conf = value[:2]
                filtered_bets = [b for b in self.bets if min_conf <= b.confidence < max_conf]
            elif dimension == 'odds_range':
                min_odds, max_odds = value[:2]
                filtered_bets = [b for b in self.bets if min_odds <= b.odds < max_odds]
            else:
                filtered_bets = []
            
            # Create new metrics calculator for filtered bets
            calc = BasicMetrics(filtered_bets)
            label = value[2] if isinstance(value, tuple) and len(value) > 2 else str(value)
            results[label] = calc.calculate()
        
        return results
