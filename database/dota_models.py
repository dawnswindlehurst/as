"""Database models for Dota 2 esports data."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.db import Base


class DotaTeam(Base):
    """Dota 2 team model."""
    __tablename__ = "dota_teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    team_id = Column(Integer, nullable=True)
    tag = Column(String(20), nullable=True)
    logo = Column(String(500), nullable=True)
    rating = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

    matches_as_team1 = relationship("DotaMatch", foreign_keys="DotaMatch.team1_id", back_populates="team1")
    matches_as_team2 = relationship("DotaMatch", foreign_keys="DotaMatch.team2_id", back_populates="team2")
    stats = relationship("DotaTeamStats", back_populates="team")


class DotaMatch(Base):
    """Dota 2 match model."""
    __tablename__ = "dota_matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(50), unique=True, nullable=False, index=True)
    team1_id = Column(Integer, ForeignKey("dota_teams.id"), nullable=True)
    team2_id = Column(Integer, ForeignKey("dota_teams.id"), nullable=True)
    team1_name = Column(String(100), nullable=True)
    team2_name = Column(String(100), nullable=True)
    team1_score = Column(Integer, default=0)
    team2_score = Column(Integer, default=0)
    winner = Column(String(100), nullable=True)
    league = Column(String(200), nullable=True)
    tournament = Column(String(200), nullable=True)
    best_of = Column(Integer, default=1)
    match_date = Column(DateTime, nullable=True, index=True)
    status = Column(String(20), default="upcoming")
    duration = Column(Integer, nullable=True)
    url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

    team1 = relationship("DotaTeam", foreign_keys=[team1_id], back_populates="matches_as_team1")
    team2 = relationship("DotaTeam", foreign_keys=[team2_id], back_populates="matches_as_team2")
    games = relationship("DotaGame", back_populates="match", cascade="all, delete-orphan")


class DotaGame(Base):
    """Individual game within a Dota 2 match."""
    __tablename__ = "dota_games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(50), ForeignKey("dota_matches.match_id"), nullable=False, index=True)
    game_number = Column(Integer, nullable=False)
    radiant_team = Column(String(100), nullable=True)
    dire_team = Column(String(100), nullable=True)
    winner = Column(String(100), nullable=True)
    duration = Column(Integer, nullable=True)
    radiant_score = Column(Integer, default=0)
    dire_score = Column(Integer, default=0)
    radiant_picks = Column(Text, nullable=True)
    radiant_bans = Column(Text, nullable=True)
    dire_picks = Column(Text, nullable=True)
    dire_bans = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    match = relationship("DotaMatch", back_populates="games")


class DotaTeamStats(Base):
    """Aggregated team statistics for Dota 2."""
    __tablename__ = "dota_team_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("dota_teams.id"), nullable=False)
    team_name = Column(String(100), nullable=True)
    league = Column(String(200), nullable=True)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    radiant_wins = Column(Integer, default=0)
    radiant_losses = Column(Integer, default=0)
    dire_wins = Column(Integer, default=0)
    dire_losses = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    avg_duration = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

    team = relationship("DotaTeam", back_populates="stats")
