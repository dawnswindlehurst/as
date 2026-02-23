"""LoL (League of Legends) database models."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.models import Base


class LolTeam(Base):
    """LoL team."""
    __tablename__ = "lol_teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(20))
    league = Column(String(100))
    region = Column(String(50))
    logo = Column(String(500))
    lol_esports_id = Column(String(100), unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    matches_as_team1 = relationship("LolMatch", foreign_keys="LolMatch.team1_id", back_populates="team1")
    matches_as_team2 = relationship("LolMatch", foreign_keys="LolMatch.team2_id", back_populates="team2")
    stats = relationship("LolTeamStats", back_populates="team")


class LolMatch(Base):
    """LoL match."""
    __tablename__ = "lol_matches"

    id = Column(Integer, primary_key=True)
    match_id = Column(String(100), unique=True, nullable=False, index=True)
    team1_id = Column(Integer, ForeignKey("lol_teams.id"), nullable=True)
    team2_id = Column(Integer, ForeignKey("lol_teams.id"), nullable=True)
    team1_name = Column(String(200))
    team2_name = Column(String(200))
    team1_score = Column(Integer, default=0)
    team2_score = Column(Integer, default=0)
    winner = Column(String(200))
    league = Column(String(200))
    tournament = Column(String(200))
    best_of = Column(Integer, default=1)
    match_date = Column(DateTime, nullable=True, index=True)
    status = Column(String(20), default="upcoming")  # upcoming, live, completed
    url = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    team1 = relationship("LolTeam", foreign_keys=[team1_id], back_populates="matches_as_team1")
    team2 = relationship("LolTeam", foreign_keys=[team2_id], back_populates="matches_as_team2")
    games = relationship("LolGame", back_populates="match", cascade="all, delete-orphan")


class LolGame(Base):
    """Individual game within a LoL match."""
    __tablename__ = "lol_games"

    id = Column(Integer, primary_key=True)
    match_id = Column(String(100), ForeignKey("lol_matches.match_id"), nullable=False)
    game_number = Column(Integer, nullable=False)
    blue_team = Column(String(200))
    red_team = Column(String(200))
    winner = Column(String(200))
    duration = Column(String(20))
    blue_picks = Column(JSON)
    red_picks = Column(JSON)
    blue_bans = Column(JSON)
    red_bans = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    match = relationship("LolMatch", back_populates="games")


class LolTeamStats(Base):
    """LoL team statistics per league/season."""
    __tablename__ = "lol_team_stats"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("lol_teams.id"), nullable=False)
    team_name = Column(String(200))
    league = Column(String(100))
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    blue_side_wins = Column(Integer, default=0)
    blue_side_losses = Column(Integer, default=0)
    red_side_wins = Column(Integer, default=0)
    red_side_losses = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    season = Column(String(50))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    team = relationship("LolTeam", back_populates="stats")
