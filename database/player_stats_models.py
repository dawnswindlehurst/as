"""Player statistics models."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from database.base import Base


class PlayerGameLog(Base):
    """Individual game stats for a player."""
    __tablename__ = "player_game_logs"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), index=True)

    game_date = Column(Date, nullable=False, index=True)
    season = Column(String(20), index=True)  # "2024-25"

    opponent_id = Column(Integer, ForeignKey("teams.id"))
    opponent_name = Column(String(200))
    home_away = Column(String(10))  # "home" or "away"
    result = Column(String(10))  # "W" or "L"

    minutes = Column(Integer, default=0)

    # Basketball stats
    points = Column(Integer, default=0)
    rebounds = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    fouls = Column(Integer, default=0)
    fgm = Column(Integer, default=0)
    fga = Column(Integer, default=0)
    fg3m = Column(Integer, default=0)
    fg3a = Column(Integer, default=0)
    ftm = Column(Integer, default=0)
    fta = Column(Integer, default=0)

    # Soccer stats
    goals = Column(Integer, default=0)
    soccer_assists = Column(Integer, default=0)
    shots = Column(Integer, default=0)
    shots_on_target = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)

    # Derived (betting combos)
    pts_reb = Column(Integer, default=0)
    pts_ast = Column(Integer, default=0)
    reb_ast = Column(Integer, default=0)
    pts_reb_ast = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    player = relationship("Player", back_populates="game_logs")
    match = relationship("Match")


class PlayerSeasonStats(Base):
    """Season averages for a player."""
    __tablename__ = "player_season_stats"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    season = Column(String(20), nullable=False, index=True)  # "2024-25"

    games_played = Column(Integer, default=0)

    # Basketball averages
    ppg = Column(Float, default=0)
    rpg = Column(Float, default=0)
    apg = Column(Float, default=0)
    spg = Column(Float, default=0)
    bpg = Column(Float, default=0)
    topg = Column(Float, default=0)
    mpg = Column(Float, default=0)
    fg_pct = Column(Float, default=0)
    fg3_pct = Column(Float, default=0)
    ft_pct = Column(Float, default=0)

    # Betting combos
    pts_reb_avg = Column(Float, default=0)
    pts_ast_avg = Column(Float, default=0)
    reb_ast_avg = Column(Float, default=0)
    pts_reb_ast_avg = Column(Float, default=0)

    # Soccer totals
    goals_total = Column(Integer, default=0)
    assists_total = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    player = relationship("Player", back_populates="season_stats")
