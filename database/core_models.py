"""Core database models shared across all sports."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from database.base import Base


class Sport(Base):
    """Sports table."""
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    name_pt = Column(String(100))  # Nome em português
    superbet_id = Column(Integer, unique=True, index=True)
    scorealarm_id = Column(Integer, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Tournament(Base):
    """Tournaments/Leagues."""
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False, index=True)
    country = Column(String(100))

    # External IDs
    scorealarm_id = Column(String(100), unique=True, index=True)
    superbet_id = Column(String(100), index=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sport = relationship("Sport")
    seasons = relationship("Season", back_populates="tournament")


class Season(Base):
    """Seasons within tournaments."""
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False, index=True)

    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)

    scorealarm_id = Column(String(100), unique=True, index=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tournament = relationship("Tournament", back_populates="seasons")


class Team(Base):
    """Universal team model for all sports."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    short_name = Column(String(50))
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False, index=True)

    # External IDs - para linkar entre plataformas
    scorealarm_id = Column(String(100), unique=True, index=True)  # ax:team:xxx
    superbet_id = Column(String(100), index=True)
    espn_id = Column(String(100), index=True)

    # Info
    country = Column(String(100))
    logo_url = Column(String(500))

    # NBA specific
    conference = Column(String(20))  # "East", "West"
    division = Column(String(50))

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    sport = relationship("Sport")
    players = relationship("Player", back_populates="team")


class Player(Base):
    """Universal player model for all sports."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), index=True)

    # External IDs - para linkar entre plataformas
    espn_id = Column(String(100), unique=True, index=True)  # Primary for NBA
    superbet_id = Column(String(100), index=True)  # For player props
    scorealarm_id = Column(String(100), index=True)  # For soccer

    # Info
    position = Column(String(20))
    jersey_number = Column(String(10))
    nationality = Column(String(100))
    birth_date = Column(Date)
    height = Column(String(20))
    weight = Column(String(20))

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    sport = relationship("Sport")
    team = relationship("Team", back_populates="players")
    game_logs = relationship("PlayerGameLog", back_populates="player")
    season_stats = relationship("PlayerSeasonStats", back_populates="player")
