"""Professional sports betting analytics functions.

This module provides comprehensive analysis functions for NBA player props,
soccer BTTS, esports map analysis, and more.
"""
from typing import Dict, Optional, List
from database.db import get_db_session
from database.historical_models import (
    NBAPlayerGameStats, NBAGame, NBATeamStats,
    SoccerMatch, SoccerTeamStats,
    EsportsMatch, EsportsTeamStats, EsportsMapStats
)


class BettingAnalytics:
    """Professional betting analytics for all sports."""
    
    def __init__(self):
        """Initialize analytics."""
        self.db = get_db_session()
    
    def get_player_prop_analysis(self, player_name: str, prop_type: str, line: float) -> Dict:
        """Get comprehensive NBA player prop analysis.
        
        Args:
            player_name: Player name
            prop_type: Type of prop ("points", "rebounds", "assists", "pra", etc.)
            line: Prop line (e.g., 25.5)
            
        Returns:
            Comprehensive analysis dict with all splits
            
        Example:
            >>> analytics = BettingAnalytics()
            >>> props = analytics.get_player_prop_analysis("LeBron James", "points", 25.5)
            >>> print(f"Overall: {props['overall']['avg']} avg, {props['overall']['over_rate']}% over rate")
        """
        # Query player game stats
        stats = self.db.query(NBAPlayerGameStats).filter(
            NBAPlayerGameStats.player_name == player_name
        ).all()
        
        if not stats:
            return {"error": "Player not found"}
        
        # Get the stat values based on prop_type
        values = []
        for stat in stats:
            if prop_type == "points":
                values.append(stat.points or 0)
            elif prop_type == "rebounds":
                values.append(stat.rebounds_total or 0)
            elif prop_type == "assists":
                values.append(stat.assists or 0)
            elif prop_type == "pra":
                values.append(stat.pts_reb_ast or 0)
        
        if not values:
            return {"error": "No stats found"}
        
        # Calculate overall stats
        over_count = sum(1 for v in values if v > line)
        under_count = len(values) - over_count
        avg = sum(values) / len(values) if values else 0
        over_rate = (over_count / len(values) * 100) if values else 0
        
        # Home/Away splits
        home_values = [
            self._get_stat_value(stat, prop_type) 
            for stat in stats if stat.is_home
        ]
        away_values = [
            self._get_stat_value(stat, prop_type) 
            for stat in stats if not stat.is_home
        ]
        
        # Last 5 and 10 games
        recent_stats = sorted(stats, key=lambda x: x.created_at, reverse=True)
        last_5_values = [self._get_stat_value(stat, prop_type) for stat in recent_stats[:5]]
        last_10_values = [self._get_stat_value(stat, prop_type) for stat in recent_stats[:10]]
        
        analysis = {
            "overall": {
                "avg": round(avg, 1),
                "over_rate": round(over_rate, 1),
                "games": len(values)
            },
            "home": {
                "avg": round(sum(home_values) / len(home_values), 1) if home_values else 0,
                "over_rate": round(sum(1 for v in home_values if v > line) / len(home_values) * 100, 1) if home_values else 0,
                "games": len(home_values)
            },
            "away": {
                "avg": round(sum(away_values) / len(away_values), 1) if away_values else 0,
                "over_rate": round(sum(1 for v in away_values if v > line) / len(away_values) * 100, 1) if away_values else 0,
                "games": len(away_values)
            },
            "last_5": {
                "avg": round(sum(last_5_values) / len(last_5_values), 1) if last_5_values else 0,
                "over_rate": round(sum(1 for v in last_5_values if v > line) / len(last_5_values) * 100, 1) if last_5_values else 0,
                "trend": "UP" if last_5_values and last_5_values[0] > avg else "DOWN"
            },
            "last_10": {
                "avg": round(sum(last_10_values) / len(last_10_values), 1) if last_10_values else 0,
                "over_rate": round(sum(1 for v in last_10_values if v > line) / len(last_10_values) * 100, 1) if last_10_values else 0,
            }
        }
        
        return analysis
    
    def _get_stat_value(self, stat: NBAPlayerGameStats, prop_type: str) -> int:
        """Get stat value based on prop type.
        
        Args:
            stat: Player game stat
            prop_type: Type of prop
            
        Returns:
            Stat value
        """
        if prop_type == "points":
            return stat.points or 0
        elif prop_type == "rebounds":
            return stat.rebounds_total or 0
        elif prop_type == "assists":
            return stat.assists or 0
        elif prop_type == "pra":
            return stat.pts_reb_ast or 0
        elif prop_type == "steals":
            return stat.steals or 0
        elif prop_type == "blocks":
            return stat.blocks or 0
        return 0
    
    def get_team_btts_analysis(self, team_name: str, league: str) -> Dict:
        """Get soccer team Both Teams To Score analysis.
        
        Args:
            team_name: Team name
            league: League ID (e.g., "eng.1")
            
        Returns:
            BTTS analysis dict
            
        Example:
            >>> analytics = BettingAnalytics()
            >>> btts = analytics.get_team_btts_analysis("Liverpool", "eng.1")
            >>> print(f"BTTS Rate: {btts['overall']['rate']}%")
        """
        # Get team stats
        team_stat = self.db.query(SoccerTeamStats).filter(
            SoccerTeamStats.team == team_name,
            SoccerTeamStats.league == league
        ).first()
        
        if not team_stat:
            return {"error": "Team not found"}
        
        # Get matches
        home_matches = self.db.query(SoccerMatch).filter(
            SoccerMatch.home_team == team_name,
            SoccerMatch.league == league
        ).all()
        
        away_matches = self.db.query(SoccerMatch).filter(
            SoccerMatch.away_team == team_name,
            SoccerMatch.league == league
        ).all()
        
        # Calculate BTTS rates
        home_btts = sum(1 for m in home_matches if m.btts)
        away_btts = sum(1 for m in away_matches if m.btts)
        total_btts = home_btts + away_btts
        total_games = len(home_matches) + len(away_matches)
        
        analysis = {
            "overall": {
                "rate": round((total_btts / total_games * 100) if total_games > 0 else 0, 1),
                "games": total_games
            },
            "home": {
                "rate": round((home_btts / len(home_matches) * 100) if home_matches else 0, 1),
                "games": len(home_matches)
            },
            "away": {
                "rate": round((away_btts / len(away_matches) * 100) if away_matches else 0, 1),
                "games": len(away_matches)
            },
            "trend": "UP" if team_stat.btts_percentage and team_stat.btts_percentage > 55 else "STABLE"
        }
        
        return analysis
    
    def get_team_map_stats(self, team_name: str, game: str) -> Dict:
        """Get esports team map statistics.
        
        Args:
            team_name: Team name
            game: Game ("valorant", "cs2")
            
        Returns:
            Map stats dict
            
        Example:
            >>> analytics = BettingAnalytics()
            >>> maps = analytics.get_team_map_stats("Sentinels", "valorant")
            >>> print(f"Ascent: {maps['ascent']['win_rate']}% win rate")
        """
        # Get matches for this team
        matches = self.db.query(EsportsMatch).filter(
            EsportsMatch.game == game,
            (EsportsMatch.team1 == team_name) | (EsportsMatch.team2 == team_name)
        ).all()
        
        if not matches:
            return {"error": "Team not found"}
        
        # Get map stats
        map_data = {}
        
        for match in matches:
            map_stats = self.db.query(EsportsMapStats).filter(
                EsportsMapStats.match_id == match.match_id
            ).all()
            
            for map_stat in map_stats:
                map_name = map_stat.map_name.lower()
                
                if map_name not in map_data:
                    map_data[map_name] = {
                        "played": 0,
                        "won": 0
                    }
                
                map_data[map_name]["played"] += 1
                
                # Check if team won this map
                if map_stat.winner == team_name:
                    map_data[map_name]["won"] += 1
        
        # Calculate win rates
        result = {}
        for map_name, data in map_data.items():
            result[map_name] = {
                "played": data["played"],
                "won": data["won"],
                "win_rate": round((data["won"] / data["played"] * 100) if data["played"] > 0 else 0, 1)
            }
        
        return result
    
    def get_value_bets(self, sport: str, min_edge: float = 5.0) -> List[Dict]:
        """Get value bet opportunities.
        
        Args:
            sport: Sport type
            min_edge: Minimum edge percentage
            
        Returns:
            List of value bet opportunities
        """
        from database.historical_models import ValueBetHistory
        
        value_bets = self.db.query(ValueBetHistory).filter(
            ValueBetHistory.sport == sport,
            ValueBetHistory.edge >= min_edge,
            ValueBetHistory.result == "PENDING"
        ).all()
        
        return [
            {
                "match": vb.match_description,
                "selection": vb.selection,
                "our_prob": vb.our_probability,
                "implied_prob": vb.implied_probability,
                "edge": vb.edge,
                "odds": vb.odds,
                "confidence": vb.confidence_score
            }
            for vb in value_bets
        ]
    
    def close(self):
        """Close database connection."""
        self.db.close()


# Convenience function
def get_analytics() -> BettingAnalytics:
    """Get BettingAnalytics instance.
    
    Returns:
        BettingAnalytics instance
    """
    return BettingAnalytics()
