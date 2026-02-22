"""Dota 2 game implementation."""
from typing import Dict, List, Optional
from games.base import GameBase
from scrapers.dota import DotaUnified
import asyncio


class Dota2(GameBase):
    """Dota 2 implementation.
    
    Data source: OpenDota API
    Features:
    - Draft phase (hero picks/bans)
    - Single map
    - BO2, BO3, BO5 formats
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Dota 2 game integration.
        
        Args:
            api_key: Optional OpenDota API key for increased rate limits
        """
        super().__init__()
        self.category = "pc"
        self.has_maps = False
        self.has_draft = True
        self.data_source = "OpenDota API"
        self._dota = DotaUnified(api_key)
    
    def get_upcoming_matches(self) -> List[Dict]:
        """Fetch upcoming Dota 2 matches.
        
        Returns:
            List of match dictionaries
        """
        matches = asyncio.run(self._dota.get_pro_matches(100))
        
        return [
            {
                'match_id': m.match_id,
                'radiant_team': m.radiant_name,
                'dire_team': m.dire_name,
                'league': m.league_name,
                'series_type': self._format_series_type(m.series_type),
                'start_time': m.start_time,
            }
            for m in matches
        ]
    
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get Dota 2 match details.
        
        Args:
            match_id: Match ID
            
        Returns:
            Match details dictionary
        """
        try:
            match = asyncio.run(self._dota.get_match_details(int(match_id)))
            
            return {
                'match_id': match.match_id,
                'duration': match.duration,
                'radiant_win': match.radiant_win,
                'radiant_score': match.radiant_score,
                'dire_score': match.dire_score,
                'draft': {
                    'radiant_picks': match.radiant_picks,
                    'radiant_bans': match.radiant_bans,
                    'dire_picks': match.dire_picks,
                    'dire_bans': match.dire_bans,
                },
                'players': match.players,
            }
        except (ValueError, KeyError, TypeError, asyncio.TimeoutError):
            return None
    
    def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get Dota 2 team statistics.
        
        Args:
            team_name: Team name or team ID as string
            
        Returns:
            Team statistics
        """
        try:
            # Try to parse as team_id first, fall back to name lookup
            try:
                team_id = int(team_name)
            except ValueError:
                # If not a number, we'd need to search by name
                # For now, return None as OpenDota API primarily uses IDs
                return None
            
            return asyncio.run(self._dota.get_team_stats(team_id))
        except (ValueError, KeyError, TypeError):
            return None
    
    def get_draft_analysis(self, match_id: str) -> Optional[Dict]:
        """Analyze hero picks and bans for a match.
        
        Args:
            match_id: Match ID
            
        Returns:
            Draft analysis with hero information
        """
        try:
            match = asyncio.run(self._dota.get_match_details(int(match_id)))
            
            # Get hero information for picks/bans
            async def get_hero_names():
                heroes_by_id = {}
                for hero_id in (match.radiant_picks + match.radiant_bans + 
                              match.dire_picks + match.dire_bans):
                    hero = await self._dota.get_hero_by_id(hero_id)
                    if hero:
                        heroes_by_id[hero_id] = hero.localized_name
                return heroes_by_id
            
            hero_names = asyncio.run(get_hero_names())
            
            return {
                'radiant': {
                    'picks': [hero_names.get(h, f'Hero {h}') for h in match.radiant_picks],
                    'bans': [hero_names.get(h, f'Hero {h}') for h in match.radiant_bans],
                },
                'dire': {
                    'picks': [hero_names.get(h, f'Hero {h}') for h in match.dire_picks],
                    'bans': [hero_names.get(h, f'Hero {h}') for h in match.dire_bans],
                },
            }
        except (ValueError, KeyError, TypeError, asyncio.TimeoutError):
            return None
    
    def _format_series_type(self, series_type: Optional[int]) -> str:
        """Format series type to human-readable string.
        
        Args:
            series_type: Series type code (0=Bo1, 1=Bo3, 2=Bo5)
            
        Returns:
            Formatted series type string
        """
        if series_type is None:
            return "Bo1"
        
        series_map = {
            0: "Bo1",
            1: "Bo3",
            2: "Bo5",
        }
        return series_map.get(series_type, "Bo1")
    
    def get_supported_markets(self) -> List[str]:
        """Get supported markets for Dota 2.
        
        Returns:
            List of market types
        """
        return [
            "match_winner",
            "handicap",
            "total_maps",
            "first_blood",
            "first_roshan",
            "total_kills",
        ]
    
    def close(self):
        """Close the Dota API client."""
        asyncio.run(self._dota.close())
