"""DEPRECATED: Moved to database/deprecated/scorealarm_models.py.

This module is superseded by the new clean architecture:
  - database/core_models.py  (Sport, Tournament, Season, Team)
  - database/match_models.py (Match)
  - database/odds_models.py  (OddsHistory)
"""
import warnings
warnings.warn(
    "database.scorealarm_models is deprecated. Use the new architecture in "
    "database/core_models.py, database/match_models.py, and database/odds_models.py.",
    DeprecationWarning,
    stacklevel=2,
)
from database.deprecated.scorealarm_models import (  # noqa: F401
    ScorealarmSport,
    ScorealarmCategory,
    ScorealarmTournament,
    ScorealarmSeason,
    ScorealarmTeam,
    ScorealarmMatch,
    ScorealarmScore,
    OddsHistory,
    ScorealarmTeamRating,
)
