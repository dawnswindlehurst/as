"""Pydantic schemas for players."""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class PlayerBase(BaseModel):
    """Base player schema."""
    player_id: str
    player_name: str
    team: Optional[str] = None


class PlayerStatsBase(BaseModel):
    """Base player stats schema."""
    points: Optional[int] = None
    rebounds_total: Optional[int] = None
    assists: Optional[int] = None
    steals: Optional[int] = None
    blocks: Optional[int] = None
    minutes: Optional[int] = None


class PlayerGameLog(PlayerStatsBase):
    """Player game log entry."""
    game_id: str
    game_date: str
    opponent: str
    is_home: bool
    minutes: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class PlayerPropAnalysis(BaseModel):
    """Player prop analysis."""
    prop_type: str
    line: float
    average: float
    over_rate: float
    under_rate: float
    last_5_avg: Optional[float] = None
    last_10_avg: Optional[float] = None
    home_avg: Optional[float] = None
    away_avg: Optional[float] = None
    

class PlayerPropsResponse(BaseModel):
    """Player props response."""
    player_id: str
    player_name: str
    team: str
    props: List[PlayerPropAnalysis]
    recent_games: List[PlayerGameLog]
    
    model_config = ConfigDict(from_attributes=True)
