"""Base dataclasses for Superbet API integration."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class SuperbetOdds:
    """Represents odds for a specific outcome."""
    
    outcome_id: str
    outcome_name: str
    odds: float
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'outcome_id': self.outcome_id,
            'outcome_name': self.outcome_name,
            'odds': self.odds,
            'is_active': self.is_active,
        }


@dataclass
class SuperbetMarket:
    """Represents a betting market."""
    
    market_id: str
    market_name: str
    market_type: str
    odds_list: List[SuperbetOdds]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'market_id': self.market_id,
            'market_name': self.market_name,
            'market_type': self.market_type,
            'odds_list': [odd.to_dict() for odd in self.odds_list],
        }


@dataclass
class SuperbetEvent:
    """Represents a sporting event."""
    
    event_id: str
    event_name: str
    sport_id: int
    sport_name: str
    tournament_id: Optional[str]
    tournament_name: Optional[str]
    start_time: datetime
    team1: str
    team2: str
    markets: List[SuperbetMarket]
    is_live: bool = False
    status: str = "scheduled"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_id': self.event_id,
            'event_name': self.event_name,
            'sport_id': self.sport_id,
            'sport_name': self.sport_name,
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament_name,
            'start_time': self.start_time.isoformat(),
            'team1': self.team1,
            'team2': self.team2,
            'markets': [market.to_dict() for market in self.markets],
            'is_live': self.is_live,
            'status': self.status,
        }


@dataclass
class SuperbetTournament:
    """Represents a tournament/league."""
    
    tournament_id: str
    tournament_name: str
    sport_id: int
    sport_name: str
    region: Optional[str] = None
    tier: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament_name,
            'sport_id': self.sport_id,
            'sport_name': self.sport_name,
            'region': self.region,
            'tier': self.tier,
        }
