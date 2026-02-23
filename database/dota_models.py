"""DEPRECATED: Moved to database/deprecated/dota_models.py.

This module is superseded by database/esports_models.py (EsportsStats).
"""
import warnings
warnings.warn(
    "database.dota_models is deprecated. Use database/esports_models.py instead.",
    DeprecationWarning,
    stacklevel=2,
)
from database.deprecated.dota_models import (  # noqa: F401
    DotaTeam,
    DotaMatch,
    DotaGame,
    DotaTeamStats,
)
