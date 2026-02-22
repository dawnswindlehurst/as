"""Async REST client for Scorealarm Stats API."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import aiohttp

from .scorealarm_models import (
    ScorealarmMatch,
    ScorealarmMatchDetail,
    ScorealarmTournamentDetails,
    ScorealarmTeam,
    ScorealarmScore,
    ScorealarmSeason,
    ScorealarmCompetition,
    ScorealarmCategory,
    MatchStat,
    LiveEvent,
    FixtureStats,
    PlayerSeasonStats,
    PlayerStats,
    TeamFormStats,
    TeamStanding,
    TeamStats,
)


logger = logging.getLogger(__name__)


class ScorealarmClient:
    """Async client for Scorealarm Stats API."""
    
    BASE_URL = "https://scorealarm-stats.freetls.fastly.net"
    PLATFORM = "brsuperbetsport"
    LOCALE = "pt-BR"

    SPORT_PATH_ALIASES = {
        "futebol": "soccer",
        "football": "soccer",
        "soccer": "soccer",
        "basquete": "basketball",
        "basketball": "basketball",
        "tenis": "tennis",
        "tênis": "tennis",
        "tennis": "tennis",
        "volei": "volleyball",
        "vôlei": "volleyball",
        "volleyball": "volleyball",
        "handebol": "handball",
        "handball": "handball",
        "hoquei no gelo": "ice-hockey",
        "hóquei no gelo": "ice-hockey",
        "ice hockey": "ice-hockey",
        "beisebol": "baseball",
        "baseball": "baseball",
        "rugbi": "rugby",
        "rúgbi": "rugby",
        "rugby": "rugby",
        "futsal": "futsal",
        "tenis de mesa": "table-tennis",
        "tênis de mesa": "table-tennis",
        "table tennis": "table-tennis",
        "dardos": "darts",
        "darts": "darts",
        "sinuca": "snooker",
        "snooker": "snooker",
        "polo aquatico": "water-polo",
        "polo aquático": "water-polo",
        "water polo": "water-polo",
        "floorball": "floorball",
        "curling": "curling",
        "hoquei sobre a grama": "field-hockey",
        "hóquei sobre a grama": "field-hockey",
        "field hockey": "field-hockey",
        "futebol australiano": "aussie-rules",
        "aussie rules": "aussie-rules",
        "bandy": "bandy",
    }
    
    def __init__(self, timeout: int = 30):
        """
        Initialize Scorealarm client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _resolve_sport_path(self, sport_hint: Optional[str]) -> Optional[str]:
        """Resolve a user/sport name hint to a known v2 sport path."""
        if not sport_hint:
            return None
        normalized = sport_hint.strip().lower()
        return self.SPORT_PATH_ALIASES.get(normalized, normalized if normalized in self.SPORT_PATH_ALIASES.values() else None)

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make GET request to API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            aiohttp.ClientError: On HTTP errors
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()

                # Some endpoints legitimately return 204 (no content)
                if response.status == 204:
                    return {}

                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type.lower():
                    text_body = await response.text()
                    if not text_body.strip():
                        return {}
                    logger.warning(f"Unexpected content type for {url}: {content_type}")
                    return {}

                return await response.json()
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                logger.debug(f"404 fetching {url}")
            else:
                logger.error(f"Error fetching {url}: {e}")
            raise
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching {url}: {e}")
            raise
    
    async def get_tournament_details(self, tournament_id: int) -> Optional[ScorealarmTournamentDetails]:
        """
        Get tournament details including competition and season IDs.
        
        Args:
            tournament_id: Tournament ID from Superbet
            
        Returns:
            ScorealarmTournamentDetails object or None if not found
            
        Example:
            GET /competition/details/tournaments/brsuperbetsport/pt-BR?tournament_id=ax:tournament:{id}
        """
        try:
            params = {'tournament_id': f'ax:tournament:{tournament_id}'}
            data = await self._get(
                f"competition/details/tournaments/{self.PLATFORM}/{self.LOCALE}",
                params=params
            )
            
            if not data or 'competition' not in data:
                logger.warning(f"No competition data found for tournament {tournament_id}")
                return None
            
            competition_data = data.get('competition', {})
            seasons_data = data.get('seasons', [])
            
            # Parse seasons
            seasons = []
            for season_data in seasons_data:
                season = ScorealarmSeason(
                    id=season_data.get('id', 0),
                    name=season_data.get('name', '')
                )
                seasons.append(season)
            
            tournament_details = ScorealarmTournamentDetails(
                tournament_id=tournament_id,
                tournament_name=competition_data.get('name', ''),
                competition_id=competition_data.get('id', 0),
                competition_name=competition_data.get('name', ''),
                seasons=seasons
            )
            
            return tournament_details
            
        except Exception as e:
            logger.error(f"Error fetching tournament details for {tournament_id}: {e}")
            return None
    
    async def get_competition_events(
        self,
        season_id: int,
        competition_id: int
    ) -> List[ScorealarmMatch]:
        """
        Get matches/events for a competition season.
        
        Args:
            season_id: Season ID
            competition_id: Competition ID
            
        Returns:
            List of ScorealarmMatch objects
            
        Example:
            GET /competition/events/brsuperbetsport/pt-BR?season_id=br:season:{id}&competition_id=br:competition:{id}
        """
        try:
            params = {
                'season_id': f'br:season:{season_id}',
                'competition_id': f'br:competition:{competition_id}'
            }
            
            data = await self._get(
                f"competition/events/{self.PLATFORM}/{self.LOCALE}",
                params=params
            )
            
            raw_matches = data.get('matches', []) if isinstance(data, dict) else []
            if not isinstance(raw_matches, list):
                logger.warning(
                    f"Unexpected matches payload for competition {competition_id}, season {season_id}"
                )
                return []

            matches = []
            for match_data in raw_matches:
                match = self._parse_match(match_data)
                if match:
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error fetching events for competition {competition_id}, season {season_id}: {e}")
            return []
    
    async def get_event_detail(self, match_id: int) -> Optional[ScorealarmMatchDetail]:
        """
        Get detailed match information including H2H and form.
        
        Args:
            match_id: Match ID
            
        Returns:
            ScorealarmMatchDetail object or None
            
        Example:
            GET /event/detail/brsuperbetsport/pt-BR?id=br:match:{id}
        """
        try:
            params = {'id': f'br:match:{match_id}'}
            
            data = await self._get(
                f"event/detail/{self.PLATFORM}/{self.LOCALE}",
                params=params
            )
            
            # Parse main match data
            match_data = data.get('match', {})
            match = self._parse_match(match_data)
            
            if not match:
                return None
            
            # Parse additional details
            match_detail = ScorealarmMatchDetail(
                match=match,
                h2h_stats=data.get('h2h', {}),
                team1_form=data.get('team1_form', []),
                team2_form=data.get('team2_form', []),
                additional_stats=data.get('stats', {})
            )
            
            return match_detail
            
        except Exception as e:
            logger.error(f"Error fetching event detail for match {match_id}: {e}")
            return None
    
    def _parse_match(self, match_data: Dict[str, Any]) -> Optional[ScorealarmMatch]:
        """
        Parse match data from API response.
        
        Args:
            match_data: Raw match data from API
            
        Returns:
            ScorealarmMatch object or None if parsing fails
        """
        try:
            if not isinstance(match_data, dict) or not match_data:
                return None

            # Parse teams
            team1_data = match_data.get('team1', {})
            team2_data = match_data.get('team2', {})

            if not isinstance(team1_data, dict):
                team1_data = {}
            if not isinstance(team2_data, dict):
                team2_data = {}
            
            team1 = ScorealarmTeam(
                id=team1_data.get('id', 0),
                name=team1_data.get('name', 'Team 1')
            )
            team2 = ScorealarmTeam(
                id=team2_data.get('id', 0),
                name=team2_data.get('name', 'Team 2')
            )
            
            # Parse scores
            scores = []
            for score_data in match_data.get('scores', []):
                if not isinstance(score_data, dict):
                    continue
                score = ScorealarmScore(
                    team1=score_data.get('team1', 0),
                    team2=score_data.get('team2', 0),
                    type=score_data.get('type', 0)
                )
                scores.append(score)
            
            # Parse season
            season_data = match_data.get('season', {})
            if not isinstance(season_data, dict):
                season_data = {}
            season = ScorealarmSeason(
                id=season_data.get('id', 0),
                name=season_data.get('name', '')
            )
            
            # Parse competition
            competition_data = match_data.get('competition', {})
            if not isinstance(competition_data, dict):
                competition_data = {}
            competition = ScorealarmCompetition(
                id=competition_data.get('id', 0),
                name=competition_data.get('name', '')
            )
            
            # Parse category
            category_data = match_data.get('category', {})
            if not isinstance(category_data, dict):
                category_data = {}
            category = ScorealarmCategory(
                id=category_data.get('id', 0),
                name=category_data.get('name', ''),
                sport_id=category_data.get('sport_id', 0)
            )
            
            # Parse match date
            match_date_data = match_data.get('match_date', {})
            if isinstance(match_date_data, dict):
                seconds = match_date_data.get('seconds', 0)
                if seconds:
                    match_date = datetime.fromtimestamp(seconds)
                else:
                    # Use epoch as sentinel for missing data
                    match_date = datetime.fromtimestamp(0)
            else:
                # Use epoch as sentinel for missing data
                match_date = datetime.fromtimestamp(0)
            
            # Parse offer_id
            offer_id_data = match_data.get('offer_id', {})
            offer_id = None
            if isinstance(offer_id_data, dict):
                offer_id = offer_id_data.get('value')
            elif isinstance(offer_id_data, str):
                offer_id = offer_id_data
            
            match = ScorealarmMatch(
                id=match_data.get('id', 0),
                platform_id=match_data.get('platform_id', ''),
                offer_id=offer_id,
                match_date=match_date,
                match_status=match_data.get('match_status', 0),
                match_state=match_data.get('match_state', 0),
                sport_id=match_data.get('sport_id', 0),
                team1=team1,
                team2=team2,
                scores=scores,
                season=season,
                competition=competition,
                category=category
            )
            
            return match
            
        except Exception as e:
            logger.warning(f"Error parsing match data: {e}")
            return None
    
    async def get_fixture_stats(self, fixture_id: str, sport_hint: Optional[str] = None) -> Optional[FixtureStats]:
        """
        Get detailed match statistics including xG, shots, goals by player.
        
        Args:
            fixture_id: Match ID (e.g., "12001839" or full "ax:match:12001839")
            sport_hint: Optional sport name/path hint to prioritize endpoint selection
            
        Returns:
            FixtureStats with match_stats, live_events, statistics
        """
        try:
            # Ensure fixture_id has proper prefix
            if not fixture_id.startswith('ax:match:'):
                fixture_id = f'ax:match:{fixture_id}'

            params = {'fixture-id': fixture_id}

            # Try multiple sport endpoints; when a sport hint is available,
            # try it first to avoid noisy cross-sport 404 probes.
            default_paths = [
                'soccer',
                'tennis',
            ]
            preferred_path = self._resolve_sport_path(sport_hint)
            sport_paths = [preferred_path] + default_paths if preferred_path else default_paths

            # Deduplicate while preserving order
            seen = set()
            sport_paths = [p for p in sport_paths if p and not (p in seen or seen.add(p))]

            data = None
            selected_path = None
            for sport_path in sport_paths:
                endpoint = f"v2/{sport_path}/fixtures/overview/{self.PLATFORM}/{self.LOCALE}"
                try:
                    candidate = await self._get(endpoint, params=params)
                except Exception:
                    continue

                if candidate and (
                    candidate.get('match_stats')
                    or candidate.get('live_events')
                    or candidate.get('statistics_by_period')
                    or candidate.get('statistics')
                    or candidate.get('point_by_point')
                ):
                    data = candidate
                    selected_path = sport_path
                    break

            if not data:
                # Tennis can expose rich stats in event/detail even when v2 overview is unavailable.
                try:
                    detail = await self._get(
                        f"event/detail/{self.PLATFORM}/{self.LOCALE}",
                        params={"id": fixture_id},
                    )
                except Exception:
                    detail = None

                if detail and (detail.get('statistics') or detail.get('point_by_point') or detail.get('live_events')):
                    data = detail
                    selected_path = 'event/detail'
                else:
                    logger.warning(f"No fixture data found for {fixture_id} across v2 sport endpoints")
                    return None

            logger.debug(f"Fixture {fixture_id} resolved via v2/{selected_path}/fixtures/overview")

            # Parse match_stats
            match_stats = []
            for stat_data in data.get('match_stats', []):
                stat_name = ''
                if 'text' in stat_data and 'args' in stat_data['text']:
                    stat_name = stat_data['text']['args'][0] if stat_data['text']['args'] else ''
                
                stat = MatchStat(
                    type=stat_data.get('type', 0),
                    team1=stat_data.get('team1', '0'),
                    team2=stat_data.get('team2', '0'),
                    stat_name=stat_name
                )
                match_stats.append(stat)
            
            # Parse live_events
            live_events = []
            for event_data in data.get('live_events', []):
                minute_data = event_data.get('minute', {})
                minute = minute_data.get('value', 0) if isinstance(minute_data, dict) else 0
                added_time = minute_data.get('added_time') if isinstance(minute_data, dict) else None
                
                # Parse primary player (scorer, card receiver, etc.)
                primary_data = event_data.get('primary', {})
                player_id = None
                player_name = None
                if primary_data:
                    player_id_data = primary_data.get('player_id', {})
                    if isinstance(player_id_data, dict):
                        player_id = player_id_data.get('value')
                    
                    text_data = primary_data.get('text', {})
                    if isinstance(text_data, dict):
                        player_name = text_data.get('val')
                
                # Parse secondary player (assist, etc.)
                secondary_data = event_data.get('secondary', {})
                secondary_player_id = None
                secondary_player_name = None
                if secondary_data:
                    sec_player_id_data = secondary_data.get('player_id', {})
                    if isinstance(sec_player_id_data, dict):
                        secondary_player_id = sec_player_id_data.get('value')
                    
                    sec_text_data = secondary_data.get('text', {})
                    if isinstance(sec_text_data, dict) and 'args' in sec_text_data:
                        # Second arg is player name for assists
                        if len(sec_text_data['args']) > 1:
                            secondary_player_name = sec_text_data['args'][1]
                
                # Parse score
                score = None
                main_data = event_data.get('main', {})
                if main_data and 'text' in main_data:
                    text_data = main_data['text']
                    if isinstance(text_data, dict) and 'args' in text_data:
                        score = text_data['args'][0] if text_data['args'] else None
                
                event = LiveEvent(
                    type=event_data.get('type', 0),
                    subtype=event_data.get('subtype', 0),
                    side=event_data.get('side', 0),
                    minute=minute,
                    added_time=added_time,
                    player_id=player_id,
                    player_name=player_name,
                    secondary_player_id=secondary_player_id,
                    secondary_player_name=secondary_player_name,
                    score=score
                )
                live_events.append(event)
            
            # Parse statistics by period
            statistics_by_period = {}
            for period_data in data.get('statistics', []):
                period = period_data.get('period', 0)
                period_stats = []
                
                for stat_data in period_data.get('stats', period_data.get('data', [])):
                    stat_name = ''
                    if 'text' in stat_data and 'args' in stat_data['text']:
                        stat_name = stat_data['text']['args'][0] if stat_data['text']['args'] else ''
                    
                    stat = MatchStat(
                        type=stat_data.get('type', 0),
                        team1=stat_data.get('team1', '0'),
                        team2=stat_data.get('team2', '0'),
                        stat_name=stat_name
                    )
                    period_stats.append(stat)
                
                statistics_by_period[period] = period_stats
            
            if not match_stats and statistics_by_period.get(0):
                match_stats = list(statistics_by_period[0])

            fixture_stats = FixtureStats(
                fixture_id=fixture_id,
                match_stats=match_stats,
                live_events=live_events,
                statistics_by_period=statistics_by_period
            )
            
            return fixture_stats
            
        except Exception as e:
            logger.error(f"Error fetching fixture stats for {fixture_id}: {e}")
            return None
    
    async def get_player_stats(self, player_id: str) -> Optional[PlayerStats]:
        """
        Get player statistics by competition including goals, assists, rating.
        
        Args:
            player_id: Player ID string (e.g., "524Lwb9169FQbvfEIUGjrl")
            
        Returns:
            PlayerStats with player info, seasonal_form, recent matches
            
        Example:
            GET /v2/soccer/players/overview/brsuperbetsport/pt-BR?player-id=524Lwb9169FQbvfEIUGjrl
        """
        try:
            params = {'player-id': player_id}
            data = await self._get(
                f"v2/soccer/players/overview/{self.PLATFORM}/{self.LOCALE}",
                params=params
            )
            
            if not data:
                logger.warning(f"No player data found for {player_id}")
                return None
            
            # Parse player info
            player_data = data.get('player', {})
            player_name = player_data.get('name', '')
            position = player_data.get('position')
            
            # Parse current team
            team_id = None
            team_name = None
            team_infos = data.get('team_infos', [])
            if team_infos:
                # Get first/current team
                current_team = team_infos[0]
                team_id = current_team.get('team_id')
                team_name = current_team.get('team_name')
            
            # Parse seasonal_form
            seasonal_form = []
            for season_data in data.get('seasonal_form', []):
                competition_id = season_data.get('competition_id', '')
                competition_name = ''
                season_name = ''
                
                # Parse season info
                season_info = season_data.get('season', {})
                if isinstance(season_info, dict):
                    season_name = season_info.get('name', '')
                
                # Parse stats
                matches_played = 0
                goals = 0
                assists = 0
                
                for stat in season_data.get('stats', []):
                    stat_type = stat.get('type', 0)
                    value_data = stat.get('value', {})
                    
                    # Extract numeric value from args
                    value = 0
                    if isinstance(value_data, dict) and 'args' in value_data:
                        try:
                            value = int(value_data['args'][0]) if value_data['args'] else 0
                        except (ValueError, IndexError):
                            value = 0
                    
                    if stat_type == 14:  # Matches Played
                        matches_played = value
                    elif stat_type == 1:  # Goals
                        goals = value
                    elif stat_type == 2:  # Assists
                        assists = value
                
                # Parse rating and rank
                rating = None
                try:
                    rating_str = season_data.get('rating', '')
                    if rating_str:
                        rating = float(rating_str)
                except (ValueError, TypeError):
                    rating = None
                
                rank = None
                rank_data = season_data.get('rank', {})
                if isinstance(rank_data, dict):
                    rank = rank_data.get('value')
                
                # Try to get competition name from competition object or derive it
                competition_data = season_data.get('competition', {})
                if isinstance(competition_data, dict):
                    competition_name = competition_data.get('name', '')
                
                # If still no name, use season name as fallback
                if not competition_name and season_name:
                    competition_name = season_name.split()[0] if ' ' in season_name else season_name
                
                player_season = PlayerSeasonStats(
                    competition_id=competition_id,
                    competition_name=competition_name,
                    season_name=season_name,
                    matches_played=matches_played,
                    goals=goals,
                    assists=assists,
                    rating=rating,
                    rank=rank
                )
                seasonal_form.append(player_season)
            
            # Parse next match
            next_match = data.get('next_match')
            
            player_stats = PlayerStats(
                player_id=player_id,
                player_name=player_name,
                position=position,
                team_id=team_id,
                team_name=team_name,
                seasonal_form=seasonal_form,
                next_match=next_match
            )
            
            return player_stats
            
        except Exception as e:
            logger.error(f"Error fetching player stats for {player_id}: {e}")
            return None
    
    async def get_team_stats(self, team_id: str) -> Optional[TeamStats]:
        """
        Get team statistics including BTTS, clean sheets, goals per game.
        
        Args:
            team_id: Team ID string (e.g., "1FmdLfx4H9O2Ouk5Lbphws")
            
        Returns:
            TeamStats with form stats, standings, next match
            
        Example:
            GET /v2/soccer/teams/overview/brsuperbetsport/pt-BR?team-id=1FmdLfx4H9O2Ouk5Lbphws
        """
        try:
            params = {'team-id': team_id}
            data = await self._get(
                f"v2/soccer/teams/overview/{self.PLATFORM}/{self.LOCALE}",
                params=params
            )
            
            if not data:
                logger.warning(f"No team data found for {team_id}")
                return None
            
            # Parse team name
            team_data = data.get('team', {})
            team_name = team_data.get('name', '')
            
            # Parse form stats
            form_data = data.get('form', {})
            all_matches_data = form_data.get('all_matches', {})
            stats_data = all_matches_data.get('stats', [])
            
            # Initialize default values
            goals_scored_per_game = 0.0
            goals_conceded_per_game = 0.0
            btts_rate = "0/0"
            clean_sheet_rate = "0/0"
            corners_per_game = 0.0
            yellows_per_game = 0.0
            
            # Parse stats
            for stat in stats_data:
                stat_type = stat.get('type', 0)
                value = stat.get('value', '0')
                
                # Convert value to appropriate type
                try:
                    if stat_type in [0, 1, 3, 4]:  # Numeric stats
                        numeric_value = float(value)
                        
                        if stat_type == 3:  # Goals scored per game
                            goals_scored_per_game = numeric_value
                        elif stat_type == 4:  # Goals conceded per game
                            goals_conceded_per_game = numeric_value
                        elif stat_type == 0:  # Corners per game
                            corners_per_game = numeric_value
                        elif stat_type == 1:  # Yellow cards per game
                            yellows_per_game = numeric_value
                    elif stat_type == 5:  # BTTS (string format "1/5")
                        btts_rate = value
                    elif stat_type == 2:  # Clean sheets (string format "3/5")
                        clean_sheet_rate = value
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse stat type {stat_type} with value {value}")
            
            team_form_stats = TeamFormStats(
                goals_scored_per_game=goals_scored_per_game,
                goals_conceded_per_game=goals_conceded_per_game,
                btts_rate=btts_rate,
                clean_sheet_rate=clean_sheet_rate,
                corners_per_game=corners_per_game,
                yellows_per_game=yellows_per_game
            )
            
            # Parse standings
            standings = []
            for standing_data in data.get('standings', []):
                competition_data = standing_data.get('competition', {})
                competition_name = competition_data.get('name', '') if isinstance(competition_data, dict) else ''
                
                position_data = standing_data.get('position', {})
                position = position_data.get('value', 0) if isinstance(position_data, dict) else 0
                
                standing = TeamStanding(
                    competition_name=competition_name,
                    position=position
                )
                standings.append(standing)
            
            # Parse recent matches
            recent_matches = all_matches_data.get('matches', [])
            
            # Parse next match
            next_match = data.get('next_match')
            
            team_stats = TeamStats(
                team_id=team_id,
                team_name=team_name,
                form_stats=team_form_stats,
                standings=standings,
                recent_matches=recent_matches,
                next_match=next_match
            )
            
            return team_stats
            
        except Exception as e:
            logger.error(f"Error fetching team stats for {team_id}: {e}")
            return None
