"""Database models for ID mapping between platforms."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, UniqueConstraint
from database.models import Base


class PlayerIdMapping(Base):
    """Mapping of player IDs between platforms."""
    __tablename__ = "player_id_mappings"
    __table_args__ = (UniqueConstraint("player_id", "platform", name="_player_platform_uc"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    platform = Column(String(50), nullable=False, index=True)  # "espn", "superbet", "scorealarm"
    external_id = Column(String(100), nullable=False, index=True)
    external_name = Column(String(200), nullable=True)  # Name as it appears on platform

    confidence = Column(Float, default=1.0)  # Match confidence (1.0 = exact match)
    matched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    matched_by = Column(String(50), nullable=True)  # "exact", "fuzzy", "manual"


class TeamIdMapping(Base):
    """Mapping of team IDs between platforms."""
    __tablename__ = "team_id_mappings"
    __table_args__ = (UniqueConstraint("team_id", "platform", name="_team_platform_uc"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)

    platform = Column(String(50), nullable=False, index=True)  # "scorealarm", "superbet", "espn"
    external_id = Column(String(100), nullable=False, index=True)
    external_name = Column(String(200), nullable=True)  # Name as it appears on platform

    confidence = Column(Float, default=1.0)
    matched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    matched_by = Column(String(50), nullable=True)
