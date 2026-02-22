"""Valorant game implementation."""
from typing import Dict, List, Optional
import asyncio
from games.base import GameBase
from scrapers.vlr import VLRUnified


class Valorant(GameBase):
    """Valorant implementation.
    
    Data source: VLR.gg via vlrggapi
    Features:
    - Map-based gameplay (BO3, BO5)
    - Agent selection (similar to draft)
    - 10 maps in pool
    """
    
    def __init__(self):
        super().__init__()
        self.category = "pc"
        self.has_maps = True
        self.has_draft = True  # Agent selection
        self.data_source = "VLR.gg"
        self.map_pool = [
            "Ascent", "Bind", "Haven", "Split", "Icebox",
            "Breeze", "Fracture", "Pearl", "Lotus", "Sunset"
        ]
        self._vlr = VLRUnified()
    
    def get_upcoming_matches(self) -> List[Dict]:
        """Fetch upcoming Valorant matches from VLR.
        
        Returns:
            List of match dictionaries
        """
        try:
            matches = asyncio.run(self._vlr.get_upcoming_matches())
            
            # Convert to game-standard format
            return [
                {
                    'game': 'Valorant',
                    'team1': m.team1,
                    'team2': m.team2,
                    'tournament': m.match_event,
                    'series': m.match_series,
                    'time_until': m.time_until_match,
                    'url': m.match_page,
                }
                for m in matches
            ]
        except Exception as e:
            # Fallback handled by VLRUnified
            return []
    
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get Valorant match details from VLR.
        
        Args:
            match_id: VLR match ID
            
        Returns:
            Match details dictionary
        """
        # TODO: Implement detailed match fetching via VLR scraping
        return None
    
    def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get Valorant team statistics from VLR.
        
        Args:
            team_name: Team name
            
        Returns:
            Team statistics
        """
        # TODO: Implement team stats via rankings
        # Could use get_all_rankings and search for team
        return None
    
    def get_supported_markets(self) -> List[str]:
        """Get supported markets for Valorant.
        
        Returns:
            List of market types
        """
        return [
            "match_winner",
            "handicap",
            "total_maps",
            "map_winner",
            "total_rounds",
            "first_blood",
        ]
    
    def close(self):
        """Close VLR API resources.
        
        Call this method when done using the Valorant game instance to clean up resources.
        """
        try:
            asyncio.run(self._vlr.close())
        except Exception:
            pass


