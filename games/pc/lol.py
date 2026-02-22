"""League of Legends (LoL) game implementation."""
from typing import Dict, List, Optional
import asyncio
from games.base import GameBase
from scrapers.lol import LoLUnified


class LoL(GameBase):
    """League of Legends implementation.
    
    Data sources:
    - LoL Esports API: Match schedules and live results
    - Oracle's Elixir: Detailed statistics and historical data
    
    Features:
    - Draft phase (champion select)
    - Single map (Summoner's Rift)
    - BO1, BO3, BO5 formats
    """
    
    def __init__(self):
        super().__init__()
        self.category = "pc"
        self.has_maps = False
        self.has_draft = True
        self.data_source = "LoL Esports API + Oracle's Elixir"
        self.lol_api = LoLUnified()
    
    def get_upcoming_matches(self) -> List[Dict]:
        """Fetch upcoming LoL matches.
        
        Returns:
            List of match dictionaries
        """
        try:
            matches = asyncio.run(self.lol_api.get_upcoming_matches())
            return [self._match_to_dict(match) for match in matches]
        except Exception:
            return []
    
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get LoL match details.
        
        Args:
            match_id: Match ID
            
        Returns:
            Match details dictionary
        """
        try:
            match = asyncio.run(self.lol_api.get_match_details(match_id))
            if match:
                return {
                    'match_id': match.match_id,
                    'team1': match.team1,
                    'team2': match.team2,
                    'score1': match.score1,
                    'score2': match.score2,
                    'winner': match.winner,
                    'date': match.date,
                    'league': match.league,
                    'tournament': match.tournament,
                    'games': [self._game_to_dict(game) for game in match.games]
                }
            return None
        except Exception:
            return None
    
    def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get LoL team statistics.
        
        Args:
            team_name: Team name
            
        Returns:
            Team statistics
        """
        try:
            return asyncio.run(self.lol_api.get_team_stats(team_name))
        except Exception:
            return None
    
    def get_draft_analysis(self, match_id: str) -> Optional[Dict]:
        """Get draft/pick-ban analysis for a match.
        
        Args:
            match_id: Match ID
            
        Returns:
            Draft analysis dictionary with picks/bans
        """
        try:
            return asyncio.run(self.lol_api.get_draft_analysis(match_id))
        except Exception:
            return None
    
    def get_supported_markets(self) -> List[str]:
        """Get supported markets for LoL.
        
        Returns:
            List of market types
        """
        return [
            "match_winner",
            "handicap",
            "total_maps",
            "first_blood",
            "first_dragon",
            "first_baron",
        ]
    
    def _match_to_dict(self, match) -> Dict:
        """Convert LoLMatch object to dictionary.
        
        Args:
            match: LoLMatch object
            
        Returns:
            Dictionary representation
        """
        return {
            'match_id': match.match_id,
            'team1': {
                'name': match.team1.name,
                'code': match.team1.code,
                'league': match.team1.league,
                'region': match.team1.region,
                'logo': match.team1.logo,
            },
            'team2': {
                'name': match.team2.name,
                'code': match.team2.code,
                'league': match.team2.league,
                'region': match.team2.region,
                'logo': match.team2.logo,
            },
            'league': match.league,
            'tournament': match.tournament,
            'date': match.date,
            'status': match.status,
            'best_of': match.best_of,
            'url': match.url,
        }
    
    def _game_to_dict(self, game) -> Dict:
        """Convert LoLGameResult object to dictionary.
        
        Args:
            game: LoLGameResult object
            
        Returns:
            Dictionary representation
        """
        return {
            'game_number': game.game_number,
            'winner': game.winner,
            'duration': game.duration,
            'blue_team': game.blue_team,
            'red_team': game.red_team,
            'blue_picks': game.blue_picks,
            'red_picks': game.red_picks,
            'blue_bans': game.blue_bans,
            'red_bans': game.red_bans,
        }
