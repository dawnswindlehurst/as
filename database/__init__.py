"""Database module for Capivara Bet Esports."""
# Removed auto-import to avoid double registration issues
# from database import scorealarm_models
from database.team_models import Team, TeamStats
from database.player_models import Player, PlayerGameLog, PlayerSeasonStats
from database.id_mapping_models import PlayerIdMapping, TeamIdMapping
