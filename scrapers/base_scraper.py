"""Base scraper class for bookmaker integrations."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class BookmakerType(Enum):
    """Type of bookmaker."""
    TRADITIONAL = "traditional"
    CRYPTO = "crypto"


class IntegrationType(Enum):
    """Type of integration."""
    SCRAPER = "scraper"
    API = "api"


@dataclass
class OddsData:
    """Standardized odds data structure."""
    event_id: str
    event_name: str
    sport: str
    league: str
    team_home: str
    team_away: str
    odds_home: float
    odds_draw: Optional[float]
    odds_away: float
    bookmaker: str
    timestamp: str
    extra_markets: Optional[Dict] = None


class BaseScraper(ABC):
    """Abstract base class for all bookmaker scrapers/integrations.
    
    Each bookmaker should inherit from this class and implement
    the required methods.
    """
    
    def __init__(self):
        self.name: str = ""
        self.enabled: bool = False
        self.bookmaker_type: BookmakerType = BookmakerType.TRADITIONAL
        self.integration_type: IntegrationType = IntegrationType.SCRAPER
        self.base_url: str = ""
        self.requires_auth: bool = False
    
    @abstractmethod
    async def get_esports_odds(self, game: str = None) -> List[OddsData]:
        """Fetch odds for esports matches.
        
        Args:
            game: Optional game filter (e.g., 'cs2', 'lol', 'dota2', 'valorant')
            
        Returns:
            List of OddsData objects
        """
        pass
    
    @abstractmethod
    async def get_live_events(self) -> List[Dict]:
        """Fetch live events.
        
        Returns:
            List of live event dictionaries
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the scraper/API is functioning.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    def _raise_not_implemented(self, method_name: str, reason: str = "awaiting configuration"):
        """Helper method for disabled scrapers to raise consistent NotImplementedError.
        
        Args:
            method_name: Name of the method being called
            reason: Reason for being disabled (e.g., "awaiting configuration", "needs API verification")
        
        Raises:
            NotImplementedError: Always raised with a formatted message
        """
        raise NotImplementedError(
            f"{self.name} scraper is disabled. "
            f"Awaiting {reason} and implementation of {self.integration_type.value} logic."
        )
    
    def __repr__(self) -> str:
        return f"{self.name}(enabled={self.enabled}, type={self.integration_type.value})"
