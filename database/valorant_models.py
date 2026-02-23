"""Database models for Valorant esports data."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from database.db import Base


class ValorantTeam(Base):
    """Valorant team model."""
    __tablename__ = "valorant_teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    tag = Column(String(20), nullable=True)
    logo = Column(String(500), nullable=True)
    country = Column(String(50), nullable=True)
    region = Column(String(20), nullable=True)
    rank = Column(Integer, nullable=True)
    record = Column(String(20), nullable=True)  # W-L format
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    earnings = Column(BigInteger, default=0)  # Total earnings in USD
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

    matches_as_team1 = relationship("ValorantMatch", foreign_keys="ValorantMatch.team1_id", back_populates="team1")
    matches_as_team2 = relationship("ValorantMatch", foreign_keys="ValorantMatch.team2_id", back_populates="team2")


class ValorantMatch(Base):
    """Valorant match model."""
    __tablename__ = "valorant_matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(200), unique=True, nullable=False, index=True)
    team1_id = Column(Integer, ForeignKey("valorant_teams.id"), nullable=True)
    team2_id = Column(Integer, ForeignKey("valorant_teams.id"), nullable=True)
    team1_name = Column(String(100), nullable=True)
    team2_name = Column(String(100), nullable=True)
    team1_score = Column(Integer, default=0)
    team2_score = Column(Integer, default=0)
    winner = Column(String(100), nullable=True)
    event = Column(String(300), nullable=True)
    series = Column(String(200), nullable=True)
    best_of = Column(Integer, default=3)
    match_date = Column(DateTime, nullable=True, index=True)
    time_until = Column(String(50), nullable=True)
    status = Column(String(20), default="upcoming")
    url = Column(String(500), nullable=True)
    flag1 = Column(String(20), nullable=True)
    flag2 = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

    team1 = relationship("ValorantTeam", foreign_keys=[team1_id], back_populates="matches_as_team1")
    team2 = relationship("ValorantTeam", foreign_keys=[team2_id], back_populates="matches_as_team2")
    maps = relationship("ValorantMap", back_populates="match", cascade="all, delete-orphan")


class ValorantMap(Base):
    """Individual map within a Valorant match."""
    __tablename__ = "valorant_maps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(200), ForeignKey("valorant_matches.match_id"), nullable=False, index=True)
    map_number = Column(Integer, nullable=False)
    map_name = Column(String(50), nullable=True)
    team1_rounds = Column(Integer, default=0)
    team2_rounds = Column(Integer, default=0)
    winner = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    match = relationship("ValorantMatch", back_populates="maps")
