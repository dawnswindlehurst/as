"""Basketball specific models."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.base import Base


class BasketballStats(Base):
    """Basketball match statistics."""
    __tablename__ = "basketball_stats"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False, index=True)

    # Quarters
    q1_home = Column(Integer)
    q1_away = Column(Integer)
    q2_home = Column(Integer)
    q2_away = Column(Integer)
    q3_home = Column(Integer)
    q3_away = Column(Integer)
    q4_home = Column(Integer)
    q4_away = Column(Integer)
    ot_home = Column(Integer)
    ot_away = Column(Integer)

    # Shooting
    fgm_home = Column(Integer)  # Field goals made
    fga_home = Column(Integer)  # Field goals attempted
    fgm_away = Column(Integer)
    fga_away = Column(Integer)
    fg3m_home = Column(Integer)  # 3-pointers made
    fg3a_home = Column(Integer)
    fg3m_away = Column(Integer)
    fg3a_away = Column(Integer)
    ftm_home = Column(Integer)  # Free throws made
    fta_home = Column(Integer)
    ftm_away = Column(Integer)
    fta_away = Column(Integer)

    # Box score
    rebounds_home = Column(Integer)
    rebounds_away = Column(Integer)
    assists_home = Column(Integer)
    assists_away = Column(Integer)
    steals_home = Column(Integer)
    steals_away = Column(Integer)
    blocks_home = Column(Integer)
    blocks_away = Column(Integer)
    turnovers_home = Column(Integer)
    turnovers_away = Column(Integer)
    fouls_home = Column(Integer)
    fouls_away = Column(Integer)

    # Game flow
    biggest_lead_home = Column(Integer)
    biggest_lead_away = Column(Integer)
    lead_changes = Column(Integer)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    match = relationship("Match", back_populates="basketball_stats")
