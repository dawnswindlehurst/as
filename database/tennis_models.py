"""Tennis specific models."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.base import Base


class TennisStats(Base):
    """Tennis match statistics."""
    __tablename__ = "tennis_stats"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False, index=True)

    # Match info
    surface = Column(String(20))  # "hard", "clay", "grass"
    best_of = Column(Integer)  # 3 or 5

    # Sets
    sets_home = Column(Integer)
    sets_away = Column(Integer)
    set1_home = Column(Integer)
    set1_away = Column(Integer)
    set2_home = Column(Integer)
    set2_away = Column(Integer)
    set3_home = Column(Integer)
    set3_away = Column(Integer)
    set4_home = Column(Integer)
    set4_away = Column(Integer)
    set5_home = Column(Integer)
    set5_away = Column(Integer)

    # Games
    total_games = Column(Integer)

    # Serve stats
    aces_home = Column(Integer)
    aces_away = Column(Integer)
    double_faults_home = Column(Integer)
    double_faults_away = Column(Integer)
    first_serve_pct_home = Column(Float)
    first_serve_pct_away = Column(Float)
    first_serve_won_pct_home = Column(Float)
    first_serve_won_pct_away = Column(Float)

    # Break points
    break_points_won_home = Column(Integer)
    break_points_total_home = Column(Integer)
    break_points_won_away = Column(Integer)
    break_points_total_away = Column(Integer)

    # Duration
    duration_minutes = Column(Integer)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    match = relationship("Match", back_populates="tennis_stats")
