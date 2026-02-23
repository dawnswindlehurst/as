"""Database models for NBA player data."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.db import Base


class NBAPlayer(Base):
    """NBA player model."""
    __tablename__ = "nba_players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    espn_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    team_id = Column(Integer, nullable=True)
    team_name = Column(String(100), nullable=True)
    position = Column(String(20), nullable=True)
    jersey_number = Column(String(10), nullable=True)
    height = Column(String(20), nullable=True)
    weight = Column(String(20), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

    game_logs = relationship("NBAPlayerGameLog", back_populates="player", cascade="all, delete-orphan")
    season_stats = relationship("NBAPlayerSeasonStats", back_populates="player", cascade="all, delete-orphan")


class NBAPlayerGameLog(Base):
    """Individual game stats for a player."""
    __tablename__ = "nba_player_game_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("nba_players.id"), nullable=False, index=True)
    game_id = Column(String(50), nullable=True, index=True)
    game_date = Column(DateTime, nullable=True, index=True)
    opponent = Column(String(50), nullable=True)
    home_away = Column(String(10), nullable=True)  # 'home' or 'away'
    result = Column(String(10), nullable=True)  # 'W' or 'L'
    
    # Core stats
    minutes = Column(Integer, default=0)
    points = Column(Integer, default=0)
    rebounds = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    fouls = Column(Integer, default=0)
    
    # Shooting
    fgm = Column(Integer, default=0)  # Field goals made
    fga = Column(Integer, default=0)  # Field goals attempted
    fg3m = Column(Integer, default=0)  # 3-pointers made
    fg3a = Column(Integer, default=0)  # 3-pointers attempted
    ftm = Column(Integer, default=0)  # Free throws made
    fta = Column(Integer, default=0)  # Free throws attempted
    
    # Derived (for betting lines)
    pts_reb = Column(Integer, default=0)  # PTS + REB
    pts_ast = Column(Integer, default=0)  # PTS + AST
    reb_ast = Column(Integer, default=0)  # REB + AST
    pts_reb_ast = Column(Integer, default=0)  # PTS + REB + AST
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    player = relationship("NBAPlayer", back_populates="game_logs")


class NBAPlayerSeasonStats(Base):
    """Season averages for a player."""
    __tablename__ = "nba_player_season_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("nba_players.id"), nullable=False, index=True)
    season = Column(String(10), nullable=False, index=True)  # e.g., "2024-25"
    games_played = Column(Integer, default=0)
    
    # Averages
    ppg = Column(Float, default=0)  # Points per game
    rpg = Column(Float, default=0)  # Rebounds per game
    apg = Column(Float, default=0)  # Assists per game
    spg = Column(Float, default=0)  # Steals per game
    bpg = Column(Float, default=0)  # Blocks per game
    topg = Column(Float, default=0)  # Turnovers per game
    mpg = Column(Float, default=0)  # Minutes per game
    
    # Shooting percentages
    fg_pct = Column(Float, default=0)
    fg3_pct = Column(Float, default=0)
    ft_pct = Column(Float, default=0)
    
    # Combo averages (for betting)
    pts_reb_avg = Column(Float, default=0)
    pts_ast_avg = Column(Float, default=0)
    reb_ast_avg = Column(Float, default=0)
    pts_reb_ast_avg = Column(Float, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

    player = relationship("NBAPlayer", back_populates="season_stats")
