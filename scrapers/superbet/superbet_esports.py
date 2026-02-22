"""Superbet integration for eSports (CS2, Dota 2, Valorant, LoL)."""

import asyncio
import logging
from typing import List, Optional, Dict
from datetime import date, datetime, timedelta

from .superbet_client import SuperbetClient
from .base import SuperbetEvent


logger = logging.getLogger(__name__)


class SuperbetEsports:
    """Superbet eSports data fetcher."""
    
    def __init__(self, client: Optional[SuperbetClient] = None):
        """
        Initialize eSports fetcher.
        
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
    
    async def get_cs2_matches(
        self,
        days_ahead: int = 7,
        include_live: bool = True,
        full_odds: bool = True
    ) -> List[SuperbetEvent]:
        """
        Get CS2 (Counter-Strike 2) matches.
        
        Args:
            days_ahead: Number of days to look ahead
            include_live: Include live matches
            full_odds: Fetch complete details for each event (default: True)
            
        Returns:
            List of SuperbetEvent objects
        """
        sport_id = SuperbetClient.SPORT_IDS['cs2']
        return await self._get_matches_by_sport(sport_id, days_ahead, include_live, full_odds)
    
    async def get_dota2_matches(
        self,
        days_ahead: int = 7,
        include_live: bool = True,
        full_odds: bool = True
    ) -> List[SuperbetEvent]:
        """
        Get Dota 2 matches.
        
        Args:
            days_ahead: Number of days to look ahead
            include_live: Include live matches
            full_odds: Fetch complete details for each event (default: True)
            
        Returns:
            List of SuperbetEvent objects
        """
        sport_id = SuperbetClient.SPORT_IDS['dota2']
        return await self._get_matches_by_sport(sport_id, days_ahead, include_live, full_odds)
    
    async def get_valorant_matches(
        self,
        days_ahead: int = 7,
        include_live: bool = True,
        full_odds: bool = True
    ) -> List[SuperbetEvent]:
        """
        Get Valorant matches.
        
        Args:
            days_ahead: Number of days to look ahead
            include_live: Include live matches
            full_odds: Fetch complete details for each event (default: True)
            
        Returns:
            List of SuperbetEvent objects
        """
        sport_id = SuperbetClient.SPORT_IDS['valorant']
        return await self._get_matches_by_sport(sport_id, days_ahead, include_live, full_odds)
    
    async def get_lol_matches(
        self,
        days_ahead: int = 7,
        include_live: bool = True,
        full_odds: bool = True
    ) -> List[SuperbetEvent]:
        """
        Get League of Legends matches.
        
        Args:
            days_ahead: Number of days to look ahead
            include_live: Include live matches
            full_odds: Fetch complete details for each event (default: True)
            
        Returns:
            List of SuperbetEvent objects
        """
        sport_id = SuperbetClient.SPORT_IDS['lol']
        return await self._get_matches_by_sport(sport_id, days_ahead, include_live, full_odds)
    
    async def get_all_esports_matches(
        self,
        days_ahead: int = 7,
        include_live: bool = True,
        full_odds: bool = True
    ) -> Dict[str, List[SuperbetEvent]]:
        """
        Get matches for all eSports.
        
        Args:
            days_ahead: Number of days to look ahead
            include_live: Include live matches
            full_odds: Fetch complete details for each event (default: True)
            
        Returns:
            Dictionary mapping game name to list of events
        """
        tasks = {
            'cs2': self.get_cs2_matches(days_ahead, include_live, full_odds),
            'dota2': self.get_dota2_matches(days_ahead, include_live, full_odds),
            'valorant': self.get_valorant_matches(days_ahead, include_live, full_odds),
            'lol': self.get_lol_matches(days_ahead, include_live, full_odds),
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        matches = {}
        for game, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {game} matches: {result}")
                matches[game] = []
            else:
                matches[game] = result
        
        return matches
    
    async def _get_matches_by_sport(
        self,
        sport_id: int,
        days_ahead: int,
        include_live: bool,
        full_odds: bool = True
    ) -> List[SuperbetEvent]:
        """
        Get matches for a specific sport.
        
        Args:
            sport_id: Sport ID
            days_ahead: Number of days to look ahead
            include_live: Include live matches
            full_odds: Fetch complete details for each event (default: True)
            
        Returns:
            List of SuperbetEvent objects
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Fetch scheduled matches
        scheduled = await self.client.get_events_by_sport(
            sport_id=sport_id,
            start_date=start_date,
            end_date=end_date,
            full_odds=full_odds
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


# Convenience function for standalone usage
async def fetch_esports_odds(game: str, days_ahead: int = 7) -> List[SuperbetEvent]:
    """
    Fetch eSports odds for a specific game.
    
    Args:
        game: Game name ('cs2', 'dota2', 'valorant', 'lol')
        days_ahead: Number of days to look ahead
        
    Returns:
        List of SuperbetEvent objects
    """
    async with SuperbetEsports() as esports:
        if game == 'cs2':
            return await esports.get_cs2_matches(days_ahead)
        elif game == 'dota2':
            return await esports.get_dota2_matches(days_ahead)
        elif game == 'valorant':
            return await esports.get_valorant_matches(days_ahead)
        elif game == 'lol':
            return await esports.get_lol_matches(days_ahead)
        else:
            raise ValueError(f"Unknown game: {game}")
