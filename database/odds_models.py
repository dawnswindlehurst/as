"""Odds and player props models."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.base import Base


class OddsHistory(Base):
    """Historical odds for matches."""
    __tablename__ = "odds_history"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)

    market_type = Column(String(50), nullable=False)  # "moneyline", "spread", "total"

    # Moneyline
    odds_home = Column(Float)
    odds_away = Column(Float)
    odds_draw = Column(Float)

    # Spread/Handicap
    spread_line = Column(Float)
    spread_home = Column(Float)
    spread_away = Column(Float)

    # Total (Over/Under)
    total_line = Column(Float)
    total_over = Column(Float)
    total_under = Column(Float)

    bookmaker = Column(String(50), default="superbet")
    captured_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    match = relationship("Match", back_populates="odds")


class PlayerProp(Base):
    """Player prop bets."""
    __tablename__ = "player_props"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), index=True)

    player_name = Column(String(200), nullable=False, index=True)  # Denormalized
    team_name = Column(String(200))

    prop_type = Column(String(50), nullable=False)  # "points", "rebounds", "assists", "goals"
    line = Column(Float, nullable=False)

    odds_over = Column(Float)
    odds_under = Column(Float)

    # Result tracking
    result_value = Column(Float)  # Actual value achieved
    result_hit = Column(Boolean)  # Over hit?
    settled_at = Column(DateTime)

    bookmaker = Column(String(50), default="superbet")
    captured_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    match = relationship("Match")
    player = relationship("Player")
