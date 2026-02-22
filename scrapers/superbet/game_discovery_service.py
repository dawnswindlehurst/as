"""Service for discovering games across multiple sports using Superbet and Scorealarm APIs."""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from .superbet_client import SuperbetClient
from .scorealarm_client import ScorealarmClient
from .scorealarm_models import (
    ScorealarmMatch,
    ScorealarmSport,
    ScorealarmTournament,
)


logger = logging.getLogger(__name__)


# Map of sports considered "gold" - less analyzed, high value opportunities
VALUABLE_SPORTS = {
    7: "Bandy",
    9: "Floorball",
    15: "Polo aquático",
    22: "Curling",
    29: "Hóquei sobre a grama",
    71: "Rink Hockey",
    81: "Lacrosse",
}


# Complete sport mapping from Superbet
SUPERBET_SPORTS = {
    1: "Vôlei",
    2: "Tênis",
    3: "Hóquei no Gelo",
    4: "Basquete",
    5: "Futebol",
    6: "Sinuca",
    7: "Bandy",
    8: "Rúgbi",
    9: "Floorball",
    10: "Esportes de inverno",
    11: "Handebol",
    12: "Futebol Americano",
    13: "Dardos",
    14: "Badminton",
    15: "Polo aquático",
    16: "Golfe",
    17: "Futsal",
    19: "Futebol australiano",
    20: "Beisebol",
    22: "Curling",
    24: "Tênis de Mesa",
    25: "Ciclismo",
    28: "Vôlei de praia",
    29: "Hóquei sobre a grama",
    32: "Críquete",
    34: "Boxe",
    38: "Squash",
    39: "League of Legends",
    40: "MMA",
    42: "Super Especiais",
    46: "Esqui alpino",
    48: "Biatlo",
    50: "Cross-Country",
    54: "Dota 2",
    55: "Counter-Strike 2",
    59: "Patinação de velocidade",
    61: "Call of Duty",
    70: "E-Sport Basquete",
    71: "Rink Hockey",
    74: "Basquete 3x3",
    75: "E-Sport Futebol",
    80: "Rainbow Six",
    81: "Lacrosse",
    85: "Arena of Valor",
    88: "Honor of Kings",
    91: "Fórmula",
    93: "Esportes Motorizados",
    94: "Speedway",
    153: "Valorant",
    157: "E-Sport Hóquei no Gelo",
    166: "Padel",
    189: "E-Sport Tênis",
    190: "Futebol Virtual",
}


