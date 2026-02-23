"""Counter-Strike 2 (CS2) game implementation."""
import asyncio
from typing import Dict, List, Optional
from games.base import GameBase
from scrapers.cs2 import CS2Unified


class CS2(GameBase):
    """Counter-Strike 2 implementation.

    Data source: HLTV
    Features:
    - Map-based gameplay (BO1, BO3, BO5)
    - No draft phase
    - 7 maps in active pool
    """

    def __init__(self):
        super().__init__()
        self.category = "pc"
        self.has_maps = True
        self.has_draft = False
        self.data_source = "HLTV"
        self.map_pool = [
            "Mirage", "Inferno", "Nuke", "Overpass",
            "Vertigo", "Ancient", "Anubis"
        ]
        self._hltv = CS2Unified()

    def get_upcoming_matches(self) -> List[Dict]:
        """Fetch upcoming CS2 matches from HLTV.

        Returns:
            List of match dictionaries
        """
        try:
            matches = asyncio.run(self._hltv.get_upcoming_matches())
            return [
                {
                    'game': 'CS2',
                    'team1': m.team1.name,
                    'team2': m.team2.name,
                    'tournament': m.tournament,
                    'best_of': m.best_of,
                    'time': m.match_date,
                    'url': m.url,
                }
                for m in matches
            ]
        except Exception:
            return []

    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get CS2 match details from HLTV.

        Args:
            match_id: HLTV match ID

        Returns:
            Match details dictionary
        """
        try:
            match = asyncio.run(self._hltv.get_match_details(match_id))
            if match:
                return {
                    'match_id': match.match_id,
                    'team1': match.team1.name,
                    'team2': match.team2.name,
                    'score1': match.team1_score,
                    'score2': match.team2_score,
                    'maps': match.maps,
                    'winner': match.winner,
                }
            return None
        except Exception:
            return None

    def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get CS2 team statistics from HLTV.

        Args:
            team_name: Team name

        Returns:
            Team statistics
        """
        try:
            return asyncio.run(self._hltv.get_team_stats(team_name))
        except Exception:
            return None

    def close(self):
        """Close HLTV scraper resources."""
        try:
            asyncio.run(self._hltv.close())
        except Exception:
            pass
    
    def get_supported_markets(self) -> List[str]:
        """Get supported markets for CS2.
        
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
