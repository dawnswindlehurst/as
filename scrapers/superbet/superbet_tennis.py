"""Superbet integration for Tennis (ATP, WTA, Grand Slams)."""

import asyncio
import logging
from typing import List, Optional, Dict
from datetime import date, timedelta

from .superbet_client import SuperbetClient
from .base import SuperbetEvent


logger = logging.getLogger(__name__)


class SuperbetTennis:
    """Superbet Tennis data fetcher."""
    
    def __init__(self, client: Optional[SuperbetClient] = None):
        """
        Initialize Tennis fetcher.
        
        Args:
            client: SuperbetClient instance (creates new if None)
        """
        self.client = client
        self._owned_client = client is None
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self._owned_client:
            self.client = SuperbetClient()
            await self.client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._owned_client and self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def get_tennis_matches(
        self,
        days_ahead: int = 7,
        include_live: bool = True
    ) -> List[SuperbetEvent]:
        """
        Get tennis matches.
        
        Args:
            days_ahead: Number of days to look ahead
            include_live: Include live matches
            
        Returns:
            List of SuperbetEvent objects
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        sport_id = SuperbetClient.SPORT_IDS['tennis']
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Fetch scheduled matches
        scheduled = await self.client.get_events_by_sport(
            sport_id=sport_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Fetch live matches if requested
        live = []
        if include_live:
            live = await self.client.get_live_events(sport_id=sport_id)
        
        # Combine and deduplicate
        all_matches = live + scheduled
        seen_ids = set()
        unique_matches = []
        
        for match in all_matches:
            if match.event_id not in seen_ids:
                seen_ids.add(match.event_id)
                unique_matches.append(match)
        
        return unique_matches
    
    async def get_atp_matches(self, days_ahead: int = 7) -> List[SuperbetEvent]:
        """
        Get ATP (men's) tennis matches.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of SuperbetEvent objects filtered for ATP
        """
        all_matches = await self.get_tennis_matches(days_ahead)
        
        # Filter for ATP tournaments (basic filter by tournament name)
        atp_keywords = ['ATP', 'Masters', 'Grand Slam', 'Davis Cup']
        atp_matches = [
            match for match in all_matches
            if match.tournament_name and any(
                keyword in match.tournament_name for keyword in atp_keywords
            )
        ]
        
        return atp_matches
    
    async def get_wta_matches(self, days_ahead: int = 7) -> List[SuperbetEvent]:
        """
        Get WTA (women's) tennis matches.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of SuperbetEvent objects filtered for WTA
        """
        all_matches = await self.get_tennis_matches(days_ahead)
        
        # Filter for WTA tournaments
        wta_keywords = ['WTA', 'Fed Cup', 'Billie Jean King Cup']
        wta_matches = [
            match for match in all_matches
            if match.tournament_name and any(
                keyword in match.tournament_name for keyword in wta_keywords
            )
        ]
        
        return wta_matches


# Convenience function for standalone usage
async def fetch_tennis_odds(days_ahead: int = 7, category: str = 'all') -> List[SuperbetEvent]:
    """
    Fetch tennis odds.
    
    Args:
        days_ahead: Number of days to look ahead
        category: 'all', 'atp', or 'wta'
        
    Returns:
        List of SuperbetEvent objects
    """
    async with SuperbetTennis() as tennis:
        if category == 'atp':
            return await tennis.get_atp_matches(days_ahead)
        elif category == 'wta':
            return await tennis.get_wta_matches(days_ahead)
        else:
            return await tennis.get_tennis_matches(days_ahead)
