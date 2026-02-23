"""CS2 (Counter-Strike 2) unified scraper using HLTV.org."""
import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from utils.logger import log


@dataclass
class CS2Team:
    """CS2 team data."""

    name: str
    ranking: Optional[int] = None
    country: Optional[str] = None
    logo: Optional[str] = None


@dataclass
class CS2MapResult:
    """Single map result within a match."""

    map_name: str
    team1_score: int
    team2_score: int
    winner: str


@dataclass
class CS2Match:
    """CS2 match data."""

    match_id: str
    team1: CS2Team
    team2: CS2Team
    team1_score: Optional[int] = None
    team2_score: Optional[int] = None
    winner: Optional[str] = None
    match_date: Optional[datetime] = None
    tournament: Optional[str] = None
    best_of: int = 1
    maps: List[str] = field(default_factory=list)
    status: str = "upcoming"  # upcoming, live, completed
    url: Optional[str] = None


class CS2Unified:
    """Unified CS2 data scraper using HLTV.org.

    Data sources:
    - HLTV.org match schedule and results
    - HLTV.org team rankings
    """

    BASE_URL = "https://www.hltv.org"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.hltv.org/",
    }

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.HEADERS)
        return self._session

    async def _fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML from a URL.

        Args:
            url: URL to fetch

        Returns:
            HTML text or None on failure
        """
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                log.warning(f"HLTV returned status {response.status} for {url}")
                return None
        except Exception as e:
            log.error(f"Error fetching {url}: {e}")
            return None

    async def get_upcoming_matches(self) -> List[CS2Match]:
        """Fetch upcoming CS2 matches from HLTV.

        Returns:
            List of upcoming CS2Match objects
        """
        matches: List[CS2Match] = []
        try:
            html = await self._fetch_html(f"{self.BASE_URL}/matches")
            if not html:
                return matches

            soup = BeautifulSoup(html, "html.parser")

            for match_div in soup.select(".upcomingMatch"):
                match = self._parse_upcoming_match(match_div)
                if match:
                    matches.append(match)

            log.info(f"Fetched {len(matches)} upcoming CS2 matches from HLTV")
        except Exception as e:
            log.error(f"Error fetching upcoming CS2 matches: {e}")

        return matches

    async def get_live_matches(self) -> List[CS2Match]:
        """Fetch live CS2 matches from HLTV.

        Returns:
            List of live CS2Match objects
        """
        matches: List[CS2Match] = []
        try:
            html = await self._fetch_html(f"{self.BASE_URL}/matches")
            if not html:
                return matches

            soup = BeautifulSoup(html, "html.parser")

            for match_div in soup.select(".liveMatch"):
                match = self._parse_upcoming_match(match_div, status="live")
                if match:
                    matches.append(match)

            log.info(f"Fetched {len(matches)} live CS2 matches from HLTV")
        except Exception as e:
            log.error(f"Error fetching live CS2 matches: {e}")

        return matches

    async def get_results(self, num_days: int = 7) -> List[CS2Match]:
        """Fetch recent CS2 match results from HLTV.

        Args:
            num_days: Number of past days to include (unused, returns current page)

        Returns:
            List of completed CS2Match objects
        """
        matches: List[CS2Match] = []
        try:
            html = await self._fetch_html(f"{self.BASE_URL}/results")
            if not html:
                return matches

            soup = BeautifulSoup(html, "html.parser")

            for result_div in soup.select(".result-con"):
                match = self._parse_result(result_div)
                if match:
                    matches.append(match)

            log.info(f"Fetched {len(matches)} CS2 results from HLTV")
        except Exception as e:
            log.error(f"Error fetching CS2 results: {e}")

        return matches

    async def get_team_ranking(self) -> List[CS2Team]:
        """Fetch HLTV team rankings.

        Returns:
            List of CS2Team objects ordered by ranking
        """
        teams: List[CS2Team] = []
        try:
            html = await self._fetch_html(f"{self.BASE_URL}/ranking/teams")
            if not html:
                return teams

            soup = BeautifulSoup(html, "html.parser")

            for rank_div in soup.select(".ranked-team"):
                team = self._parse_ranked_team(rank_div)
                if team:
                    teams.append(team)

            log.info(f"Fetched {len(teams)} teams from HLTV rankings")
        except Exception as e:
            log.error(f"Error fetching HLTV team rankings: {e}")

        return teams

    async def get_match_details(self, match_id: str) -> Optional[CS2Match]:
        """Get detailed match information including maps.

        Args:
            match_id: HLTV match ID

        Returns:
            CS2Match with detail, or None
        """
        try:
            url = f"{self.BASE_URL}/matches/{match_id}/_"
            html = await self._fetch_html(url)
            if not html:
                return None

            soup = BeautifulSoup(html, "html.parser")
            return self._parse_match_detail(soup, match_id, url)
        except Exception as e:
            log.error(f"Error fetching CS2 match details for {match_id}: {e}")
            return None

    async def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get team statistics by searching HLTV rankings.

        Args:
            team_name: Team name to look up

        Returns:
            Dictionary with team stats or None
        """
        try:
            teams = await self.get_team_ranking()
            name_lower = team_name.lower()
            for team in teams:
                if team.name.lower() == name_lower:
                    return {
                        "name": team.name,
                        "ranking": team.ranking,
                        "country": team.country,
                        "logo": team.logo,
                    }
            return None
        except Exception as e:
            log.error(f"Error fetching team stats for {team_name}: {e}")
            return None

    # ------------------------------------------------------------------
    # Private parsing helpers
    # ------------------------------------------------------------------

    def _parse_upcoming_match(
        self, div, status: str = "upcoming"
    ) -> Optional[CS2Match]:
        """Parse an upcoming/live match div into CS2Match."""
        try:
            link_tag = div.select_one("a.match")
            if not link_tag:
                link_tag = div.find("a")
            href = link_tag["href"] if link_tag and link_tag.get("href") else ""
            url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

            match_id = self._extract_match_id(href)

            team_names = [t.get_text(strip=True) for t in div.select(".matchTeamName")]
            if len(team_names) < 2:
                team_names = [t.get_text(strip=True) for t in div.select(".team")]
            team1_name = team_names[0] if len(team_names) > 0 else "TBD"
            team2_name = team_names[1] if len(team_names) > 1 else "TBD"

            tournament = ""
            event_tag = div.select_one(".matchEventName") or div.select_one(".event-name")
            if event_tag:
                tournament = event_tag.get_text(strip=True)

            best_of = 1
            meta_tag = div.select_one(".matchMeta") or div.select_one(".bestof")
            if meta_tag:
                text = meta_tag.get_text(strip=True)
                m = re.search(r"bo(\d)", text, re.IGNORECASE)
                if m:
                    best_of = int(m.group(1))

            match_date = None
            time_tag = div.select_one("[data-unix]")
            if time_tag:
                ts = time_tag.get("data-unix", "")
                if ts:
                    try:
                        match_date = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
                    except (ValueError, OverflowError):
                        pass

            return CS2Match(
                match_id=match_id,
                team1=CS2Team(name=team1_name),
                team2=CS2Team(name=team2_name),
                tournament=tournament,
                best_of=best_of,
                match_date=match_date,
                status=status,
                url=url,
            )
        except Exception as e:
            log.debug(f"Error parsing upcoming match div: {e}")
            return None

    def _parse_result(self, div) -> Optional[CS2Match]:
        """Parse a result div into a completed CS2Match."""
        try:
            link_tag = div.select_one("a")
            href = link_tag["href"] if link_tag and link_tag.get("href") else ""
            url = f"{self.BASE_URL}{href}" if href.startswith("/") else href
            match_id = self._extract_match_id(href)

            team_names = [t.get_text(strip=True) for t in div.select(".team")]
            team1_name = team_names[0] if len(team_names) > 0 else "TBD"
            team2_name = team_names[1] if len(team_names) > 1 else "TBD"

            scores = [s.get_text(strip=True) for s in div.select(".score")]
            team1_score: Optional[int] = None
            team2_score: Optional[int] = None
            if len(scores) >= 2:
                try:
                    team1_score = int(scores[0])
                    team2_score = int(scores[1])
                except ValueError:
                    pass

            winner: Optional[str] = None
            if team1_score is not None and team2_score is not None:
                if team1_score > team2_score:
                    winner = team1_name
                elif team2_score > team1_score:
                    winner = team2_name

            tournament = ""
            event_tag = div.select_one(".event-name") or div.select_one(".matchEventName")
            if event_tag:
                tournament = event_tag.get_text(strip=True)

            return CS2Match(
                match_id=match_id,
                team1=CS2Team(name=team1_name),
                team2=CS2Team(name=team2_name),
                team1_score=team1_score,
                team2_score=team2_score,
                winner=winner,
                tournament=tournament,
                status="completed",
                url=url,
            )
        except Exception as e:
            log.debug(f"Error parsing result div: {e}")
            return None

    def _parse_ranked_team(self, div) -> Optional[CS2Team]:
        """Parse a ranked-team div into CS2Team."""
        try:
            name_tag = div.select_one(".name") or div.select_one(".teamLine .name")
            name = name_tag.get_text(strip=True) if name_tag else ""
            if not name:
                return None

            ranking: Optional[int] = None
            rank_tag = div.select_one(".position")
            if rank_tag:
                try:
                    ranking = int(rank_tag.get_text(strip=True).lstrip("#"))
                except ValueError:
                    pass

            country: Optional[str] = None
            country_tag = div.select_one(".country-name") or div.select_one(".flag")
            if country_tag:
                country = country_tag.get("title") or country_tag.get_text(strip=True)

            logo: Optional[str] = None
            img_tag = div.select_one("img.team-logo") or div.select_one("img")
            if img_tag:
                logo = img_tag.get("src", "")

            return CS2Team(name=name, ranking=ranking, country=country, logo=logo)
        except Exception as e:
            log.debug(f"Error parsing ranked team div: {e}")
            return None

    def _parse_match_detail(
        self, soup: BeautifulSoup, match_id: str, url: str
    ) -> Optional[CS2Match]:
        """Parse a match detail page into CS2Match."""
        try:
            team_divs = soup.select(".teamName")
            team1_name = team_divs[0].get_text(strip=True) if len(team_divs) > 0 else "TBD"
            team2_name = team_divs[1].get_text(strip=True) if len(team_divs) > 1 else "TBD"

            score_divs = soup.select(".won, .lost, .tie")
            scores = [s.get_text(strip=True) for s in score_divs[:2]]
            team1_score: Optional[int] = None
            team2_score: Optional[int] = None
            if len(scores) >= 2:
                try:
                    team1_score = int(scores[0])
                    team2_score = int(scores[1])
                except ValueError:
                    pass

            winner: Optional[str] = None
            if team1_score is not None and team2_score is not None:
                if team1_score > team2_score:
                    winner = team1_name
                elif team2_score > team1_score:
                    winner = team2_name

            tournament = ""
            event_tag = soup.select_one(".timeAndEvent .event")
            if event_tag:
                tournament = event_tag.get_text(strip=True)

            maps: List[str] = []
            for map_div in soup.select(".mapname"):
                map_name = map_div.get_text(strip=True)
                if map_name and map_name.lower() != "default":
                    maps.append(map_name)

            best_of = max(len(maps), 1)

            match_date: Optional[datetime] = None
            time_tag = soup.select_one("[data-unix]")
            if time_tag:
                ts = time_tag.get("data-unix", "")
                if ts:
                    try:
                        match_date = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
                    except (ValueError, OverflowError):
                        pass

            status = "completed" if (team1_score is not None) else "upcoming"

            return CS2Match(
                match_id=match_id,
                team1=CS2Team(name=team1_name),
                team2=CS2Team(name=team2_name),
                team1_score=team1_score,
                team2_score=team2_score,
                winner=winner,
                match_date=match_date,
                tournament=tournament,
                best_of=best_of,
                maps=maps,
                status=status,
                url=url,
            )
        except Exception as e:
            log.debug(f"Error parsing match detail page: {e}")
            return None

    @staticmethod
    def _extract_match_id(href: str) -> str:
        """Extract numeric match ID from an HLTV href.

        Examples:
            /matches/2370295/team-a-vs-team-b  -> '2370295'
            /results  -> ''
        """
        m = re.search(r"/matches/(\d+)", href)
        return m.group(1) if m else href

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

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
