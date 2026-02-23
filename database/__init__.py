"""Database models."""

# Core
from database.core_models import Sport, Tournament, Season, Team, Player

# Matches
from database.match_models import Match, MatchScore

# Sport-specific stats
from database.football_models import FootballStats
from database.basketball_models import BasketballStats
from database.tennis_models import TennisStats
from database.esports_models import EsportsStats

# Odds
from database.odds_models import OddsHistory, PlayerProp

# Player stats
from database.player_stats_models import PlayerGameLog, PlayerSeasonStats

__all__ = [
    # Core
    "Sport", "Tournament", "Season", "Team", "Player",
    # Matches
    "Match", "MatchScore",
    # Stats
    "FootballStats", "BasketballStats", "TennisStats", "EsportsStats",
    # Odds
    "OddsHistory", "PlayerProp",
    # Player stats
    "PlayerGameLog", "PlayerSeasonStats",
]

