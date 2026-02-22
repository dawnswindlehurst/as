"""Timing analysis - odds movement over time."""
from typing import Dict, List
from datetime import datetime, timedelta
from database.db import get_db
from database.models import Odds, Match
from config.constants import TIMING_WINDOWS


class TimingAnalyzer:
    """Analyze odds timing and movement."""
    
    def __init__(self):
        self.timing_windows = TIMING_WINDOWS
    
    def analyze_odds_movement(self, match_id: int) -> Dict:
        """Analyze odds movement for a match.
        
        Args:
            match_id: Match ID
            
        Returns:
            Dictionary with odds movement analysis
        """
        with get_db() as db:
            match = db.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                return {}
            
            # Get all odds for this match ordered by time
            odds_history = db.query(Odds).filter(
                Odds.match_id == match_id
            ).order_by(Odds.timestamp).all()
            
            if not odds_history:
                return {}
            
            # Analyze movement
            opening = odds_history[0]
            closing = odds_history[-1]
            
            return {
                "match_id": match_id,
                "total_updates": len(odds_history),
                "opening_odds": {
                    "team1": opening.team1_odds,
                    "team2": opening.team2_odds,
                },
                "closing_odds": {
                    "team1": closing.team1_odds,
                    "team2": closing.team2_odds,
                },
                "movement": {
                    "team1": closing.team1_odds - opening.team1_odds if opening.team1_odds and closing.team1_odds else 0,
                    "team2": closing.team2_odds - opening.team2_odds if opening.team2_odds and closing.team2_odds else 0,
                },
            }
    
    def get_best_timing_window(self) -> Dict:
        """Find the best timing window for placing bets.
        
        Returns:
            Dictionary with best timing window analysis
        """
        # TODO: Implement analysis based on historical bet performance
        # grouped by time until match start
        
        return {
            "best_window": "24h",
            "roi": 0.0,
            "sample_size": 0,
        }
    
    def analyze_steam_moves(self, threshold: float = 0.10) -> List[Dict]:
        """Identify steam moves (sudden large odds changes).
        
        Args:
            threshold: Minimum odds change percentage to consider
            
        Returns:
            List of steam moves
        """
        steam_moves = []
        
        with get_db() as db:
            # Get recent matches
            recent_matches = db.query(Match).filter(
                Match.start_time > datetime.utcnow()
            ).all()
            
            for match in recent_matches:
                movement = self.analyze_odds_movement(match.id)
                
                if movement:
                    team1_change = abs(movement["movement"]["team1"])
                    team2_change = abs(movement["movement"]["team2"])
                    
                    if team1_change > threshold or team2_change > threshold:
                        steam_moves.append({
                            "match_id": match.id,
                            "team1": match.team1,
                            "team2": match.team2,
                            **movement,
                        })
        
        return steam_moves
