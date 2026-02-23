"""Database models for players (multi-sport)."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from database.models import Base


class Player(Base):
    """Universal player model (multi-sport)."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    sport_id = Column(Integer, nullable=False, index=True)  # 4=NBA, 5=Futebol
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)

    # External IDs for linking between platforms
    espn_id = Column(String(100), unique=True, nullable=True, index=True)  # Primary for NBA
    superbet_id = Column(String(100), nullable=True, index=True)  # For player prop odds
    scorealarm_id = Column(String(100), nullable=True, index=True)  # Primary for Soccer

    # Player info
    position = Column(String(20), nullable=True)  # "PG", "SG", "SF", "PF", "C" or "FW", "MF", "DF", "GK"
    jersey_number = Column(String(10), nullable=True)
    nationality = Column(String(100), nullable=True)
    birth_date = Column(Date, nullable=True)
    height = Column(String(20), nullable=True)
    weight = Column(String(20), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    team = relationship("Team", back_populates="players")
    game_logs = relationship("PlayerGameLog", back_populates="player", cascade="all, delete-orphan")
    season_stats = relationship("PlayerSeasonStats", back_populates="player", cascade="all, delete-orphan")


class PlayerGameLog(Base):
    """Individual game stats for a player."""
    __tablename__ = "player_game_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    sport_id = Column(Integer, nullable=False)
    game_id = Column(String(100), nullable=True, index=True)  # External game ID
    game_date = Column(DateTime, nullable=True, index=True)
    season = Column(String(20), nullable=True)  # "2024-25"

    # Game context
    opponent = Column(String(100), nullable=True)
    opponent_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    home_away = Column(String(10), nullable=True)  # "home" or "away"
    result = Column(String(10), nullable=True)  # "W" or "L"

    # Common stats
    minutes = Column(Integer, default=0)
    points = Column(Integer, default=0)

    # Basketball stats
    rebounds = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    fouls = Column(Integer, default=0)
    fgm = Column(Integer, default=0)  # Field goals made
    fga = Column(Integer, default=0)  # Field goals attempted
    fg3m = Column(Integer, default=0)  # 3-pointers made
    fg3a = Column(Integer, default=0)  # 3-pointers attempted
    ftm = Column(Integer, default=0)  # Free throws made
    fta = Column(Integer, default=0)  # Free throws attempted

    # Soccer stats
    goals = Column(Integer, default=0)
    soccer_assists = Column(Integer, default=0)  # Named differently to avoid conflict
    shots = Column(Integer, default=0)
    shots_on_target = Column(Integer, default=0)
    passes = Column(Integer, default=0)
    pass_accuracy = Column(Float, nullable=True)
    tackles = Column(Integer, default=0)
    interceptions = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)

    # Derived stats for betting (NBA)
    pts_reb = Column(Integer, default=0)  # PTS + REB
    pts_ast = Column(Integer, default=0)  # PTS + AST
    reb_ast = Column(Integer, default=0)  # REB + AST
    pts_reb_ast = Column(Integer, default=0)  # PTS + REB + AST

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    player = relationship("Player", back_populates="game_logs")


class PlayerSeasonStats(Base):
    """Season averages for a player."""
    __tablename__ = "player_season_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    sport_id = Column(Integer, nullable=False)
    season = Column(String(20), nullable=False, index=True)  # "2024-25"

    games_played = Column(Integer, default=0)

    # Basketball averages
    ppg = Column(Float, default=0)  # Points per game
    rpg = Column(Float, default=0)  # Rebounds per game
    apg = Column(Float, default=0)  # Assists per game
    spg = Column(Float, default=0)  # Steals per game
    bpg = Column(Float, default=0)  # Blocks per game
    topg = Column(Float, default=0)  # Turnovers per game
    mpg = Column(Float, default=0)  # Minutes per game
    fg_pct = Column(Float, default=0)
    fg3_pct = Column(Float, default=0)
    ft_pct = Column(Float, default=0)

    # Combo averages for betting
    pts_reb_avg = Column(Float, default=0)
    pts_ast_avg = Column(Float, default=0)
    reb_ast_avg = Column(Float, default=0)
    pts_reb_ast_avg = Column(Float, default=0)

    # Soccer stats
    goals_total = Column(Integer, default=0)
    assists_total = Column(Integer, default=0)
    goals_per_90 = Column(Float, nullable=True)
    assists_per_90 = Column(Float, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    player = relationship("Player", back_populates="season_stats")
