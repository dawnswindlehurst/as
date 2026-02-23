"""DEPRECATED: Moved to database/deprecated/historical_models.py.

This module is superseded by the new clean architecture:
  - database/core_models.py      (Team, Player)
  - database/match_models.py     (Match)
  - database/basketball_models.py (BasketballStats)
  - database/football_models.py   (FootballStats)
  - database/tennis_models.py     (TennisStats)
  - database/esports_models.py    (EsportsStats)
  - database/player_stats_models.py (PlayerGameLog, PlayerSeasonStats)
"""
import warnings
warnings.warn(
    "database.historical_models is deprecated. Use the new sport-specific model files.",
    DeprecationWarning,
    stacklevel=2,
)
from database.deprecated.historical_models import (  # noqa: F401
    NBAGame,
    NBAPlayerGameStats,
    NBATeamStats,
    NBAPlayerPropsAnalysis,
    SoccerMatch,
    SoccerTeamStats,
    SoccerPlayerStats,
    EsportsMatch,
    EsportsMapStats,
    EsportsPlayerStats,
    EsportsTeamStats,
    EsportsPlayerPropsAnalysis,
    TennisMatch,
    TennisPlayerStats,
    BettingPattern,
    ValueBetHistory,
)
