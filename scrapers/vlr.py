"""Scraper for Valorant data from VLR.gg API."""
import asyncio
from dataclasses import dataclass
from typing import List, Optional, Dict
import aiohttp
from utils.logger import log


@dataclass
class VLRMatch:
    """Valorant match from VLR.gg."""
    match_id: str
    team1: str
    team2: str
    team1_score: int = 0
    team2_score: int = 0
    status: str = "upcoming"  # upcoming, live, completed
    match_event: str = ""
    match_series: str = ""
    time_until_match: str = ""
    match_page: str = ""
    flag1: str = ""
    flag2: str = ""


@dataclass
class VLRTeam:
    """Valorant team from VLR.gg."""
    team_id: str
    name: str
    tag: str = ""
    logo: str = ""
    country: str = ""
    rank: int = 0
    region: str = ""
    record: str = ""  # W-L record
    wins: int = 0
    losses: int = 0
    earnings: int = 0  # in USD


class VLRUnified:
    """Unified VLR.gg API client for Valorant data."""
    
    BASE_URL = "https://vlrggapi.vercel.app"
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _fetch(self, endpoint: str) -> Optional[Dict]:
        """Fetch data from VLR API."""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}{endpoint}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    log.error(f"VLR API error: {response.status}")
                    return None
        except Exception as e:
            log.error(f"VLR fetch error: {e}")
            return None
    
    def _parse_earnings(self, earnings_str: str) -> int:
        """Parse earnings string like '$2,000,500' to int."""
        if not earnings_str:
            return 0
        try:
            # Remove $ and commas
            clean = earnings_str.replace('$', '').replace(',', '').strip()
            return int(float(clean))
        except:
            return 0
    
    def _parse_record(self, record_str: str) -> tuple:
        """Parse record string like '43–21' to (wins, losses)."""
        if not record_str:
            return 0, 0
        try:
            # Handle different dash types
            for sep in ['–', '-', '—']:
                if sep in record_str:
                    parts = record_str.split(sep)
                    return int(parts[0].strip()), int(parts[1].strip())
            return 0, 0
        except:
            return 0, 0
    
    async def get_upcoming_matches(self) -> List[VLRMatch]:
        """Get upcoming Valorant matches."""
        matches = []
        
        try:
            data = await self._fetch("/match?q=upcoming")
            
            if not data or "data" not in data:
                return matches
            
            segments = data.get("data", {}).get("segments", [])
            
            for item in segments:
                match = VLRMatch(
                    match_id=item.get("match_page", "").split("/")[-1] if item.get("match_page") else "",
                    team1=item.get("team1", "TBD"),
                    team2=item.get("team2", "TBD"),
                    status="upcoming",
                    match_event=item.get("match_event", ""),
                    match_series=item.get("match_series", ""),
                    time_until_match=item.get("time_until_match", ""),
                    match_page=item.get("match_page", ""),
                    flag1=item.get("flag1", ""),
                    flag2=item.get("flag2", ""),
                )
                matches.append(match)
            
            log.info(f"VLR API: {len(matches)} upcoming matches")
            
        except Exception as e:
            log.error(f"Error fetching VLR upcoming matches: {e}")
        
        return matches
    
    async def get_live_matches(self) -> List[VLRMatch]:
        """Get live Valorant matches."""
        matches = []
        
        try:
            data = await self._fetch("/match?q=live_score")
            
            if not data or "data" not in data:
                return matches
            
            segments = data.get("data", {}).get("segments", [])
            
            for item in segments:
                match = VLRMatch(
                    match_id=item.get("match_page", "").split("/")[-1] if item.get("match_page") else "",
                    team1=item.get("team1", "TBD"),
                    team2=item.get("team2", "TBD"),
                    team1_score=int(item.get("score1", 0) or 0),
                    team2_score=int(item.get("score2", 0) or 0),
                    status="live",
                    match_event=item.get("match_event", ""),
                    match_series=item.get("match_series", ""),
                    match_page=item.get("match_page", ""),
                    flag1=item.get("flag1", ""),
                    flag2=item.get("flag2", ""),
                )
                matches.append(match)
            
            log.info(f"VLR API: {len(matches)} live matches")
            
        except Exception as e:
            log.error(f"Error fetching VLR live matches: {e}")
        
        return matches
    
    async def get_results(self) -> List[VLRMatch]:
        """Get recent match results."""
        matches = []
        
        try:
            data = await self._fetch("/match?q=results")
            
            if not data or "data" not in data:
                return matches
            
            segments = data.get("data", {}).get("segments", [])
            
            for item in segments:
                match = VLRMatch(
                    match_id=item.get("match_page", "").split("/")[-1] if item.get("match_page") else "",
                    team1=item.get("team1", "TBD"),
                    team2=item.get("team2", "TBD"),
                    team1_score=int(item.get("score1", 0) or 0),
                    team2_score=int(item.get("score2", 0) or 0),
                    status="completed",
                    match_event=item.get("match_event", ""),
                    match_series=item.get("match_series", ""),
                    match_page=item.get("match_page", ""),
                    flag1=item.get("flag1", ""),
                    flag2=item.get("flag2", ""),
                )
                matches.append(match)
            
            log.info(f"VLR API: {len(matches)} results")
            
        except Exception as e:
            log.error(f"Error fetching VLR results: {e}")
        
        return matches
    
    async def get_all_matches(self) -> List[VLRMatch]:
        """Get all matches (upcoming, live, results)."""
        upcoming, live, results = await asyncio.gather(
            self.get_upcoming_matches(),
            self.get_live_matches(),
            self.get_results(),
        )
        
        all_matches = upcoming + live + results
        log.info(f"VLR API: {len(all_matches)} total matches ({len(upcoming)} upcoming, {len(live)} live, {len(results)} completed)")
        
        return all_matches
    
    async def get_rankings(self, region: str = "na") -> List[VLRTeam]:
        """Get team rankings for a region.
        
        Args:
            region: Region code (na, eu, ap, la, la-s, la-n, oce, kr, mn, gc, br, cn)
        """
        teams = []
        
        try:
            data = await self._fetch(f"/rankings?region={region}")
            
            if not data or "data" not in data:
                return teams
            
            for item in data.get("data", []):
                rank = int(item.get("rank", 0) or 0)
                wins, losses = self._parse_record(item.get("record", ""))
                earnings = self._parse_earnings(item.get("earnings", ""))
                
                team = VLRTeam(
                    team_id=item.get("team", "").lower().replace(" ", "-"),
                    name=item.get("team", ""),
                    logo=item.get("logo", ""),
                    country=item.get("country", ""),
                    rank=rank,
                    region=region,
                    record=item.get("record", ""),
                    wins=wins,
                    losses=losses,
                    earnings=earnings,
                )
                teams.append(team)
            
            log.info(f"VLR API: {len(teams)} teams in {region} rankings")
            
        except Exception as e:
            log.error(f"Error fetching VLR rankings: {e}")
        
        return teams
    
    async def get_all_rankings(self) -> List[VLRTeam]:
        """Get rankings from all major regions."""
        regions = ["na", "eu", "ap", "br", "kr", "cn", "la"]
        
        all_teams = []
        for region in regions:
            teams = await self.get_rankings(region)
            all_teams.extend(teams)
            await asyncio.sleep(0.5)  # Rate limit
        
        log.info(f"VLR API: {len(all_teams)} total teams from all regions")
        return all_teams
