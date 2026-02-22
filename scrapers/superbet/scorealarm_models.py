"""Data models for Scorealarm API integration."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ScorealarmTeam:
    """Represents a team in a match."""
    
    id: int
    name: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
        }


@dataclass
class ScorealarmScore:
    """Represents a score entry (final, period, overtime, etc)."""
    
    team1: int
    team2: int
    type: int  # 0=Final, 1=1st period, 2=2nd period, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'team1': self.team1,
            'team2': self.team2,
            'type': self.type,
        }


@dataclass
class ScorealarmCategory:
    """Represents a category (country/region)."""
    
    id: int
    name: str
    sport_id: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'sport_id': self.sport_id,
        }


@dataclass
class ScorealarmCompetition:
    """Represents a competition/league."""
    
    id: int
    name: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
        }


@dataclass
class ScorealarmSeason:
    """Represents a season."""
    
    id: int
    name: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
        }


@dataclass
class ScorealarmMatch:
    """Represents a match/event with scores and statistics."""
    
    id: int
    platform_id: str
    offer_id: Optional[str]
    match_date: datetime
    match_status: int
    match_state: int
    sport_id: int
    team1: ScorealarmTeam
    team2: ScorealarmTeam
    scores: List[ScorealarmScore]
    season: ScorealarmSeason
    competition: ScorealarmCompetition
    category: ScorealarmCategory
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'platform_id': self.platform_id,
            'offer_id': self.offer_id,
            'match_date': self.match_date.isoformat(),
            'match_status': self.match_status,
            'match_state': self.match_state,
            'sport_id': self.sport_id,
            'team1': self.team1.to_dict(),
            'team2': self.team2.to_dict(),
            'scores': [score.to_dict() for score in self.scores],
            'season': self.season.to_dict(),
            'competition': self.competition.to_dict(),
            'category': self.category.to_dict(),
        }


@dataclass
class ScorealarmMatchDetail:
    """Detailed match information including H2H, form, etc."""
    
    match: ScorealarmMatch
    h2h_stats: Optional[Dict[str, Any]] = None
    team1_form: Optional[List[Dict[str, Any]]] = None
    team2_form: Optional[List[Dict[str, Any]]] = None
    additional_stats: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'match': self.match.to_dict(),
            'h2h_stats': self.h2h_stats,
            'team1_form': self.team1_form,
            'team2_form': self.team2_form,
            'additional_stats': self.additional_stats,
        }


@dataclass
class ScorealarmTournamentDetails:
    """Tournament details including competition and season IDs."""
    
    tournament_id: int
    tournament_name: str
    competition_id: int
    competition_name: str
    seasons: List[ScorealarmSeason]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament_name,
            'competition_id': self.competition_id,
            'competition_name': self.competition_name,
            'seasons': [season.to_dict() for season in self.seasons],
        }
    
    def get_latest_season(self) -> Optional[ScorealarmSeason]:
        """Get the most recent season."""
        if not self.seasons:
            return None
        # Assuming seasons are returned in order, take the last one
        return self.seasons[-1]


@dataclass
class ScorealarmSport:
    """Represents a sport from Superbet."""
    
    id: int
    name: str
    local_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'local_name': self.local_name,
        }


@dataclass
class ScorealarmTournament:
    """Tournament from Superbet tournaments endpoint."""
    
    tournament_id: int
    tournament_name: str
    sport_id: int
    category_id: int
    category_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament_name,
            'sport_id': self.sport_id,
            'category_id': self.category_id,
            'category_name': self.category_name,
        }


# V2 API Models for Value Bets


@dataclass
class MatchStat:
    """Single match statistic (xG, shots, etc)."""
    type: int
    team1: str
    team2: str
    stat_name: str  # Parsed from text.args
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'type': self.type,
            'team1': self.team1,
            'team2': self.team2,
            'stat_name': self.stat_name,
        }


@dataclass
class LiveEvent:
    """Live event (goal, card, shot)."""
    type: int
    subtype: int
    side: int  # 1=team1, 2=team2
    minute: int
    added_time: Optional[int] = None
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    secondary_player_id: Optional[str] = None  # For assists
    secondary_player_name: Optional[str] = None
    score: Optional[str] = None  # Current score after event
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'type': self.type,
            'subtype': self.subtype,
            'side': self.side,
            'minute': self.minute,
            'added_time': self.added_time,
            'player_id': self.player_id,
            'player_name': self.player_name,
            'secondary_player_id': self.secondary_player_id,
            'secondary_player_name': self.secondary_player_name,
            'score': self.score,
        }


@dataclass
class FixtureStats:
    """Complete fixture statistics."""
    fixture_id: str
    match_stats: List[MatchStat]
    live_events: List[LiveEvent]
    statistics_by_period: Dict[int, List[MatchStat]]  # period -> stats
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'fixture_id': self.fixture_id,
            'match_stats': [stat.to_dict() for stat in self.match_stats],
            'live_events': [event.to_dict() for event in self.live_events],
            'statistics_by_period': {
                period: [stat.to_dict() for stat in stats]
                for period, stats in self.statistics_by_period.items()
            },
        }


@dataclass
class PlayerSeasonStats:
    """Player stats for a specific competition/season."""
    competition_id: str
    competition_name: str
    season_name: str
    matches_played: int
    goals: int
    assists: int
    rating: Optional[float] = None
    rank: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'competition_id': self.competition_id,
            'competition_name': self.competition_name,
            'season_name': self.season_name,
            'matches_played': self.matches_played,
            'goals': self.goals,
            'assists': self.assists,
            'rating': self.rating,
            'rank': self.rank,
        }


@dataclass
class PlayerStats:
    """Complete player statistics."""
    player_id: str
    player_name: str
    position: Optional[str] = None
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    seasonal_form: List[PlayerSeasonStats] = field(default_factory=list)
    next_match: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'player_id': self.player_id,
            'player_name': self.player_name,
            'position': self.position,
            'team_id': self.team_id,
            'team_name': self.team_name,
            'seasonal_form': [season.to_dict() for season in self.seasonal_form],
            'next_match': self.next_match,
        }


@dataclass
class TeamFormStats:
    """Team form statistics."""
    goals_scored_per_game: float
    goals_conceded_per_game: float
    btts_rate: str  # "1/5" format
    clean_sheet_rate: str  # "3/5" format
    corners_per_game: float
    yellows_per_game: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'goals_scored_per_game': self.goals_scored_per_game,
            'goals_conceded_per_game': self.goals_conceded_per_game,
            'btts_rate': self.btts_rate,
            'clean_sheet_rate': self.clean_sheet_rate,
            'corners_per_game': self.corners_per_game,
            'yellows_per_game': self.yellows_per_game,
        }


@dataclass  
class TeamStanding:
    """Team standing in a competition."""
    competition_name: str
    position: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'competition_name': self.competition_name,
            'position': self.position,
        }


@dataclass
class TeamStats:
    """Complete team statistics."""
    team_id: str
    team_name: str
    form_stats: TeamFormStats
    standings: List[TeamStanding] = field(default_factory=list)
    recent_matches: List[Dict[str, Any]] = field(default_factory=list)
    next_match: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'team_id': self.team_id,
            'team_name': self.team_name,
            'form_stats': self.form_stats.to_dict(),
            'standings': [standing.to_dict() for standing in self.standings],
            'recent_matches': self.recent_matches,
            'next_match': self.next_match,
        }
