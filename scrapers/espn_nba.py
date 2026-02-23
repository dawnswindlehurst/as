"""ESPN NBA Stats Collector - API based."""
import requests
import time
import unicodedata
from typing import List, Dict
from dataclasses import dataclass
from utils.logger import log


@dataclass
class ESPNPlayer:
    """ESPN player data."""
    espn_id: str
    name: str
    team_id: str = ""
    team_name: str = ""
    position: str = ""
    jersey: str = ""


@dataclass
class ESPNGameStats:
    """Game stats from ESPN."""
    game_id: str = ""
    game_date: str = ""
    opponent: str = ""
    home_away: str = ""
    result: str = ""
    points: int = 0
    rebounds: int = 0
    assists: int = 0
    steals: int = 0
    blocks: int = 0
    turnovers: int = 0
    fouls: int = 0
    fgm: int = 0
    fga: int = 0
    fg3m: int = 0
    fg3a: int = 0
    ftm: int = 0
    fta: int = 0
    minutes: int = 0


class ESPNNBACollector:
    """Collects NBA data from ESPN API."""
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
    WEB_API_URL = "https://site.web.api.espn.com/apis"
    
    # Stats order: MIN, FG, FG%, 3PT, 3P%, FT, FT%, REB, AST, BLK, STL, PF, TO, PTS
    STAT_INDICES = {
        'minutes': 0,
        'fg': 1,       # "9-21" format
        'fg_pct': 2,
        '3pt': 3,      # "1-5" format
        '3pt_pct': 4,
        'ft': 5,       # "3-6" format
        'ft_pct': 6,
        'rebounds': 7,
        'assists': 8,
        'blocks': 9,
        'steals': 10,
        'fouls': 11,
        'turnovers': 12,
        'points': 13,
    }
    
    KNOWN_PLAYERS = {
        'lebron james': '1966',
        'stephen curry': '3975',
        'kevin durant': '3202',
        'giannis antetokounmpo': '3032977',
        'luka doncic': '3945274',
        'nikola jokic': '3112335',
        'joel embiid': '3059318',
        'jayson tatum': '4065648',
        'damian lillard': '6606',
        'anthony davis': '6583',
        'kawhi leonard': '6450',
        'james harden': '3992',
        'kyrie irving': '6442',
        'devin booker': '3136193',
        'donovan mitchell': '3934719',
        'trae young': '4277905',
        'jimmy butler': '6430',
        'shai gilgeous-alexander': '4278073',
        'tyrese haliburton': '4433137',
        'jaylen brown': '3917376',
        'anthony edwards': '4594268',
        'victor wembanyama': '5104157',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        self.player_cache: Dict[str, str] = {}
    
    def _normalize_name(self, name: str) -> str:
        """Normalize player name for matching."""
        name = ''.join(c for c in unicodedata.normalize('NFD', name) 
                       if unicodedata.category(c) != 'Mn')
        return name.lower().strip().replace('.', '').replace("'", '')
    
    def _parse_made_attempted(self, value: str) -> tuple:
        """Parse '9-21' format to (made, attempted)."""
        try:
            parts = value.split('-')
            return int(parts[0]), int(parts[1])
        except:
            return 0, 0
    
    def _safe_int(self, value) -> int:
        """Safely convert to int."""
        try:
            return int(float(value))
        except:
            return 0
    
    def get_all_teams(self) -> List[Dict]:
        """Get all NBA teams."""
        try:
            url = f"{self.BASE_URL}/teams"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                log.error(f"ESPN teams API error: {response.status_code}")
                return []
            
            data = response.json()
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            result = []
            for team_data in teams:
                team = team_data.get('team', {})
                result.append({
                    'id': team.get('id'),
                    'name': team.get('displayName'),
                    'abbreviation': team.get('abbreviation'),
                    'logo': team.get('logos', [{}])[0].get('href') if team.get('logos') else None,
                })
            
            log.info(f"ESPN API: {len(result)} NBA teams")
            return result
            
        except Exception as e:
            log.error(f"Error fetching ESPN teams: {e}")
            return []
    
    def get_team_roster(self, team_id: str) -> List[ESPNPlayer]:
        """Get roster for a team."""
        try:
            url = f"{self.BASE_URL}/teams/{team_id}/roster"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            athletes = data.get('athletes', [])
            team_name = data.get('team', {}).get('displayName', '')
            
            players = []
            for athlete in athletes:
                player = ESPNPlayer(
                    espn_id=str(athlete.get('id', '')),
                    name=athlete.get('displayName', ''),
                    team_id=team_id,
                    team_name=team_name,
                    position=athlete.get('position', {}).get('abbreviation', ''),
                    jersey=athlete.get('jersey', ''),
                )
                players.append(player)
                
                norm_name = self._normalize_name(player.name)
                self.player_cache[norm_name] = player.espn_id
            
            return players
            
        except Exception as e:
            log.error(f"Error fetching roster for team {team_id}: {e}")
            return []
    
    def get_all_players(self) -> List[ESPNPlayer]:
        """Get all NBA players from all teams."""
        teams = self.get_all_teams()
        all_players = []
        
        for team in teams:
            team_id = team.get('id')
            if not team_id:
                continue
            
            time.sleep(0.3)
            players = self.get_team_roster(team_id)
            all_players.extend(players)
            log.info(f"ESPN: {team.get('name')} - {len(players)} players")
        
        log.info(f"ESPN API: {len(all_players)} total NBA players")
        return all_players
    
    def search_player_id(self, player_name: str) -> str:
        """Search for player ESPN ID."""
        norm_name = self._normalize_name(player_name)
        
        if norm_name in self.player_cache:
            return self.player_cache[norm_name]
        
        if norm_name in self.KNOWN_PLAYERS:
            return self.KNOWN_PLAYERS[norm_name]
        
        teams = self.get_all_teams()
        
        for team in teams:
            team_id = team.get('id')
            if not team_id:
                continue
            
            time.sleep(0.2)
            players = self.get_team_roster(team_id)
            
            for player in players:
                if self._normalize_name(player.name) == norm_name:
                    log.info(f"Found player: {player.name} = {player.espn_id}")
                    return player.espn_id
        
        log.warning(f"Player not found: {player_name}")
        return ""
    
    def get_player_gamelog(self, player_id: str, season: int = 2025, limit: int = 10) -> List[ESPNGameStats]:
        """Get player game log from ESPN API."""
        if not player_id:
            return []
            
        try:
            url = f"{self.WEB_API_URL}/common/v3/sports/basketball/nba/athletes/{player_id}/gamelog"
            params = {
                'season': season,
                'seasontype': 2
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                log.warning(f"Gamelog API error: {response.status_code}")
                return []
            
            data = response.json()
            
            # Get event details for dates/opponents
            events_info = data.get('events', {})
            
            # Get stats from seasonTypes
            season_types = data.get('seasonTypes', [])
            
            games = []
            
            for season_type in season_types:
                categories = season_type.get('categories', [])
                
                for category in categories:
                    events = category.get('events', [])
                    
                    for event in events:
                        if len(games) >= limit:
                            break
                        
                        event_id = event.get('eventId', '')
                        stats_arr = event.get('stats', [])
                        
                        if len(stats_arr) < 14:
                            continue
                        
                        # Parse stats
                        fgm, fga = self._parse_made_attempted(stats_arr[1])
                        fg3m, fg3a = self._parse_made_attempted(stats_arr[3])
                        ftm, fta = self._parse_made_attempted(stats_arr[5])
                        
                        game_stats = ESPNGameStats(
                            game_id=event_id,
                            minutes=self._safe_int(stats_arr[0]),
                            fgm=fgm,
                            fga=fga,
                            fg3m=fg3m,
                            fg3a=fg3a,
                            ftm=ftm,
                            fta=fta,
                            rebounds=self._safe_int(stats_arr[7]),
                            assists=self._safe_int(stats_arr[8]),
                            blocks=self._safe_int(stats_arr[9]),
                            steals=self._safe_int(stats_arr[10]),
                            fouls=self._safe_int(stats_arr[11]),
                            turnovers=self._safe_int(stats_arr[12]),
                            points=self._safe_int(stats_arr[13]),
                        )
                        
                        # Get event info if available
                        event_detail = events_info.get(event_id, {})
                        if event_detail:
                            game_stats.opponent = event_detail.get('opponent', {}).get('displayName', '')
                            game_stats.home_away = event_detail.get('homeAway', '')
                            game_stats.result = event_detail.get('gameResult', '')
                        
                        games.append(game_stats)
                    
                    if len(games) >= limit:
                        break
                
                if len(games) >= limit:
                    break
            
            log.info(f"ESPN: {len(games)} games for player {player_id}")
            return games
            
        except Exception as e:
            log.error(f"Error fetching gamelog: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_player_stats(self, player_name: str, limit: int = 10) -> List[ESPNGameStats]:
        """Get player stats by name."""
        player_id = self.search_player_id(player_name)
        
        if not player_id:
            return []
        
        time.sleep(0.3)
        return self.get_player_gamelog(player_id, limit=limit)
