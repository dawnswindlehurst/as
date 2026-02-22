"""Head-to-head features."""
from typing import Dict, List, Optional
from database.db import get_db
from database.models import Match


class H2HFeatures:
    """Calculate head-to-head features between teams."""
    
    def __init__(self):
        pass
    
    def get_h2h_record(self, team1: str, team2: str, game: str) -> Dict:
        """Get head-to-head record between two teams.
        
        Args:
            team1: Team 1 name
            team2: Team 2 name
            game: Game name
            
        Returns:
            Dictionary with H2H statistics
        """
        with get_db() as db:
            # Get all matches between these teams
            matches = db.query(Match).filter(
                Match.game == game,
                Match.finished == True,
                (
                    ((Match.team1 == team1) & (Match.team2 == team2)) |
                    ((Match.team1 == team2) & (Match.team2 == team1))
                )
            ).all()
            
            team1_wins = 0
            team2_wins = 0
            total_matches = len(matches)
            
            for match in matches:
                if match.winner == team1:
                    team1_wins += 1
                elif match.winner == team2:
                    team2_wins += 1
            
            return {
                "total_matches": total_matches,
                "team1_wins": team1_wins,
                "team2_wins": team2_wins,
                "team1_win_rate": team1_wins / total_matches if total_matches > 0 else 0.5,
                "team2_win_rate": team2_wins / total_matches if total_matches > 0 else 0.5,
            }
    
    def get_recent_h2h(
        self, team1: str, team2: str, game: str, num_matches: int = 5
    ) -> List[Dict]:
        """Get recent head-to-head matches.
        
        Args:
            team1: Team 1 name
            team2: Team 2 name
            game: Game name
            num_matches: Number of recent matches to retrieve
            
        Returns:
            List of recent match dictionaries
        """
        with get_db() as db:
            matches = db.query(Match).filter(
                Match.game == game,
                Match.finished == True,
                (
                    ((Match.team1 == team1) & (Match.team2 == team2)) |
                    ((Match.team1 == team2) & (Match.team2 == team1))
                )
            ).order_by(Match.start_time.desc()).limit(num_matches).all()
            
            return [
                {
                    "date": match.start_time,
                    "winner": match.winner,
                    "score": f"{match.team1_score}-{match.team2_score}",
                }
                for match in matches
            ]
