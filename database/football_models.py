"""Football (Soccer) specific models."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.base import Base


class FootballStats(Base):
    """Football match statistics."""
    __tablename__ = "football_stats"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False, index=True)

    # Expected Goals
    xg_home = Column(Float)
    xg_away = Column(Float)

    # Shots
    shots_home = Column(Integer)
    shots_away = Column(Integer)
    shots_on_target_home = Column(Integer)
    shots_on_target_away = Column(Integer)

    # Possession
    possession_home = Column(Float)  # 0.55 = 55%
    possession_away = Column(Float)

    # Set pieces
    corners_home = Column(Integer)
    corners_away = Column(Integer)

    # Discipline
    fouls_home = Column(Integer)
    fouls_away = Column(Integer)
    yellow_cards_home = Column(Integer)
    yellow_cards_away = Column(Integer)
    red_cards_home = Column(Integer)
    red_cards_away = Column(Integer)

    # Goals by half
    first_half_home = Column(Integer)
    first_half_away = Column(Integer)
    second_half_home = Column(Integer)
    second_half_away = Column(Integer)

    # Raw data
    goal_events = Column(JSON)  # List of goal events with player, minute, etc
    match_stats_raw = Column(JSON)  # Full raw stats from API

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    match = relationship("Match", back_populates="football_stats")
