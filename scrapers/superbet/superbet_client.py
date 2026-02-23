"""Async REST client for Superbet API."""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import aiohttp

from .base import SuperbetEvent, SuperbetOdds, SuperbetMarket, SuperbetTournament
from .tournament_cache import TournamentCache
from .scorealarm_models import ScorealarmSport, ScorealarmTournament


logger = logging.getLogger(__name__)


class SuperbetClient:
    """Async client for Superbet API."""
    
    BASE_URL = "https://production-superbet-offer-br.freetls.fastly.net/v2/pt-BR"
    
    
    # Tournament ID to name mapping (known tournaments)
    TOURNAMENT_NAMES = {
        164: 'NBA',
        36: 'NCAA',
        2175: 'NCAA (F)',
        84290: 'Unrivaled (F)',
        19114: 'EuroLeague',
        2383: 'EuroCup',
        6632: 'Liga Argentina',
        27691: 'Liga Argentina 2',
        27560: 'Turkey League',
    }

    SPORT_IDS = {
        'cs2': 55,          # Counter-Strike 2
        'dota2': 54,        # Dota 2
        'valorant': 153,    # Valorant
        'lol': 39,          # League of Legends
        'tennis': 4,        # Tênis
        'football': 5,      # Futebol
    }
    
    def __init__(self, timeout: int = 30, cache_ttl: int = 3600):
        """
        Initialize Superbet client.
        
        Args:
            timeout: Request timeout in seconds
            cache_ttl: Cache TTL in seconds (default: 1 hour)
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.cache = TournamentCache(default_ttl=cache_ttl)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make GET request to API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Build URL manually to avoid encoding + as %2B
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"
        
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching {url}: {e}")
            raise

    @staticmethod
    def _to_int(value: Any) -> Optional[int]:
        """Convert API numeric identifiers to int when possible."""
        if value is None:
            return None

        if isinstance(value, int):
            return value

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    
    async def get_sports(self) -> List[ScorealarmSport]:
        """
        Get list of available sports from struct endpoint.
        
        Returns:
            List of ScorealarmSport objects
            
        Example:
            GET /struct -> .data.sports[]: {id, localNames["pt-BR"]}
        """
        data = await self._get("struct")
        sports = []
        
        for sport_data in data.get('data', {}).get('sports', []):
            sport_id = self._to_int(sport_data.get('id'))
            if sport_id is None:
                logger.warning(f"Skipping sport with invalid id payload: {sport_data.get('id')!r}")
                continue

            local_names = sport_data.get('localNames', {})
            sport_name = local_names.get('pt-BR', sport_data.get('name', f'Sport {sport_id}'))
            
            sport = ScorealarmSport(
                id=sport_id,
                name=sport_data.get('name', sport_name),
                local_name=sport_name
            )
            sports.append(sport)
        
        return sports
    
    async def get_tournaments_by_sport(self, sport_id: int) -> List[ScorealarmTournament]:
        """
        Get list of tournaments for a specific sport.
        
        Args:
            sport_id: Sport ID
            
        Returns:
            List of ScorealarmTournament objects
            
        Example:
            GET /sport/{sport_id}/tournaments -> .data[]: {sportId, categoryId, competitions[]: {tournamentId, localNames}}
        """
        cache_key = f"tournaments_sport_{sport_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        data = await self._get(f"sport/{sport_id}/tournaments")
        tournaments = []
        
        for category_data in data.get('data', []):
            category_id = self._to_int(category_data.get('categoryId'))
            category_name = category_data.get('categoryName', '')
            
            for comp_data in category_data.get('competitions', []):
                tournament_id = self._to_int(comp_data.get('tournamentId'))
                if tournament_id is None:
                    logger.warning(f"Skipping tournament with invalid id payload: {comp_data.get('tournamentId')!r}")
                    continue

                local_names = comp_data.get('localNames', {})
                tournament_name = local_names.get('pt-BR', comp_data.get('name', f'Tournament {tournament_id}'))
                
                tournament = ScorealarmTournament(
                    tournament_id=tournament_id,
                    tournament_name=tournament_name,
                    sport_id=sport_id,
                    category_id=category_id or 0,
                    category_name=category_name
                )
                tournaments.append(tournament)
        
        self.cache.set(cache_key, tournaments)
        return tournaments
    
    async def get_tournaments(self, sport_id: Optional[int] = None) -> List[SuperbetTournament]:
        """
        Get list of tournaments (legacy method for backward compatibility).
        
        Args:
            sport_id: Filter by sport ID (optional)
            
        Returns:
            List of SuperbetTournament objects
            
        Note:
            This method is kept for backward compatibility with existing code.
            For new code, use get_tournaments_by_sport() for the new API format.
        """
        cache_key = f"tournaments_{sport_id or 'all'}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        data = await self._get("tournaments")
        tournaments = []
        
        for item in data.get('tournaments', []):
            if sport_id is None or item.get('sportId') == sport_id:
                tournament = SuperbetTournament(
                    tournament_id=str(item.get('id')),
                    tournament_name=item.get('name', ''),
                    sport_id=item.get('sportId'),
                    sport_name=item.get('sportName', ''),
                    region=item.get('region'),
                    tier=item.get('tier'),
                )
                tournaments.append(tournament)
        
        self.cache.set(cache_key, tournaments)
        return tournaments
    
    async def get_event_full_odds(self, event_id: int) -> Optional[SuperbetEvent]:
        """
        Fetch ALL odds for a specific event.
        
        Args:
            event_id: Event ID
            
        Returns:
            SuperbetEvent object with all markets/odds or None
        """
        try:
            data = await self._get(f"events/{event_id}")
            events = self._parse_events(data)
            return events[0] if events else None
        except Exception as e:
            logger.error(f"Error fetching full odds for event {event_id}: {e}")
            return None
    
    async def get_events_by_sport(
        self,
        sport_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        full_odds: bool = False
    ) -> List[SuperbetEvent]:
        """
        Get events for a specific sport.
        
        Args:
            sport_id: Sport ID
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            full_odds: If True, fetches complete details for each event (default: False)
            
        Returns:
            List of SuperbetEvent objects
        """
        from datetime import datetime, timedelta, timezone
        
        now = datetime.now(timezone.utc)
        if not start_date:
            start_date = now
        if not end_date:
            end_date = now + timedelta(days=1)
        
        # Formato correto: YYYY-MM-DD+HH:MM:SS (API espera + em vez de espaço)
        if isinstance(start_date, date) and not isinstance(start_date, datetime):
            start_str = f"{start_date.isoformat()}+00:00:00"
        else:
            start_str = start_date.strftime("%Y-%m-%d+%H:%M:%S")
            
        if isinstance(end_date, date) and not isinstance(end_date, datetime):
            end_str = f"{end_date.isoformat()}+23:59:59"
        else:
            end_str = end_date.strftime("%Y-%m-%d+%H:%M:%S")
        
        params = {
            'sportId': sport_id,
            'currentStatus': 'active',
            'offerState': 'prematch',
            'startDate': start_str,
            'endDate': end_str,
        }

        try:
            data = await self._get("events/by-date", params=params)
        except aiohttp.ClientResponseError as exc:
            # Some environments return HTTP 400 for time-based windows,
            # but accept date-only boundaries. Retry once with full-day window.
            if exc.status != 400:
                raise

            fallback_params = {
                'sportId': sport_id,
                'currentStatus': 'active',
                'offerState': 'prematch',
                'startDate': f"{start_date.date().isoformat() if hasattr(start_date, 'date') else start_date.isoformat()}+00:00:00",
                'endDate': f"{end_date.date().isoformat() if hasattr(end_date, 'date') else end_date.isoformat()}+23:59:59",
            }
            logger.warning(
                "events/by-date returned 400 for startDate=%s endDate=%s; retrying with fallback window %s -> %s",
                params['startDate'],
                params['endDate'],
                fallback_params['startDate'],
                fallback_params['endDate'],
            )
            data = await self._get("events/by-date", params=fallback_params)

        events = self._parse_events(data)
        
        # Fetch complete details if requested (using concurrent requests)
        if full_odds and events:
            # Use asyncio.gather for concurrent API calls
            detailed_tasks = [self.get_event_full_odds(int(event.event_id)) for event in events]
            detailed_results = await asyncio.gather(*detailed_tasks, return_exceptions=True)
            
            detailed_events = []
            for i, detailed in enumerate(detailed_results):
                if isinstance(detailed, Exception):
                    logger.warning(f"Error fetching full odds for event {events[i].event_id}: {detailed}")
                    # Use original event if details fetch fails
                    detailed_events.append(events[i])
                elif detailed:
                    detailed_events.append(detailed)
                else:
                    # Use original event if no details returned
                    detailed_events.append(events[i])
            return detailed_events
        
        return events
    
    async def get_event_details(self, event_id: str) -> Optional[SuperbetEvent]:
        """
        Get detailed information for a specific event.
        
        Args:
            event_id: Event ID
            
        Returns:
            SuperbetEvent object or None
        """
        try:
            data = await self._get(f"events/{event_id}")
            events = self._parse_events({'events': [data]})
            return events[0] if events else None
        except Exception as e:
            logger.error(f"Error fetching event {event_id}: {e}")
            return None
    
    async def get_live_events(self, sport_id: Optional[int] = None) -> List[SuperbetEvent]:
        """
        Get currently live events.
        
        Args:
            sport_id: Filter by sport ID (optional)
            
        Returns:
            List of live SuperbetEvent objects
        """
        params = {}
        if sport_id:
            params['sportIds'] = sport_id
        
        try:
            data = await self._get("events/live", params=params)
            return self._parse_events(data, is_live=True)
        except Exception as e:
            logger.error(f"Error fetching live events: {e}")
            return []
    
    def _parse_events(self, data: Dict[str, Any], is_live: bool = False) -> List[SuperbetEvent]:
        """
        Parse events from API response.
        
        Args:
            data: API response data
            is_live: Whether events are live
            
        Returns:
            List of SuperbetEvent objects
        """
        events = []
        
        for item in (data.get('data', []) or data.get('events', [])):
            try:
                # Parse teams - novo formato usa matchName com separador
                match_name = item.get('matchName', '')
                if match_name and chr(183) in match_name:  # · separador
                    parts = match_name.split(chr(183))
                    team1 = parts[0].strip() if len(parts) > 0 else 'Team 1'
                    team2 = parts[1].strip() if len(parts) > 1 else 'Team 2'
                else:
                    participants = item.get('participants', [])
                    team1 = participants[0].get('name', 'Team 1') if len(participants) > 0 else 'Team 1'
                    team2 = participants[1].get('name', 'Team 2') if len(participants) > 1 else 'Team 2'
                
                # Parse markets/odds - novo formato
                markets = []
                raw_odds = item.get('odds') or []
                markets_dict = {}
                for odd_data in raw_odds:
                    market_uuid = odd_data.get('marketUuid', 'default')
                    if market_uuid not in markets_dict:
                        markets_dict[market_uuid] = {
                            'id': str(odd_data.get('marketId', '')),
                            'name': odd_data.get('marketName', ''),
                            'odds': []
                        }
                    odd = SuperbetOdds(
                        outcome_id=str(odd_data.get('outcomeId', '')),
                        outcome_name=odd_data.get('name', ''),
                        odds=float(odd_data.get('price', 1.0)),
                        is_active=odd_data.get('status') == 'active',
                    )
                    markets_dict[market_uuid]['odds'].append(odd)
                for md in markets_dict.values():
                    market = SuperbetMarket(
                        market_id=md['id'],
                        market_name=md['name'],
                        market_type='',
                        odds_list=md['odds'],
                    )
                    markets.append(market)
                
                # Parse event
                event = SuperbetEvent(
                    event_id=str(item.get('eventId') or item.get('id') or ''),
                    event_name=item.get('name', ''),
                    sport_id=item.get('sportId'),
                    sport_name=item.get('sportName', ''),
                    tournament_id=str(item.get('tournamentId')) if item.get('tournamentId') else None,
                    tournament_name=item.get('tournamentName') or self.TOURNAMENT_NAMES.get(item.get('tournamentId'), ''),
                    start_time=datetime.fromisoformat(item.get('utcDate', item.get('startTime', '')).replace('Z', '+00:00')),
                    team1=team1,
                    team2=team2,
                    markets=markets,
                    is_live=is_live or item.get('isLive', False),
                    status=item.get('status', 'scheduled'),
                )
                events.append(event)
            except Exception as e:
                logger.warning(f"Error parsing event: {e}")
                continue
        
        return events
