"""Performance metrics."""
from typing import Dict
import numpy as np
from database.db import get_db
from database.models import Bet
from utils.helpers import calculate_roi


class PerformanceMetrics:
    """Calculate various performance metrics."""
    
    def __init__(self):
        pass
    
    def calculate_sharpe_ratio(self, returns: list, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio.
        
        Args:
            returns: List of returns
            risk_free_rate: Risk-free rate
            
        Returns:
            Sharpe ratio
        """
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate
        
        if np.std(excess_returns) == 0:
            return 0.0
        
        return np.mean(excess_returns) / np.std(excess_returns)
    
    def calculate_max_drawdown(self, equity_curve: list) -> float:
        """Calculate maximum drawdown.
        
        Args:
            equity_curve: List of equity values over time
            
        Returns:
            Maximum drawdown (negative value)
        """
        if not equity_curve:
            return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            
            dd = (value - peak) / peak if peak > 0 else 0
            max_dd = min(max_dd, dd)
        
        return max_dd
    
    def calculate_win_loss_ratio(self) -> float:
        """Calculate average win / average loss ratio.
        
        Returns:
            Win/Loss ratio
        """
        with get_db() as db:
            won_bets = db.query(Bet).filter(Bet.status == "won").all()
            lost_bets = db.query(Bet).filter(Bet.status == "lost").all()
            
            if not won_bets or not lost_bets:
                return 0.0
            
            avg_win = sum(b.profit for b in won_bets) / len(won_bets)
            avg_loss = abs(sum(b.profit for b in lost_bets) / len(lost_bets))
            
            return avg_win / avg_loss if avg_loss > 0 else 0.0
    
    def get_all_metrics(self) -> Dict:
        """Get all performance metrics.
        
        Returns:
            Dictionary with all metrics
        """
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).order_by(Bet.settled_at).all()
            
            if not bets:
                return {}
            
            # Calculate equity curve
            equity = 0.0
            equity_curve = []
            returns = []
            
            for bet in bets:
                equity += bet.profit
                equity_curve.append(equity)
                returns.append(bet.profit / bet.stake)
            
            total_stake = sum(b.stake for b in bets)
            total_profit = sum(b.profit for b in bets)
            
            return {
                "roi": calculate_roi(total_profit, total_stake),
                "sharpe_ratio": self.calculate_sharpe_ratio(returns),
                "max_drawdown": self.calculate_max_drawdown(equity_curve),
                "win_loss_ratio": self.calculate_win_loss_ratio(),
                "total_bets": len(bets),
                "final_equity": equity,
            }
