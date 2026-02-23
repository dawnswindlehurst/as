"""Database models for teams (multi-sport)."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.models import Base


class Team(Base):
    """Universal team model (multi-sport)."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    short_name = Column(String(50), nullable=True)
    sport_id = Column(Integer, nullable=False, index=True)  # 4=NBA/Basquete, 5=Futebol

    # External IDs for linking between platforms
    scorealarm_id = Column(String(100), unique=True, nullable=True, index=True)  # Primary for teams
    superbet_id = Column(String(100), nullable=True, index=True)  # For odds
    espn_id = Column(String(100), nullable=True, index=True)  # For NBA

    # Team info
    country = Column(String(100), nullable=True)
    league = Column(String(200), nullable=True)
    conference = Column(String(50), nullable=True)  # NBA: "East", "West"
    division = Column(String(100), nullable=True)
    logo_url = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    players = relationship("Player", back_populates="team")
    stats = relationship("TeamStats", back_populates="team")


class TeamStats(Base):
    """Team statistics per season."""
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    sport_id = Column(Integer, nullable=False)
    season = Column(String(20), nullable=False, index=True)  # "2024-25"

    # Record
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)  # Soccer
    home_wins = Column(Integer, default=0)
    home_losses = Column(Integer, default=0)
    away_wins = Column(Integer, default=0)
    away_losses = Column(Integer, default=0)

    # NBA specific
    offensive_rating = Column(Float, nullable=True)
    defensive_rating = Column(Float, nullable=True)
    net_rating = Column(Float, nullable=True)
    pace = Column(Float, nullable=True)

    # Soccer specific
    goals_scored = Column(Integer, nullable=True)
    goals_conceded = Column(Integer, nullable=True)
    clean_sheets = Column(Integer, nullable=True)

    # Betting stats
    ats_wins = Column(Integer, default=0)  # Against the spread wins
    ats_losses = Column(Integer, default=0)
    over_hits = Column(Integer, default=0)  # Over/under
    under_hits = Column(Integer, default=0)

    # Form
    form = Column(String(10), nullable=True)  # "WWLWW"
    current_streak = Column(String(10), nullable=True)  # "W3" or "L2"

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    team = relationship("Team", back_populates="stats")
