"""DEPRECATED: Moved to database/deprecated/valorant_models.py.

This module is superseded by database/esports_models.py (EsportsStats).
"""
import warnings
warnings.warn(
    "database.valorant_models is deprecated. Use database/esports_models.py instead.",
    DeprecationWarning,
    stacklevel=2,
)
from database.deprecated.valorant_models import (  # noqa: F401
    ValorantTeam,
    ValorantMatch,
    ValorantMap,
)
