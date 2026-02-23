"""eSports models for LoL, Dota 2, CS2, Valorant."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.base import Base


class EsportsStats(Base):
    """eSports match statistics."""
    __tablename__ = "esports_stats"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False, index=True)

    game = Column(String(20))  # "lol", "dota2", "cs2", "valorant"
    best_of = Column(Integer)  # 1, 3, 5

    # Map/Game scores
    maps_team1 = Column(Integer)
    maps_team2 = Column(Integer)

    # Maps played (for CS2/Valorant)
    map1_name = Column(String(50))
    map1_team1 = Column(Integer)
    map1_team2 = Column(Integer)
    map2_name = Column(String(50))
    map2_team1 = Column(Integer)
    map2_team2 = Column(Integer)
    map3_name = Column(String(50))
    map3_team1 = Column(Integer)
    map3_team2 = Column(Integer)

    # Raw data
    maps_raw = Column(JSON)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    match = relationship("Match", back_populates="esports_stats")
