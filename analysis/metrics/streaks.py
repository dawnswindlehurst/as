"""Streaks and consistency metrics."""
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from .base import MetricsCalculator
from database.models import Bet


class StreakMetrics(MetricsCalculator):
    """Calculate streak and consistency metrics."""
    
    def calculate(self) -> Dict:
        """Calculate streak metrics.
        
        Returns:
            Dictionary with:
            - current_streak: Current winning/losing streak
            - longest_win_streak: Longest consecutive wins
            - longest_lose_streak: Longest consecutive losses
            - average_win_streak: Average win streak length
            - average_lose_streak: Average lose streak length
            - win_after_loss: Win rate after a loss
            - win_after_win: Win rate after a win
            - consecutive_profitable_days: Most consecutive profitable days
        """
        if not self.bets:
            return self._empty_metrics()
        
        # Filter and sort settled bets
        settled_bets = sorted(
            [b for b in self.bets if b.status in ['won', 'lost'] and b.settled_at],
            key=lambda x: x.settled_at
        )
        
        if not settled_bets:
            return self._empty_metrics()
        
        # Calculate streaks
        current_streak = self._get_current_streak(settled_bets)
        longest_win, longest_lose = self._get_longest_streaks(settled_bets)
        avg_win_streak, avg_lose_streak = self._get_average_streaks(settled_bets)
        
        # Win rate after outcomes
        win_after_loss = self._calculate_win_after_outcome(settled_bets, 'lost')
        win_after_win = self._calculate_win_after_outcome(settled_bets, 'won')
        
        # Consecutive profitable days
        consecutive_days = self._calculate_consecutive_profitable_days(settled_bets)
        
        return {
            'current_streak': current_streak,
            'longest_win_streak': longest_win,
            'longest_lose_streak': longest_lose,
            'average_win_streak': round(avg_win_streak, 1),
            'average_lose_streak': round(avg_lose_streak, 1),
            'win_after_loss': round(win_after_loss, 2),
            'win_after_win': round(win_after_win, 2),
            'consecutive_profitable_days': consecutive_days,
        }
    
    def _get_current_streak(self, bets: List[Bet]) -> Dict:
        """Get current win/loss streak.
        
        Args:
            bets: Sorted list of settled bets
            
        Returns:
            Dictionary with streak type and count
        """
        if not bets:
            return {'type': 'none', 'count': 0}
        
        # Start from most recent bet
        current_status = bets[-1].status
        count = 1
        
        for bet in reversed(bets[:-1]):
            if bet.status == current_status:
                count += 1
            else:
                break
        
        return {
            'type': 'win' if current_status == 'won' else 'loss',
            'count': count
        }
    
    def _get_longest_streaks(self, bets: List[Bet]) -> Tuple[int, int]:
        """Get longest win and loss streaks.
        
        Args:
            bets: Sorted list of settled bets
            
        Returns:
            Tuple of (longest_win_streak, longest_lose_streak)
        """
        if not bets:
            return 0, 0
        
        longest_win = 0
        longest_lose = 0
        current_win = 0
        current_lose = 0
        
        for bet in bets:
            if bet.status == 'won':
                current_win += 1
                current_lose = 0
                longest_win = max(longest_win, current_win)
            else:
                current_lose += 1
                current_win = 0
                longest_lose = max(longest_lose, current_lose)
        
        return longest_win, longest_lose
    
    def _get_average_streaks(self, bets: List[Bet]) -> Tuple[float, float]:
        """Calculate average streak lengths.
        
        Args:
            bets: Sorted list of settled bets
            
        Returns:
            Tuple of (avg_win_streak, avg_lose_streak)
        """
        if not bets:
            return 0.0, 0.0
        
        win_streaks = []
        lose_streaks = []
        current_streak = 0
        current_type = None
        
        for bet in bets:
            if current_type == bet.status:
                current_streak += 1
            else:
                if current_type == 'won' and current_streak > 0:
                    win_streaks.append(current_streak)
                elif current_type == 'lost' and current_streak > 0:
                    lose_streaks.append(current_streak)
                
                current_type = bet.status
                current_streak = 1
        
        # Add final streak
        if current_type == 'won' and current_streak > 0:
            win_streaks.append(current_streak)
        elif current_type == 'lost' and current_streak > 0:
            lose_streaks.append(current_streak)
        
        avg_win = sum(win_streaks) / len(win_streaks) if win_streaks else 0.0
        avg_lose = sum(lose_streaks) / len(lose_streaks) if lose_streaks else 0.0
        
        return avg_win, avg_lose
    
    def _calculate_win_after_outcome(self, bets: List[Bet], previous_outcome: str) -> float:
        """Calculate win rate after a specific outcome.
        
        Args:
            bets: Sorted list of settled bets
            previous_outcome: 'won' or 'lost'
            
        Returns:
            Win rate percentage
        """
        if len(bets) < 2:
            return 0.0
        
        total_after = 0
        wins_after = 0
        
        for i in range(1, len(bets)):
            if bets[i-1].status == previous_outcome:
                total_after += 1
                if bets[i].status == 'won':
                    wins_after += 1
        
        return (wins_after / total_after * 100) if total_after > 0 else 0.0
    
    def _calculate_consecutive_profitable_days(self, bets: List[Bet]) -> int:
        """Calculate longest streak of consecutive profitable days.
        
        Args:
            bets: Sorted list of settled bets
            
        Returns:
            Number of consecutive profitable days
        """
        if not bets:
            return 0
        
        # Group bets by day
        daily_profits = {}
        for bet in bets:
            day = bet.settled_at.date()
            if day not in daily_profits:
                daily_profits[day] = 0
            daily_profits[day] += bet.profit if bet.profit else 0
        
        # Find longest consecutive profitable days
        sorted_days = sorted(daily_profits.keys())
        max_consecutive = 0
        current_consecutive = 0
        
        for i, day in enumerate(sorted_days):
            if daily_profits[day] > 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics dictionary."""
        return {
            'current_streak': {'type': 'none', 'count': 0},
            'longest_win_streak': 0,
            'longest_lose_streak': 0,
            'average_win_streak': 0.0,
            'average_lose_streak': 0.0,
            'win_after_loss': 0.0,
            'win_after_win': 0.0,
            'consecutive_profitable_days': 0,
        }
