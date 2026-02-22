"""Scorealarm database models for multi-sport support."""
from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Date, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator
from database.models import Base


class JSONBCompat(TypeDecorator):
    """JSONB type that falls back to JSON for non-PostgreSQL databases."""
    impl = JSON
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


class ScorealarmSport(Base):
    """Sports available in Scorealarm."""
    __tablename__ = "scorealarm_sports"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    superbet_id = Column(Integer, unique=True)
    is_gold = Column(Boolean, default=False)  # Esportes menos analisados
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ScorealarmCategory(Base):
    """Categories (countries/regions) for tournaments."""
    __tablename__ = "scorealarm_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    sport_id = Column(Integer, ForeignKey("scorealarm_sports.id"))
    country_code = Column(String(10))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ScorealarmTournament(Base):
    """Tournaments/Leagues."""
    __tablename__ = "scorealarm_tournaments"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("scorealarm_categories.id"))
    sport_id = Column(Integer, ForeignKey("scorealarm_sports.id"))
    axilis_id = Column(String(100))  # ax:tournament:xxx
    betradar_id = Column(String(100))  # br:tournament:xxx
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ScorealarmSeason(Base):
    """Seasons within tournaments."""
    __tablename__ = "scorealarm_seasons"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    tournament_id = Column(Integer, ForeignKey("scorealarm_tournaments.id"))
    axilis_id = Column(String(100))  # ax:season:xxx
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ScorealarmTeam(Base):
    """Teams across all sports."""
    __tablename__ = "scorealarm_teams"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    short_name = Column(String(50))
    sport_id = Column(Integer, ForeignKey("scorealarm_sports.id"))
    country_code = Column(String(10))
    axilis_id = Column(String(100))  # ax:team:xxx
    betradar_id = Column(String(100))  # br:competitor:xxx
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ScorealarmMatch(Base):
    """Matches/Events from Scorealarm."""
    __tablename__ = "scorealarm_matches"
    
    id = Column(Integer, primary_key=True)
    
    # IDs externos
    platform_id = Column(String(100))  # br:match:xxx
    offer_id = Column(String(100))  # ax:match:xxx
    
    # Relacionamentos
    sport_id = Column(Integer, ForeignKey("scorealarm_sports.id"))
    tournament_id = Column(Integer, ForeignKey("scorealarm_tournaments.id"))
    season_id = Column(Integer, ForeignKey("scorealarm_seasons.id"))
    team1_id = Column(Integer, ForeignKey("scorealarm_teams.id"))
    team2_id = Column(Integer, ForeignKey("scorealarm_teams.id"))
    
    # Match info
    match_date = Column(DateTime, index=True)
    match_status = Column(Integer)  # 0=scheduled, 100=finished, etc
    
    # Scores
    team1_score = Column(Integer, nullable=True)
    team2_score = Column(Integer, nullable=True)
    
    # Status de processamento
    is_finished = Column(Boolean, default=False, index=True)
    finished_at = Column(DateTime, nullable=True)
    
    # V2 API Enrichment - Detailed stats
    enriched_at = Column(DateTime, nullable=True, index=True)
    xg_home = Column(Float, nullable=True)  # Expected Goals home team
    xg_away = Column(Float, nullable=True)  # Expected Goals away team
    shots_on_goal_home = Column(Integer, nullable=True)
    shots_on_goal_away = Column(Integer, nullable=True)
    corners_home = Column(Integer, nullable=True)
    corners_away = Column(Integer, nullable=True)
    goal_events = Column(JSON, nullable=True)  # List of goal events with player details
    
    # V2 API Raw Data - Complete API response for future analysis
    match_stats_raw = Column(JSONBCompat, nullable=True)  # All match statistics from V2 soccer/fixtures API
    live_events_raw = Column(JSONBCompat, nullable=True)  # All live events from API

    # Detailed raw data for value bet analysis (from event/detail endpoint)
    match_statistics_raw = Column(JSONBCompat, nullable=True)  # statistics array (by period) from event/detail
    score_trend_raw = Column(JSONBCompat, nullable=True)        # score evolution minute by minute

    # Game metadata
    venue_id = Column(Integer, nullable=True)             # Stadium ID
    coverage_level = Column(JSONBCompat, nullable=True)   # ["livescout", ...]
    number_of_periods = Column(Integer, nullable=True)    # 4, 5 (OT), etc
    period_duration = Column(Integer, nullable=True)      # 10 or 12 minutes
    leading_team = Column(Integer, nullable=True)         # 1 or 2

    # Tennis-specific fields
    ground_type = Column(Integer, nullable=True)          # 1=clay, 2=grass, 3=hard, 4=indoor
    team1_seed = Column(Integer, nullable=True)
    team2_seed = Column(Integer, nullable=True)
    tournament_round = Column(String(100), nullable=True)
    prize_money = Column(Integer, nullable=True)
    prize_currency = Column(String(10), nullable=True)

    # Tennis - Set durations
    set1_duration = Column(Integer, nullable=True)        # minutes
    set2_duration = Column(Integer, nullable=True)
    set3_duration = Column(Integer, nullable=True)
    set4_duration = Column(Integer, nullable=True)
    set5_duration = Column(Integer, nullable=True)
    total_duration = Column(Integer, nullable=True)       # sum of all sets

    # Tennis - Serve statistics
    aces_home = Column(Integer, nullable=True)
    aces_away = Column(Integer, nullable=True)
    double_faults_home = Column(Integer, nullable=True)
    double_faults_away = Column(Integer, nullable=True)
    first_serve_pct_home = Column(Float, nullable=True)   # 0.65 means 65%
    first_serve_pct_away = Column(Float, nullable=True)
    first_serve_won_pct_home = Column(Float, nullable=True)
    first_serve_won_pct_away = Column(Float, nullable=True)
    second_serve_won_pct_home = Column(Float, nullable=True)
    second_serve_won_pct_away = Column(Float, nullable=True)

    # Tennis - Break points
    break_points_faced_home = Column(Integer, nullable=True)
    break_points_saved_home = Column(Integer, nullable=True)
    break_points_faced_away = Column(Integer, nullable=True)
    break_points_saved_away = Column(Integer, nullable=True)
    break_points_converted_home = Column(Integer, nullable=True)
    break_points_converted_away = Column(Integer, nullable=True)

    # Tennis - Service games
    service_games_won_home = Column(Integer, nullable=True)
    service_games_total_home = Column(Integer, nullable=True)
    service_games_won_away = Column(Integer, nullable=True)
    service_games_total_away = Column(Integer, nullable=True)

    # Tennis - Total games (for over/under)
    total_games = Column(Integer, nullable=True)

    # Tennis - Point by point raw data
    point_by_point_raw = Column(JSONBCompat, nullable=True)

    # Basketball shooting stats
    ft_made_home = Column(Integer, nullable=True)
    ft_attempted_home = Column(Integer, nullable=True)
    ft_made_away = Column(Integer, nullable=True)
    ft_attempted_away = Column(Integer, nullable=True)
    fg2_made_home = Column(Integer, nullable=True)
    fg2_attempted_home = Column(Integer, nullable=True)
    fg2_made_away = Column(Integer, nullable=True)
    fg2_attempted_away = Column(Integer, nullable=True)
    fg3_made_home = Column(Integer, nullable=True)
    fg3_attempted_home = Column(Integer, nullable=True)
    fg3_made_away = Column(Integer, nullable=True)
    fg3_attempted_away = Column(Integer, nullable=True)

    # Basketball box score
    rebounds_home = Column(Integer, nullable=True)
    rebounds_away = Column(Integer, nullable=True)
    assists_home = Column(Integer, nullable=True)
    assists_away = Column(Integer, nullable=True)
    turnovers_home = Column(Integer, nullable=True)
    turnovers_away = Column(Integer, nullable=True)
    steals_home = Column(Integer, nullable=True)
    steals_away = Column(Integer, nullable=True)
    blocks_home = Column(Integer, nullable=True)
    blocks_away = Column(Integer, nullable=True)
    fouls_home = Column(Integer, nullable=True)
    fouls_away = Column(Integer, nullable=True)

    # Basketball game flow
    biggest_lead_home = Column(Integer, nullable=True)
    biggest_lead_away = Column(Integer, nullable=True)
    time_in_lead_home = Column(String(10), nullable=True)  # "38:53"
    time_in_lead_away = Column(String(10), nullable=True)  # "00:00"
    lead_changes = Column(Integer, nullable=True)          # calculated from score_trend

    # Volleyball - Sets
    sets_home = Column(Integer, nullable=True)              # Sets won by home team
    sets_away = Column(Integer, nullable=True)              # Sets won by away team

    # Volleyball - Points per set
    set1_home = Column(Integer, nullable=True)
    set1_away = Column(Integer, nullable=True)
    set2_home = Column(Integer, nullable=True)
    set2_away = Column(Integer, nullable=True)
    set3_home = Column(Integer, nullable=True)
    set3_away = Column(Integer, nullable=True)
    set4_home = Column(Integer, nullable=True)
    set4_away = Column(Integer, nullable=True)
    set5_home = Column(Integer, nullable=True)
    set5_away = Column(Integer, nullable=True)

    # Volleyball - Calculated totals
    total_points_home = Column(Integer, nullable=True)      # Sum of all points scored
    total_points_away = Column(Integer, nullable=True)
    total_sets_played = Column(Integer, nullable=True)      # 3, 4 or 5

    # Volleyball - Derived metrics
    avg_points_per_set_home = Column(Float, nullable=True)  # Average points per set
    avg_points_per_set_away = Column(Float, nullable=True)
    point_diff_per_set = Column(JSONBCompat, nullable=True)  # [2, 2, 7] point difference per set

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ScorealarmScore(Base):
    """Scores por período (quarter, half, set, map, etc)."""
    __tablename__ = "scorealarm_scores"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("scorealarm_matches.id"))
    period_type = Column(String(50))  # "q1", "q2", "half1", "set1", "map1", etc
    period_number = Column(Integer)
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class OddsHistory(Base):
    """Histórico de odds para detectar movimentos."""
    __tablename__ = "odds_history"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("scorealarm_matches.id"))
    
    market_type = Column(String(50))  # "moneyline", "over_under", "handicap"
    team1_odds = Column(Float)
    team2_odds = Column(Float)
    draw_odds = Column(Float, nullable=True)
    line = Column(Float, nullable=True)  # Para over/under, handicap
    
    bookmaker = Column(String(50), default="superbet")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class ScorealarmTeamRating(Base):
    """Rating ELO/Glicko dos times do Scorealarm."""
    __tablename__ = "scorealarm_team_ratings"
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("scorealarm_teams.id"), unique=True)
    
    elo_rating = Column(Float, default=1500.0)
    glicko_rating = Column(Float, default=1500.0)
    glicko_rd = Column(Float, default=350.0)  # Rating deviation
    glicko_vol = Column(Float, default=0.06)  # Volatility
    
    matches_played = Column(Integer, default=0)
    last_match_date = Column(DateTime, nullable=True)
    
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
