"""Streak tracking and analysis."""
from typing import Dict, List
from database.db import get_db
from database.models import Bet
from utils.helpers import get_streak_info


class StreakAnalyzer:
    """Analyze winning and losing streaks."""
    
    def __init__(self):
        pass
    
    def get_current_streak(self) -> Dict:
        """Get current winning/losing streak.
        
        Returns:
            Current streak information
        """
        with get_db() as db:
            recent_bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).order_by(Bet.settled_at.desc()).limit(100).all()
            
            if not recent_bets:
                return {"current_streak": 0, "type": None}
            
            results = [b.status == "won" for b in reversed(recent_bets)]
            streak_info = get_streak_info(results)
            
            return streak_info
    
    def get_streak_history(self) -> Dict:
        """Get historical streak information.
        
        Returns:
            Dictionary with streak history
        """
        with get_db() as db:
            all_bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).order_by(Bet.settled_at).all()
            
            if not all_bets:
                return {}
            
            results = [b.status == "won" for b in all_bets]
            streak_info = get_streak_info(results)
            
            # Calculate average streak lengths
            win_streaks = []
            loss_streaks = []
            current_streak = 0
            current_type = None
            
            for result in results:
                if current_type is None:
                    current_type = result
                    current_streak = 1
                elif result == current_type:
                    current_streak += 1
                else:
                    if current_type:
                        win_streaks.append(current_streak)
                    else:
                        loss_streaks.append(current_streak)
                    current_type = result
                    current_streak = 1
            
            return {
                **streak_info,
                "avg_win_streak": sum(win_streaks) / len(win_streaks) if win_streaks else 0,
                "avg_loss_streak": sum(loss_streaks) / len(loss_streaks) if loss_streaks else 0,
                "total_win_streaks": len(win_streaks),
                "total_loss_streaks": len(loss_streaks),
            }
