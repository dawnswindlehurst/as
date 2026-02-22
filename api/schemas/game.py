"""Pydantic schemas for games."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class GameBase(BaseModel):
    """Base game schema."""
    game: str
    team1: str
    team2: str
    start_time: datetime
    tournament: Optional[str] = None
    best_of: int = 1


class GameResponse(GameBase):
    """Game response schema."""
    id: int
    winner: Optional[str] = None
    team1_score: Optional[int] = None
    team2_score: Optional[int] = None
    finished: bool = False
    is_live: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class OddsSchema(BaseModel):
    """Odds schema."""
    bookmaker: str
    team1_odds: Optional[float] = None
    team2_odds: Optional[float] = None
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GameWithOdds(GameResponse):
    """Game with odds information."""
    odds: List[OddsSchema] = []
    
    model_config = ConfigDict(from_attributes=True)
