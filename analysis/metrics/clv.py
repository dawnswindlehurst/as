"""Closing Line Value (CLV) metrics."""
from typing import Dict, List
import numpy as np
from .base import MetricsCalculator
from database.models import Bet


class CLVMetrics(MetricsCalculator):
    """Calculate Closing Line Value metrics."""
    
    def calculate(self) -> Dict:
        """Calculate CLV metrics.
        
        Returns:
            Dictionary with:
            - clv_average: Average CLV across all bets
            - clv_positive_rate: % of bets with positive CLV
            - clv_by_sport: CLV broken down by sport
            - clv_by_market: CLV broken down by market
            - clv_correlation: Correlation between CLV and profit
            - edge_realized: Actual edge vs theoretical edge
        """
        if not self.bets:
            return self._empty_metrics()
        
        # Filter bets with CLV data
        bets_with_clv = [b for b in self.bets if b.clv is not None and b.closing_odds is not None]
        
        if not bets_with_clv:
            return self._empty_metrics()
        
        # Calculate average CLV
        clv_values = [b.clv for b in bets_with_clv]
        clv_average = np.mean(clv_values)
        
        # Positive CLV rate
        positive_clv_count = sum(1 for clv in clv_values if clv > 0)
        clv_positive_rate = (positive_clv_count / len(clv_values)) * 100
        
        # CLV by sport
        clv_by_sport = self._calculate_clv_by_dimension(bets_with_clv, 'sport')
        
        # CLV by market
        clv_by_market = self._calculate_clv_by_dimension(bets_with_clv, 'market')
        
        # CLV correlation with results
        clv_correlation = self._calculate_clv_correlation(bets_with_clv)
        
        # Edge realized
        edge_realized = self._calculate_edge_realized(bets_with_clv)
        
        return {
            'clv_average': round(clv_average, 4),
            'clv_positive_rate': round(clv_positive_rate, 2),
            'clv_by_sport': clv_by_sport,
            'clv_by_market': clv_by_market,
            'clv_correlation': round(clv_correlation, 3),
            'edge_realized': round(edge_realized, 2),
        }
    
    def _calculate_clv_by_dimension(self, bets: List[Bet], dimension: str) -> Dict:
        """Calculate average CLV by a dimension.
        
        Args:
            bets: List of bets with CLV
            dimension: 'sport' or 'market'
            
        Returns:
            Dictionary mapping dimension values to average CLV
        """
        dimension_map = {}
        
        for bet in bets:
            if dimension == 'sport':
                key = bet.match.game if hasattr(bet.match, 'game') else 'Unknown'
            elif dimension == 'market':
                key = bet.market_type
            else:
                continue
            
            if key not in dimension_map:
                dimension_map[key] = []
            dimension_map[key].append(bet.clv)
        
        return {
            key: round(np.mean(values), 4)
            for key, values in dimension_map.items()
        }
    
    def _calculate_clv_correlation(self, bets: List[Bet]) -> float:
        """Calculate correlation between CLV and bet outcome.
        
        Args:
            bets: List of bets with CLV
            
        Returns:
            Correlation coefficient
        """
        settled_bets = [b for b in bets if b.status in ['won', 'lost']]
        
        if len(settled_bets) < 2:
            return 0.0
        
        clv_values = [b.clv for b in settled_bets]
        outcomes = [1 if b.status == 'won' else 0 for b in settled_bets]
        
        # Calculate Pearson correlation
        correlation = np.corrcoef(clv_values, outcomes)[0, 1]
        
        return correlation if not np.isnan(correlation) else 0.0
    
    def _calculate_edge_realized(self, bets: List[Bet]) -> float:
        """Calculate how much of theoretical edge was realized.
        
        Args:
            bets: List of bets with CLV
            
        Returns:
            Percentage of edge realized
        """
        settled_bets = [b for b in bets if b.status in ['won', 'lost'] and b.profit is not None]
        
        if not settled_bets:
            return 0.0
        
        # Theoretical edge (average)
        theoretical_edge = np.mean([b.edge for b in settled_bets])
        
        # Realized edge (actual ROI)
        total_stake = sum(b.stake for b in settled_bets)
        total_profit = sum(b.profit for b in settled_bets)
        realized_edge = (total_profit / total_stake) if total_stake > 0 else 0
        
        # Percentage of theoretical edge achieved
        if theoretical_edge > 0:
            return (realized_edge / theoretical_edge) * 100
        
        return 0.0
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics dictionary."""
        return {
            'clv_average': 0.0,
            'clv_positive_rate': 0.0,
            'clv_by_sport': {},
            'clv_by_market': {},
            'clv_correlation': 0.0,
            'edge_realized': 0.0,
        }
