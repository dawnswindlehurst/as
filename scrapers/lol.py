"""League of Legends scraper using LoL Esports API."""
import aiohttp
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from utils.logger import log


@dataclass
class LoLTeam:
    """LoL team data."""
    name: str
    code: str
    league: str = ""
    region: str = ""
    logo: str = ""


@dataclass
class LoLGameResult:
    """Single game result within a match."""
    game_number: int
    winner: str = ""
    duration: str = ""
    blue_team: str = ""
    red_team: str = ""
    blue_picks: List[str] = field(default_factory=list)
    red_picks: List[str] = field(default_factory=list)
    blue_bans: List[str] = field(default_factory=list)
    red_bans: List[str] = field(default_factory=list)


@dataclass
class LoLMatch:
    """LoL match data."""
    match_id: str
    team1: LoLTeam
    team2: LoLTeam
    league: str = ""
    tournament: str = ""
    date: str = ""
    status: str = "upcoming"  # upcoming, live, completed
    best_of: int = 1
    url: str = ""
    score1: int = 0
    score2: int = 0
    winner: str = ""
    games: List[LoLGameResult] = field(default_factory=list)


class LoLUnified:
    """Unified LoL data scraper.

    Data sources:
    - LoL Esports API (esports-api.lolesports.com)
    - Fallback to other sources if needed
    """

    # LoL Esports API endpoints
    BASE_URL = "https://esports-api.lolesports.com/persisted/gw"
    LIVE_URL = "https://feed.lolesports.com/livestats/v1"

    # API key (public, used by official site)
    API_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"

    def __init__(self):
        self.headers = {
            "x-api-key": self.API_KEY,
            "Accept": "application/json",
        }
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def _fetch(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Fetch data from API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            JSON response or None
        """
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}{endpoint}"

            default_params = {"hl": "en-US"}
            if params:
                default_params.update(params)

            async with session.get(url, params=default_params) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    log.warning(f"LoL API error {resp.status}: {endpoint}")
                    return None
        except Exception as e:
            log.error(f"LoL API fetch error: {e}")
            return None

    async def get_upcoming_matches(self) -> List[LoLMatch]:
        """Fetch upcoming LoL matches (all states for updates).

        Returns:
            List of matches
        """
        matches = []

        try:
            data = await self._fetch("/getSchedule")

            if not data or "data" not in data:
                return matches

            schedule = data.get("data", {}).get("schedule", {})
            events = schedule.get("events", [])

            for event in events:
                # Pegar todos os estados para poder atualizar
                if event.get("state") in ["unstarted", "inProgress", "completed"]:
                    match = self._parse_event(event)
                    if match:
                        matches.append(match)

            # Log com breakdown
            upcoming = sum(1 for m in matches if m.status == "upcoming")
            tbd = sum(1 for m in matches if m.status == "tbd")
            live = sum(1 for m in matches if m.status == "live")
            completed = sum(1 for m in matches if m.status == "completed")

            log.info(f"LoL API: {len(matches)} matches ({upcoming} upcoming, {tbd} TBD, {live} live, {completed} completed)")

        except Exception as e:
            log.error(f"Error fetching LoL matches: {e}")

        return matches

    async def get_match_details(self, match_id: str) -> Optional[LoLMatch]:
        """Get detailed match information.

        Args:
            match_id: Match ID

        Returns:
            Match details or None
        """
        try:
            data = await self._fetch("/getEventDetails", {"id": match_id})

            if not data or "data" not in data:
                return None

            event = data.get("data", {}).get("event", {})
            match = self._parse_event(event)

            if match and event.get("match", {}).get("games"):
                match.games = self._parse_games(event["match"]["games"])

            return match

        except Exception as e:
            log.error(f"Error fetching match details: {e}")
            return None

    async def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get team statistics.

        Args:
            team_name: Team name or code

        Returns:
            Team statistics dictionary
        """
        try:
            data = await self._fetch("/getTeams")

            if not data or "data" not in data:
                return None

            teams = data.get("data", {}).get("teams", [])

            team_name_lower = team_name.lower()
            for team in teams:
                if (team.get("name", "").lower() == team_name_lower or
                        team.get("code", "").lower() == team_name_lower):
                    return {
                        "name": team.get("name", ""),
                        "code": team.get("code", ""),
                        "region": team.get("homeLeague", {}).get("region", ""),
                        "league": team.get("homeLeague", {}).get("name", ""),
                        "logo": team.get("image", ""),
                        "players": team.get("players", []),
                    }

            return None

        except Exception as e:
            log.error(f"Error fetching team stats: {e}")
            return None

    async def get_draft_analysis(self, match_id: str) -> Optional[Dict]:
        """Get draft/pick-ban analysis for a match.

        Args:
            match_id: Match ID

        Returns:
            Draft analysis with picks and bans
        """
        try:
            match = await self.get_match_details(match_id)

            if not match or not match.games:
                return None

            analysis = {
                "match_id": match_id,
                "games": []
            }

            for game in match.games:
                game_draft = {
                    "game_number": game.game_number,
                    "blue_team": game.blue_team,
                    "red_team": game.red_team,
                    "blue_picks": game.blue_picks,
                    "red_picks": game.red_picks,
                    "blue_bans": game.blue_bans,
                    "red_bans": game.red_bans,
                }
                analysis["games"].append(game_draft)

            return analysis

        except Exception as e:
            log.error(f"Error fetching draft analysis: {e}")
            return None

    def _parse_event(self, event: Dict) -> Optional[LoLMatch]:
        """Parse event data into LoLMatch.

        Args:
            event: Event dictionary from API

        Returns:
            LoLMatch object or None
        """
        try:
            if not event or not isinstance(event, dict):
                return None

            match_data = event.get("match")
            if not match_data or not isinstance(match_data, dict):
                log.debug(f"Skipping event without match data: {event.get('id', 'unknown')}")
                return None

            teams = match_data.get("teams") or []

            if len(teams) < 2:
                return None

            team1 = self._parse_team(teams[0])
            team2 = self._parse_team(teams[1])

            # Determinar status baseado no estado E nos times
            state = event.get("state", "")

            # Verificar se algum time é TBD
            has_tbd = team1.name == "TBD" or team2.name == "TBD"

            if state == "completed":
                status = "completed"
            elif state == "inProgress":
                status = "live"
            elif has_tbd:
                status = "tbd"  # Times não definidos ainda
            else:
                status = "upcoming"  # Pronto para apostas!

            strategy = match_data.get("strategy") or {}
            best_of = strategy.get("count", 1) if isinstance(strategy, dict) else 1

            result1 = (teams[0] or {}).get("result") or {}
            result2 = (teams[1] or {}).get("result") or {}
            score1 = result1.get("gameWins", 0) if isinstance(result1, dict) else 0
            score2 = result2.get("gameWins", 0) if isinstance(result2, dict) else 0

            winner = ""
            if status == "completed":
                if score1 > score2:
                    winner = team1.name
                elif score2 > score1:
                    winner = team2.name

            league_data = event.get("league") or {}
            tournament_data = event.get("tournament") or {}

            return LoLMatch(
                match_id=str(match_data.get("id", "")),
                team1=team1,
                team2=team2,
                league=league_data.get("name", "") if isinstance(league_data, dict) else "",
                tournament=tournament_data.get("name", "") if isinstance(tournament_data, dict) else "",
                date=event.get("startTime", ""),
                status=status,
                best_of=best_of,
                url=f"https://lolesports.com/match/{event.get('id', '')}",
                score1=score1,
                score2=score2,
                winner=winner,
            )

        except Exception as e:
            log.error(f"Error parsing event {event.get('id', 'unknown') if isinstance(event, dict) else 'invalid'}: {e}")
            return None

    def _parse_team(self, team_data: Dict) -> LoLTeam:
        """Parse team data into LoLTeam.

        Args:
            team_data: Team dictionary from API

        Returns:
            LoLTeam object
        """
        if team_data is None or not isinstance(team_data, dict):
            return LoLTeam(name="TBD", code="TBD")

        name = team_data.get("name")
        code = team_data.get("code")

        if not name or name.strip() == "":
            return LoLTeam(name="TBD", code="TBD")

        # homeLeague só existe em chamadas de getTeams, não em getSchedule
        home_league = team_data.get("homeLeague")
        if home_league is None or not isinstance(home_league, dict):
            home_league = {}

        return LoLTeam(
            name=name,
            code=code or "TBD",
            league=home_league.get("name", ""),
            region=home_league.get("region", ""),
            logo=team_data.get("image", ""),
        )

    def _parse_games(self, games_data: List[Dict]) -> List[LoLGameResult]:
        """Parse games data into LoLGameResult list.

        Args:
            games_data: List of game dictionaries

        Returns:
            List of LoLGameResult objects
        """
        if not games_data or not isinstance(games_data, list):
            return []

        games = []

        for i, game in enumerate(games_data, 1):
            if not game or not isinstance(game, dict):
                continue

            teams = game.get("teams") or []

            blue_team = ""
            red_team = ""

            if len(teams) > 0 and teams[0] and isinstance(teams[0], dict):
                blue_team = teams[0].get("name", "")
            if len(teams) > 1 and teams[1] and isinstance(teams[1], dict):
                red_team = teams[1].get("name", "")

            winner = ""
            if game.get("state") == "completed":
                for team in teams:
                    if team and isinstance(team, dict):
                        result = team.get("result")
                        if result and isinstance(result, dict) and result.get("outcome") == "win":
                            winner = team.get("name", "")
                            break

            game_result = LoLGameResult(
                game_number=game.get("number", i),
                winner=winner,
                duration=str(game.get("duration", "")),
                blue_team=blue_team,
                red_team=red_team,
                blue_picks=[],
                red_picks=[],
                blue_bans=[],
                red_bans=[],
            )
            games.append(game_result)

        return games

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
