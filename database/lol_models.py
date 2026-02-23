"""DEPRECATED: Moved to database/deprecated/lol_models.py.

This module is superseded by database/esports_models.py (EsportsStats).
"""
import warnings
warnings.warn(
    "database.lol_models is deprecated. Use database/esports_models.py instead.",
    DeprecationWarning,
    stacklevel=2,
)
from database.deprecated.lol_models import (  # noqa: F401
    LolTeam,
    LolMatch,
    LolGame,
    LolTeamStats,
)
