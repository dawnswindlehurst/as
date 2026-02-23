"""DEPRECATED: Moved to database/deprecated/nba_player_models.py.

This module is superseded by database/core_models.py (Player) and
database/player_stats_models.py (PlayerGameLog, PlayerSeasonStats).
"""
import warnings
warnings.warn(
    "database.nba_player_models is deprecated. Use database/core_models.py and "
    "database/player_stats_models.py instead.",
    DeprecationWarning,
    stacklevel=2,
)
from database.deprecated.nba_player_models import (  # noqa: F401
    NBAPlayer,
    NBAPlayerGameLog,
    NBAPlayerSeasonStats,
)
