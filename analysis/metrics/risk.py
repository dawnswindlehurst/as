"""Risk metrics calculation."""
from typing import Dict, List
import numpy as np
from .base import MetricsCalculator
from database.models import Bet


class RiskMetrics(MetricsCalculator):
    """Calculate risk-related metrics."""
    
    def calculate(self, risk_free_rate: float = 0.0) -> Dict:
        """Calculate risk metrics.
        
        Args:
            risk_free_rate: Annual risk-free rate (default 0.0)
            
        Returns:
            Dictionary with:
            - sharpe_ratio: (Mean Return - Risk Free) / Std Dev
            - sortino_ratio: Sharpe considering only downside
            - max_drawdown: Maximum peak-to-valley decline (%)
            - max_drawdown_duration: Days in max drawdown
            - recovery_factor: Total Profit / Max Drawdown
            - calmar_ratio: Annualized ROI / Max Drawdown
            - volatility: Standard deviation of returns
            - var_95: Value at Risk (95% confidence)
            - cvar_95: Conditional VaR (average of worst 5%)
        """
        if not self.bets:
            return self._empty_metrics()
        
        # Filter settled bets and sort by date
        settled_bets = sorted(
            [b for b in self.bets if b.status in ['won', 'lost'] and b.settled_at],
            key=lambda x: x.settled_at
        )
        
        if not settled_bets:
            return self._empty_metrics()
        
        # Calculate returns and equity curve
        returns = []
        equity_curve = [0]
        cumulative_equity = 0
        
        for bet in settled_bets:
            ret = (bet.profit / bet.stake) if bet.stake > 0 else 0
            returns.append(ret)
            cumulative_equity += bet.profit
            equity_curve.append(cumulative_equity)
        
        returns_array = np.array(returns)
        
        # Sharpe Ratio
        excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate
        sharpe = (np.mean(excess_returns) / np.std(returns_array)) if np.std(returns_array) > 0 else 0
        sharpe = sharpe * np.sqrt(252)  # Annualize
        
        # Sortino Ratio (only downside deviation)
        downside_returns = returns_array[returns_array < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino = (np.mean(excess_returns) / downside_std) if downside_std > 0 else 0
        sortino = sortino * np.sqrt(252)  # Annualize
        
        # Max Drawdown
        max_dd, max_dd_duration = self._calculate_max_drawdown(equity_curve, settled_bets)
        
        # Recovery Factor
        total_profit = cumulative_equity
        recovery = (total_profit / abs(max_dd)) if max_dd < 0 else 0
        
        # Calmar Ratio (annualized ROI / max DD)
        total_stake = sum(b.stake for b in settled_bets)
        roi = (total_profit / total_stake) if total_stake > 0 else 0
        
        # Estimate annualized ROI
        days = (settled_bets[-1].settled_at - settled_bets[0].settled_at).days
        annualized_roi = (roi * 365 / days) if days > 0 else roi
        calmar = (annualized_roi / abs(max_dd)) if max_dd < 0 else 0
        
        # Volatility
        volatility = np.std(returns_array) * np.sqrt(252)  # Annualized
        
        # VaR and CVaR (95% confidence)
        var_95 = np.percentile(returns_array, 5)
        worst_5_percent = returns_array[returns_array <= var_95]
        cvar_95 = np.mean(worst_5_percent) if len(worst_5_percent) > 0 else var_95
        
        return {
            'sharpe_ratio': round(sharpe, 3),
            'sortino_ratio': round(sortino, 3),
            'max_drawdown': round(max_dd, 2),
            'max_drawdown_duration': max_dd_duration,
            'recovery_factor': round(recovery, 2),
            'calmar_ratio': round(calmar, 3),
            'volatility': round(volatility * 100, 2),  # As percentage
            'var_95': round(var_95 * 100, 2),  # As percentage
            'cvar_95': round(cvar_95 * 100, 2),  # As percentage
        }
    
    def _calculate_max_drawdown(self, equity_curve: List[float], bets: List[Bet]) -> tuple:
        """Calculate maximum drawdown and its duration.
        
        Args:
            equity_curve: List of cumulative equity values
            bets: Sorted list of bets
            
        Returns:
            Tuple of (max_drawdown_percent, duration_days)
        """
        if len(equity_curve) < 2:
            return 0.0, 0
        
        peak = equity_curve[0]
        max_dd = 0.0
        max_dd_duration = 0
        current_dd_start = None
        
        for i, equity in enumerate(equity_curve):
            if equity > peak:
                peak = equity
                current_dd_start = None
            else:
                dd = ((equity - peak) / abs(peak)) * 100 if peak != 0 else 0
                
                if dd < max_dd:
                    max_dd = dd
                    if current_dd_start is None and i > 0:
                        current_dd_start = bets[i-1].settled_at if i-1 < len(bets) else None
                    
                    if current_dd_start and i-1 < len(bets):
                        duration = (bets[i-1].settled_at - current_dd_start).days
                        max_dd_duration = max(max_dd_duration, duration)
        
        return max_dd, max_dd_duration
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics dictionary."""
        return {
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'max_drawdown': 0.0,
            'max_drawdown_duration': 0,
            'recovery_factor': 0.0,
            'calmar_ratio': 0.0,
            'volatility': 0.0,
            'var_95': 0.0,
            'cvar_95': 0.0,
        }
