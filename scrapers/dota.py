"""Dota 2 scraper using OpenDota API."""
import aiohttp
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from utils.logger import log


@dataclass
class DotaHero:
    """Dota hero data."""
    id: int
    name: str
    localized_name: str


@dataclass
class DotaTeam:
    """Dota team data."""
    team_id: int
    name: str
    tag: str = ""
    logo_url: str = ""


@dataclass
class DotaMatch:
    """Dota match data."""
    match_id: int
    radiant_team_id: Optional[int] = None
    dire_team_id: Optional[int] = None
    radiant_name: str = ""
    dire_name: str = ""
    league_id: Optional[int] = None
    league_name: str = ""
    series_id: Optional[int] = None
    series_type: Optional[int] = None  # 0=Bo1, 1=Bo3, 2=Bo5
    start_time: Optional[int] = None
    duration: Optional[int] = None
    radiant_win: Optional[bool] = None
    radiant_score: int = 0
    dire_score: int = 0
    radiant_picks: List[int] = field(default_factory=list)
    radiant_bans: List[int] = field(default_factory=list)
    dire_picks: List[int] = field(default_factory=list)
    dire_bans: List[int] = field(default_factory=list)
    players: List[Dict] = field(default_factory=list)
    status: str = "upcoming"  # upcoming, live, completed


