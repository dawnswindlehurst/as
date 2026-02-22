"""Results scraper - fetch match results."""
from typing import List, Dict, Optional
from datetime import datetime
from database.db import get_db
from database.models import Match
from utils.logger import log


class ResultsScraper:
    """Scraper for fetching match results."""
    
    def __init__(self):
        pass
    
    def fetch_pending_results(self) -> List[Dict]:
        """Fetch results for matches that have finished but not yet settled.
        
        Returns:
            List of match results
        """
        results = []
        
        with get_db() as db:
            # Get matches that should have finished but aren't marked as finished
            pending_matches = db.query(Match).filter(
                Match.finished == False,
                Match.start_time < datetime.utcnow()
            ).all()
            
            log.info(f"Found {len(pending_matches)} pending matches to check")
            
            for match in pending_matches:
                # TODO: Fetch actual result from game-specific scrapers
                result = self._fetch_match_result(match)
                if result:
                    results.append(result)
        
        return results
    
    def _fetch_match_result(self, match: Match) -> Optional[Dict]:
        """Fetch result for a specific match.
        
        Args:
            match: Match object
            
        Returns:
            Result dictionary or None
        """
        # TODO: Implement actual result fetching based on game type
        # This would use HLTV for CS2, VLR for Valorant, etc.
        return None
    
    def update_match_result(self, match_id: int, winner: str, team1_score: int, team2_score: int):
        """Update match result in database.
        
        Args:
            match_id: Match ID
            winner: Winner team name
            team1_score: Team 1 score
            team2_score: Team 2 score
        """
        with get_db() as db:
            match = db.query(Match).filter(Match.id == match_id).first()
            
            if match:
                match.winner = winner
                match.team1_score = team1_score
                match.team2_score = team2_score
                match.finished = True
                
                log.info(f"Updated result for match {match_id}: {winner} wins {team1_score}-{team2_score}")
