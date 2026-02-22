"""Team form features."""
from typing import Dict, List
from datetime import datetime, timedelta
from database.db import get_db
from database.models import Match
from features.decay import exponential_decay


class FormFeatures:
    """Calculate team form features."""
    
    def __init__(self):
        pass
    
    def get_recent_form(
        self, team: str, game: str, num_matches: int = 10
    ) -> Dict:
        """Get recent form for a team.
        
        Args:
            team: Team name
            game: Game name
            num_matches: Number of recent matches to consider
            
        Returns:
            Dictionary with form statistics
        """
        with get_db() as db:
            matches = db.query(Match).filter(
                Match.game == game,
                Match.finished == True,
                ((Match.team1 == team) | (Match.team2 == team))
            ).order_by(Match.start_time.desc()).limit(num_matches).all()
            
            if not matches:
                return {
                    "matches_played": 0,
                    "wins": 0,
                    "losses": 0,
                    "win_rate": 0.5,
                    "weighted_win_rate": 0.5,
                }
            
            wins = 0
            total = len(matches)
            weighted_wins = 0.0
            total_weight = 0.0
            
            now = datetime.utcnow()
            
            for match in matches:
                is_win = match.winner == team
                if is_win:
                    wins += 1
                
                # Calculate decay weight
                days_ago = (now - match.start_time).days
                weight = exponential_decay(days_ago)
                
                weighted_wins += weight if is_win else 0
                total_weight += weight
            
            weighted_win_rate = weighted_wins / total_weight if total_weight > 0 else 0.5
            
            return {
                "matches_played": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": wins / total,
                "weighted_win_rate": weighted_win_rate,
            }
    
    def get_form_by_period(
        self, team: str, game: str, days: int = 30
    ) -> Dict:
        """Get form for a specific time period.
        
        Args:
            team: Team name
            game: Game name
            days: Number of days to look back
            
        Returns:
            Dictionary with period form statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with get_db() as db:
            matches = db.query(Match).filter(
                Match.game == game,
                Match.finished == True,
                Match.start_time >= cutoff_date,
                ((Match.team1 == team) | (Match.team2 == team))
            ).all()
            
            if not matches:
                return {
                    "matches_played": 0,
                    "wins": 0,
                    "win_rate": 0.5,
                }
            
            wins = sum(1 for m in matches if m.winner == team)
            total = len(matches)
            
            return {
                "matches_played": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": wins / total,
            }