class DotaUnified:
    """Unified Dota 2 data scraper using OpenDota API."""

    BASE_URL = "https://api.opendota.com/api"

    def __init__(self, api_key: str = None):
        """Initialize scraper.
        
        Args:
            api_key: Optional OpenDota API key for higher rate limits
        """
        self.api_key = api_key
        self._session: Optional[aiohttp.ClientSession] = None
        self._heroes_cache: Dict[int, DotaHero] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _fetch(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Fetch data from OpenDota API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            JSON response or None
        """
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}{endpoint}"

            if params is None:
                params = {}
            if self.api_key:
                params["api_key"] = self.api_key

            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    log.warning(f"OpenDota API error {resp.status}: {endpoint}")
                    return None
        except Exception as e:
            log.error(f"OpenDota API fetch error: {e}")
            return None

    async def get_pro_matches(self, limit: int = 100, fetch_history: bool = False) -> List[DotaMatch]:
        """Fetch professional Dota 2 matches.

        Args:
            limit: Number of matches to fetch per page
            fetch_history: If True, fetch historical matches until 2024

        Returns:
            List of matches
        """
        matches = []
        less_than_match_id = None
        max_pages = 200 if fetch_history else 1

        try:
            for page in range(max_pages):
                params = {}
                if less_than_match_id:
                    params["less_than_match_id"] = less_than_match_id

                data = await self._fetch("/proMatches", params)

                if not data or not isinstance(data, list):
                    break

                if not data:
                    log.info(f"Dota API: No more matches at page {page}")
                    break

                for match_data in data:
                    match = self._parse_match(match_data)
                    if match:
                        matches.append(match)

                # Check date of oldest match in this batch
                if fetch_history and data:
                    oldest_time = min(m.get("start_time", 0) for m in data if m.get("start_time"))
                    if oldest_time:
                        from datetime import datetime
                        oldest_date = datetime.utcfromtimestamp(oldest_time)
                        if oldest_date.year < 2024:
                            log.info(f"Dota API: Reached 2024, stopping at page {page}")
                            break

                    # Get last match_id for pagination
                    less_than_match_id = min(m.get("match_id", 0) for m in data if m.get("match_id"))
                    
                    if page % 10 == 0:
                        log.info(f"Dota API: Fetching page {page}, matches so far: {len(matches)}")
                else:
                    break  # Single page for normal updates

            # Log summary
            upcoming = sum(1 for m in matches if m.status == "upcoming")
            completed = sum(1 for m in matches if m.status == "completed")
            log.info(f"Dota API: {len(matches)} matches ({upcoming} upcoming, {completed} completed)")

        except Exception as e:
            log.error(f"Error fetching Dota matches: {e}")

        return matches

    async def get_match_details(self, match_id: int) -> Optional[DotaMatch]:
        """Get detailed match information.

        Args:
            match_id: Match ID

        Returns:
            Match details or None
        """
        try:
            data = await self._fetch(f"/matches/{match_id}")

            if not data:
                return None

            return self._parse_match_details(data)

        except Exception as e:
            log.error(f"Error fetching match details: {e}")
            return None

    async def get_team_stats(self, team_id: int) -> Optional[Dict]:
        """Get team statistics.

        Args:
            team_id: Team ID

        Returns:
            Team statistics dictionary
        """
        try:
            data = await self._fetch(f"/teams/{team_id}")

            if not data:
                return None

            return {
                "team_id": data.get("team_id"),
                "name": data.get("name", ""),
                "tag": data.get("tag", ""),
                "wins": data.get("wins", 0),
                "losses": data.get("losses", 0),
                "rating": data.get("rating", 0),
                "logo_url": data.get("logo_url", ""),
            }

        except Exception as e:
            log.error(f"Error fetching team stats: {e}")
            return None

    async def get_hero_by_id(self, hero_id: int) -> Optional[DotaHero]:
        """Get hero information by ID.

        Args:
            hero_id: Hero ID

        Returns:
            DotaHero or None
        """
        # Check cache first
        if hero_id in self._heroes_cache:
            return self._heroes_cache[hero_id]

        # Fetch all heroes and cache
        try:
            data = await self._fetch("/heroes")

            if not data or not isinstance(data, list):
                return None

            for hero_data in data:
                hero = DotaHero(
                    id=hero_data.get("id", 0),
                    name=hero_data.get("name", ""),
                    localized_name=hero_data.get("localized_name", ""),
                )
                self._heroes_cache[hero.id] = hero

            return self._heroes_cache.get(hero_id)

        except Exception as e:
            log.error(f"Error fetching heroes: {e}")
            return None

    async def get_live_matches(self) -> List[DotaMatch]:
        """Fetch currently live professional matches.

        Returns:
            List of live matches
        """
        try:
            data = await self._fetch("/live")

            if not data or not isinstance(data, list):
                return []

            matches = []
            for match_data in data:
                match = DotaMatch(
                    match_id=match_data.get("match_id", 0),
                    radiant_name=match_data.get("radiant_team", {}).get("team_name", "Radiant"),
                    dire_name=match_data.get("dire_team", {}).get("team_name", "Dire"),
                    radiant_team_id=match_data.get("radiant_team", {}).get("team_id"),
                    dire_team_id=match_data.get("dire_team", {}).get("team_id"),
                    league_id=match_data.get("league_id"),
                    radiant_score=match_data.get("radiant_score", 0),
                    dire_score=match_data.get("dire_score", 0),
                    status="live",
                )
                matches.append(match)

            log.info(f"Dota API: {len(matches)} live matches")
            return matches

        except Exception as e:
            log.error(f"Error fetching live matches: {e}")
            return []

    def _parse_match(self, data: Dict) -> Optional[DotaMatch]:
        """Parse match data from proMatches endpoint.

        Args:
            data: Match dictionary from API

        Returns:
            DotaMatch object or None
        """
        try:
            match_id = data.get("match_id")
            if not match_id:
                return None

            # Determine status
            duration = data.get("duration")
            if duration is not None:
                status = "completed"
            else:
                status = "upcoming"

            return DotaMatch(
                match_id=match_id,
                radiant_team_id=data.get("radiant_team_id"),
                dire_team_id=data.get("dire_team_id"),
                radiant_name=data.get("radiant_name", "Radiant"),
                dire_name=data.get("dire_name", "Dire"),
                league_id=data.get("leagueid"),
                league_name=data.get("league_name", ""),
                series_id=data.get("series_id"),
                series_type=data.get("series_type"),
                start_time=data.get("start_time"),
                duration=duration,
                radiant_win=data.get("radiant_win"),
                radiant_score=data.get("radiant_score", 0),
                dire_score=data.get("dire_score", 0),
                status=status,
            )

        except Exception as e:
            log.error(f"Error parsing match: {e}")
            return None

    def _parse_match_details(self, data: Dict) -> Optional[DotaMatch]:
        """Parse detailed match data.

        Args:
            data: Match details dictionary from API

        Returns:
            DotaMatch object or None
        """
        try:
            match_id = data.get("match_id")
            if not match_id:
                return None

            # Extract picks and bans
            picks_bans = data.get("picks_bans", [])
            radiant_picks = []
            radiant_bans = []
            dire_picks = []
            dire_bans = []

            for pb in picks_bans or []:
                hero_id = pb.get("hero_id")
                is_pick = pb.get("is_pick", False)
                team = pb.get("team")  # 0=radiant, 1=dire

                if team == 0:
                    if is_pick:
                        radiant_picks.append(hero_id)
                    else:
                        radiant_bans.append(hero_id)
                else:
                    if is_pick:
                        dire_picks.append(hero_id)
                    else:
                        dire_bans.append(hero_id)

            # Extract players
            players = []
            for player in data.get("players", []):
                players.append({
                    "account_id": player.get("account_id"),
                    "hero_id": player.get("hero_id"),
                    "kills": player.get("kills", 0),
                    "deaths": player.get("deaths", 0),
                    "assists": player.get("assists", 0),
                    "gold_per_min": player.get("gold_per_min", 0),
                    "xp_per_min": player.get("xp_per_min", 0),
                    "isRadiant": player.get("isRadiant", False),
                })

            return DotaMatch(
                match_id=match_id,
                radiant_team_id=data.get("radiant_team_id"),
                dire_team_id=data.get("dire_team_id"),
                radiant_name=data.get("radiant_name", "Radiant"),
                dire_name=data.get("dire_name", "Dire"),
                league_id=data.get("leagueid"),
                league_name=data.get("league", {}).get("name", "") if data.get("league") else "",
                series_id=data.get("series_id"),
                series_type=data.get("series_type"),
                start_time=data.get("start_time"),
                duration=data.get("duration"),
                radiant_win=data.get("radiant_win"),
                radiant_score=data.get("radiant_score", 0),
                dire_score=data.get("dire_score", 0),
                radiant_picks=radiant_picks,
                radiant_bans=radiant_bans,
                dire_picks=dire_picks,
                dire_bans=dire_bans,
                players=players,
                status="completed" if data.get("duration") else "upcoming",
            )

        except Exception as e:
            log.error(f"Error parsing match details: {e}")
            return None

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def __del__(self):
        """Cleanup on deletion."""
        if self._session and not self._session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except Exception:
                pass
