"""Map-specific features for games with maps."""
from typing import Dict, List
from database.db import get_db
from database.models import Match


class MapFeatures:
    """Calculate map-specific features (for CS2, Valorant)."""
    
    def __init__(self):
        pass
    
    def get_map_stats(self, team: str, game: str, map_name: str) -> Dict:
        """Get team statistics on a specific map.
        
        Args:
            team: Team name
            game: Game name
            map_name: Map name
            
        Returns:
            Dictionary with map statistics
        """
        # TODO: This would require storing map-specific data
        # For now, returns a placeholder structure
        return {
            "map": map_name,
            "matches_played": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.5,
            "avg_rounds_won": 0.0,
            "avg_rounds_lost": 0.0,
        }
    
    def get_map_pool_strength(self, team: str, game: str, maps: List[str]) -> Dict:
        """Get team's overall map pool strength.
        
        Args:
            team: Team name
            game: Game name
            maps: List of maps to consider
            
        Returns:
            Dictionary with map pool statistics
        """
        map_stats = {}
        total_wins = 0
        total_matches = 0
        
        for map_name in maps:
            stats = self.get_map_stats(team, game, map_name)
            map_stats[map_name] = stats
            total_wins += stats["wins"]
            total_matches += stats["matches_played"]
        
        return {
            "maps": map_stats,
            "overall_win_rate": total_wins / total_matches if total_matches > 0 else 0.5,
            "strong_maps": [m for m, s in map_stats.items() if s["win_rate"] > 0.6],
            "weak_maps": [m for m, s in map_stats.items() if s["win_rate"] < 0.4],
        }
    
    def compare_map_pools(
        self, team1: str, team2: str, game: str, maps: List[str]
    ) -> Dict:
        """Compare map pool strength between two teams.
        
        Args:
            team1: Team 1 name
            team2: Team 2 name
            game: Game name
            maps: List of maps to consider
            
        Returns:
            Dictionary with comparison
        """
        team1_pool = self.get_map_pool_strength(team1, game, maps)
        team2_pool = self.get_map_pool_strength(team2, game, maps)
        
        return {
            "team1": team1_pool,
            "team2": team2_pool,
            "team1_advantage_maps": list(
                set(team1_pool["strong_maps"]) & set(team2_pool["weak_maps"])
            ),
            "team2_advantage_maps": list(
                set(team2_pool["strong_maps"]) & set(team1_pool["weak_maps"])
            ),
        }
