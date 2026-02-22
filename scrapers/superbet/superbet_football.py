"""Superbet integration for Football (Brasileirão, Champions League, etc)."""

import asyncio
import logging
from typing import List, Optional, Dict
from datetime import date, timedelta

from .superbet_client import SuperbetClient
from .base import SuperbetEvent


logger = logging.getLogger(__name__)


class SuperbetFootball:
    """Superbet Football data fetcher."""
    
    def __init__(self, client: Optional[SuperbetClient] = None):
        """
        Initialize Football fetcher.
        
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
    
    async def get_football_matches(
        self,
        days_ahead: int = 7,
        include_live: bool = True
    ) -> List[SuperbetEvent]:
        """
        Get football matches.
        
        Args:
            days_ahead: Number of days to look ahead
            include_live: Include live matches
            
        Returns:
            List of SuperbetEvent objects
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        sport_id = SuperbetClient.SPORT_IDS['football']
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
    
    async def get_brasileirao_matches(self, days_ahead: int = 7) -> List[SuperbetEvent]:
        """
        Get Brasileirão (Brazilian Championship) matches.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of SuperbetEvent objects filtered for Brasileirão
        """
        all_matches = await self.get_football_matches(days_ahead)
        
        # Filter for Brasileirão
        brasileirao_keywords = ['Brasileirão', 'Brazilian', 'Brasil', 'Serie A']
        brasileirao_matches = [
            match for match in all_matches
            if match.tournament_name and any(
                keyword in match.tournament_name for keyword in brasileirao_keywords
            )
        ]
        
        return brasileirao_matches
    
    async def get_champions_league_matches(self, days_ahead: int = 7) -> List[SuperbetEvent]:
        """
        Get UEFA Champions League matches.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of SuperbetEvent objects filtered for Champions League
        """
        all_matches = await self.get_football_matches(days_ahead)
        
        # Filter for Champions League
        ucl_keywords = ['Champions League', 'UCL', 'UEFA Champions']
        ucl_matches = [
            match for match in all_matches
            if match.tournament_name and any(
                keyword in match.tournament_name for keyword in ucl_keywords
            )
        ]
        
        return ucl_matches
    
    async def get_copa_matches(self, days_ahead: int = 7) -> List[SuperbetEvent]:
        """
        Get Copa do Brasil and Copa Libertadores matches.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of SuperbetEvent objects filtered for Copas
        """
        all_matches = await self.get_football_matches(days_ahead)
        
        # Filter for Copa tournaments
        copa_keywords = ['Copa do Brasil', 'Copa Libertadores', 'Copa Sul-Americana']
        copa_matches = [
            match for match in all_matches
            if match.tournament_name and any(
                keyword in match.tournament_name for keyword in copa_keywords
            )
        ]
        
        return copa_matches


# Convenience function for standalone usage
async def fetch_football_odds(days_ahead: int = 7, league: str = 'all') -> List[SuperbetEvent]:
    """
    Fetch football odds.
    
    Args:
        days_ahead: Number of days to look ahead
        league: 'all', 'brasileirao', 'champions', or 'copa'
        
    Returns:
        List of SuperbetEvent objects
    """
    async with SuperbetFootball() as football:
        if league == 'brasileirao':
            return await football.get_brasileirao_matches(days_ahead)
        elif league == 'champions':
            return await football.get_champions_league_matches(days_ahead)
        elif league == 'copa':
            return await football.get_copa_matches(days_ahead)
        else:
            return await football.get_football_matches(days_ahead)