class GameDiscoveryService:
    """Service to discover games across multiple sports using Superbet and Scorealarm APIs."""
    
    def __init__(self, timeout: int = 30, cache_ttl: int = 3600):
        """
        Initialize the game discovery service.
        
        Args:
            timeout: Request timeout in seconds
            cache_ttl: Cache TTL in seconds for SuperbetClient
        """
        self.timeout = timeout
        self.cache_ttl = cache_ttl
    
    async def discover_games_by_sport(
        self,
        sport_id: int,
        limit: Optional[int] = None
    ) -> List[ScorealarmMatch]:
        """
        Discover games for a specific sport.
        
        This method:
        1. Gets tournaments for the sport from Superbet
        2. For each tournament, gets competition/season details from Scorealarm
        3. Fetches matches for each competition
        
        Args:
            sport_id: Sport ID
            limit: Maximum number of tournaments to process (optional)
            
        Returns:
            List of ScorealarmMatch objects
        """
        all_matches = []
        
        async with SuperbetClient(timeout=self.timeout, cache_ttl=self.cache_ttl) as superbet:
            async with ScorealarmClient(timeout=self.timeout) as scorealarm:
                try:
                    # Get tournaments for sport
                    logger.info(f"Fetching tournaments for sport {sport_id}")
                    tournaments = await superbet.get_tournaments_by_sport(sport_id)
                    
                    if limit:
                        tournaments = tournaments[:limit]
                    
                    logger.info(f"Found {len(tournaments)} tournaments for sport {sport_id}")
                    
                    # Process each tournament
                    for tournament in tournaments:
                        try:
                            # Get tournament details from Scorealarm
                            logger.debug(f"Processing tournament {tournament.tournament_id}: {tournament.tournament_name}")
                            tournament_details = await scorealarm.get_tournament_details(tournament.tournament_id)
                            
                            if not tournament_details:
                                logger.debug(f"No details found for tournament {tournament.tournament_id}")
                                continue
                            
                            # Get latest season
                            season = tournament_details.get_latest_season()
                            if not season:
                                logger.debug(f"No season found for tournament {tournament.tournament_id}")
                                continue
                            
                            # Get matches for this competition/season
                            logger.debug(f"Fetching matches for competition {tournament_details.competition_id}, season {season.id}")
                            matches = await scorealarm.get_competition_events(
                                season_id=season.id,
                                competition_id=tournament_details.competition_id
                            )
                            
                            all_matches.extend(matches)
                            logger.debug(f"Found {len(matches)} matches for tournament {tournament.tournament_name}")
                            
                        except Exception as e:
                            logger.warning(f"Error processing tournament {tournament.tournament_id}: {e}")
                            continue
                    
                    logger.info(f"Total matches found for sport {sport_id}: {len(all_matches)}")
                    
                except Exception as e:
                    logger.error(f"Error discovering games for sport {sport_id}: {e}")
        
        return all_matches
    
    async def discover_all_games(
        self,
        sport_ids: Optional[List[int]] = None,
        limit_per_sport: Optional[int] = None
    ) -> Dict[str, List[ScorealarmMatch]]:
        """
        Discover games across all (or specified) sports.
        
        Args:
            sport_ids: List of sport IDs to process (if None, uses all valuable sports)
            limit_per_sport: Maximum number of tournaments per sport to process
            
        Returns:
            Dictionary mapping sport name to list of matches
        """
        if sport_ids is None:
            sport_ids = list(VALUABLE_SPORTS.keys())
        
        results = {}
        
        # Process sports concurrently
        tasks = []
        for sport_id in sport_ids:
            sport_name = SUPERBET_SPORTS.get(sport_id, f"Sport {sport_id}")
            tasks.append(self._discover_sport(sport_id, sport_name, limit_per_sport))
        
        # Wait for all tasks to complete
        sport_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for i, result in enumerate(sport_results):
            sport_id = sport_ids[i]
            sport_name = SUPERBET_SPORTS.get(sport_id, f"Sport {sport_id}")
            
            if isinstance(result, Exception):
                logger.error(f"Error discovering games for {sport_name}: {result}")
                results[sport_name] = []
            else:
                results[sport_name] = result
        
        return results
    
    async def _discover_sport(
        self,
        sport_id: int,
        sport_name: str,
        limit: Optional[int]
    ) -> List[ScorealarmMatch]:
        """
        Helper method to discover games for a single sport.
        
        Args:
            sport_id: Sport ID
            sport_name: Sport name
            limit: Tournament limit
            
        Returns:
            List of matches
        """
        logger.info(f"Discovering games for {sport_name} (ID: {sport_id})")
        matches = await self.discover_games_by_sport(sport_id, limit=limit)
        logger.info(f"Found {len(matches)} matches for {sport_name}")
        return matches
    
    def get_valuable_sports(self) -> List[Dict[str, Any]]:
        """
        Get list of "valuable" sports (less analyzed, high opportunity).
        
        Returns:
            List of sport dictionaries with id and name
        """
        return [
            {'id': sport_id, 'name': name}
            for sport_id, name in VALUABLE_SPORTS.items()
        ]
    
    def get_all_sports(self) -> List[Dict[str, Any]]:
        """
        Get list of all supported sports.
        
        Returns:
            List of sport dictionaries with id and name
        """
        return [
            {'id': sport_id, 'name': name}
            for sport_id, name in SUPERBET_SPORTS.items()
        ]
