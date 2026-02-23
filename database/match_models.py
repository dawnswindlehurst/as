"""Match models - base table for all sports."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.base import Base


class Match(Base):
    """Base match table - common fields for all sports."""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), index=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), index=True)

    # Teams
    team1_id = Column(Integer, ForeignKey("teams.id"), index=True)
    team2_id = Column(Integer, ForeignKey("teams.id"), index=True)
    team1_name = Column(String(200))  # Denormalized for convenience
    team2_name = Column(String(200))

    # External IDs
    scorealarm_id = Column(String(100), unique=True, index=True)  # br:match:xxx
    superbet_id = Column(String(100), index=True)  # ax:match:xxx

    # Match info
    match_date = Column(DateTime, nullable=False, index=True)
    status = Column(Integer, default=0)  # 0=scheduled, 100=finished

    # Score
    team1_score = Column(Integer)
    team2_score = Column(Integer)

    is_finished = Column(Boolean, default=False, index=True)
    finished_at = Column(DateTime)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    sport = relationship("Sport")
    tournament = relationship("Tournament")
    season = relationship("Season")
    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])

    # Sport-specific stats (one-to-one)
    football_stats = relationship("FootballStats", back_populates="match", uselist=False)
    basketball_stats = relationship("BasketballStats", back_populates="match", uselist=False)
    tennis_stats = relationship("TennisStats", back_populates="match", uselist=False)
    esports_stats = relationship("EsportsStats", back_populates="match", uselist=False)

    # Scores by period
    scores = relationship("MatchScore", back_populates="match")

    # Odds
    odds = relationship("OddsHistory", back_populates="match")


class MatchScore(Base):
    """Scores by period (quarter, half, set, etc)."""
    __tablename__ = "match_scores"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)

    period_type = Column(String(20))  # "q1", "q2", "half1", "set1", etc
    period_number = Column(Integer)
    team1_score = Column(Integer)
    team2_score = Column(Integer)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    match = relationship("Match", back_populates="scores")
