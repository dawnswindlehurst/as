"""Historical database models for comprehensive sports betting analysis."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON, Date, Time
from sqlalchemy.orm import relationship

# Import Base from the main models to avoid circular imports
try:
    from database.models import Base
except ImportError:
    # Fallback if models not available
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()


# ============================================================================
# NBA MODELS
# ============================================================================

class NBAGame(Base):
    """NBA game model with complete stats."""
    __tablename__ = "nba_games"
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(100), unique=True, nullable=False)
    season = Column(String(20))  # "2024-25"
    season_type = Column(String(20))  # "regular", "playoffs", "playin"
    game_date = Column(Date)
    
    home_team = Column(String(100))
    away_team = Column(String(100))
    home_score = Column(Integer)
    away_score = Column(Integer)
    
    # Quarter scores
    home_q1 = Column(Integer)
    home_q2 = Column(Integer)
    home_q3 = Column(Integer)
    home_q4 = Column(Integer)
    home_ot = Column(Integer)
    away_q1 = Column(Integer)
    away_q2 = Column(Integer)
    away_q3 = Column(Integer)
    away_q4 = Column(Integer)
    away_ot = Column(Integer)
    
    total_points = Column(Integer)
    spread = Column(Float)
    over_under = Column(Float)
    home_odds = Column(Float)
    away_odds = Column(Float)
    
    attendance = Column(Integer)
    arena = Column(String(200))
    
    is_back_to_back_home = Column(Boolean)
    is_back_to_back_away = Column(Boolean)
    days_rest_home = Column(Integer)
    days_rest_away = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player_stats = relationship("NBAPlayerGameStats", back_populates="game", cascade="all, delete-orphan")


class NBAPlayerGameStats(Base):
    """NBA player game statistics."""
    __tablename__ = "nba_player_game_stats"
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(100), ForeignKey("nba_games.game_id"))
    player_id = Column(String(50))
    player_name = Column(String(100))
    team = Column(String(100))
    is_home = Column(Boolean)
    is_starter = Column(Boolean)
    minutes = Column(Integer)
    
    # Scoring
    points = Column(Integer)
    field_goals_made = Column(Integer)
    field_goals_attempted = Column(Integer)
    fg_percentage = Column(Float)
    three_pointers_made = Column(Integer)
    three_pointers_attempted = Column(Integer)
    three_percentage = Column(Float)
    free_throws_made = Column(Integer)
    free_throws_attempted = Column(Integer)
    ft_percentage = Column(Float)
    
    # Rebounds
    rebounds_offensive = Column(Integer)
    rebounds_defensive = Column(Integer)
    rebounds_total = Column(Integer)
    
    # Other stats
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    personal_fouls = Column(Integer)
    plus_minus = Column(Integer)
    
    # Fantasy/Props combos
    pts_reb_ast = Column(Integer)  # PRA combo
    pts_reb = Column(Integer)
    pts_ast = Column(Integer)
    reb_ast = Column(Integer)
    stocks = Column(Integer)  # Steals + Blocks
    fantasy_points = Column(Float)
    
    # Context
    opponent = Column(String(100))
    opponent_defensive_rating = Column(Float)
    is_back_to_back = Column(Boolean)
    days_rest = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    game = relationship("NBAGame", back_populates="player_stats")


class NBATeamStats(Base):
    """NBA team statistics and metrics."""
    __tablename__ = "nba_team_stats"
    
    id = Column(Integer, primary_key=True)
    team = Column(String(100))
    season = Column(String(20))
    game_date = Column(Date)
    
    # Record
    wins = Column(Integer)
    losses = Column(Integer)
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    away_wins = Column(Integer)
    away_losses = Column(Integer)
    
    # Ratings
    offensive_rating = Column(Float)
    defensive_rating = Column(Float)
    net_rating = Column(Float)
    pace = Column(Float)
    
    # Averages
    ppg = Column(Float)  # Points per game
    oppg = Column(Float)  # Opponent PPG
    rpg = Column(Float)  # Rebounds per game
    apg = Column(Float)  # Assists per game
    spg = Column(Float)  # Steals per game
    bpg = Column(Float)  # Blocks per game
    tpg = Column(Float)  # Turnovers per game
    
    # Shooting
    fg_percentage = Column(Float)
    three_percentage = Column(Float)
    ft_percentage = Column(Float)
    
    # Advanced
    ats_record = Column(String(20))  # Against the spread: "15-10"
    over_under_record = Column(String(20))  # O/U record: "12-13"
    last_10 = Column(String(20))  # "7-3"
    streak = Column(String(20))  # "W3" or "L2"
    
    created_at = Column(DateTime, default=datetime.utcnow)


class NBAPlayerPropsAnalysis(Base):
    """NBA player props comprehensive analysis."""
    __tablename__ = "nba_player_props_analysis"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String(50))
    player_name = Column(String(100))
    team = Column(String(100))
    prop_type = Column(String(50))  # "points", "rebounds", "assists", "pra", etc
    line = Column(Float)  # Ex: 25.5
    
    # Overall Stats
    season_avg = Column(Float)
    season_games = Column(Integer)
    over_count = Column(Integer)
    under_count = Column(Integer)
    over_rate = Column(Float)
    
    # Home/Away Splits
    home_avg = Column(Float)
    home_games = Column(Integer)
    home_over_rate = Column(Float)
    away_avg = Column(Float)
    away_games = Column(Integer)
    away_over_rate = Column(Float)
    
    # After Win/Loss
    after_win_avg = Column(Float)
    after_win_over_rate = Column(Float)
    after_loss_avg = Column(Float)
    after_loss_over_rate = Column(Float)
    
    # After Win Streak (3+)
    after_win_streak_avg = Column(Float)
    after_win_streak_over_rate = Column(Float)
    
    # After Loss Streak (3+)
    after_loss_streak_avg = Column(Float)
    after_loss_streak_over_rate = Column(Float)
    
    # vs Defense Quality
    vs_top10_defense_avg = Column(Float)
    vs_top10_defense_over_rate = Column(Float)
    vs_bottom10_defense_avg = Column(Float)
    vs_bottom10_defense_over_rate = Column(Float)
    
    # Rest Days Impact
    no_rest_avg = Column(Float)  # Back to back
    no_rest_over_rate = Column(Float)
    one_day_rest_avg = Column(Float)
    one_day_rest_over_rate = Column(Float)
    two_plus_rest_avg = Column(Float)
    two_plus_rest_over_rate = Column(Float)
    
    # With/Without Key Teammate
    with_teammate_avg = Column(Float)  # Ex: AD playing for Lakers
    with_teammate_over_rate = Column(Float)
    without_teammate_avg = Column(Float)
    without_teammate_over_rate = Column(Float)
    key_teammate = Column(String(100))  # Name of key teammate
    
    # Last N Games
    last_5_avg = Column(Float)
    last_5_over_rate = Column(Float)
    last_10_avg = Column(Float)
    last_10_over_rate = Column(Float)
    
    # Trend
    trend = Column(String(20))  # "UP", "DOWN", "STABLE"
    trend_last_5 = Column(Float)  # % change
    
    # Head to Head vs Opponent
    vs_opponent = Column(String(100))
    vs_opponent_avg = Column(Float)
    vs_opponent_games = Column(Integer)
    vs_opponent_over_rate = Column(Float)
    
    updated_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# SOCCER MODELS
# ============================================================================

class SoccerMatch(Base):
    """Soccer match model with complete stats."""
    __tablename__ = "soccer_matches"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(100), unique=True, nullable=False)
    league = Column(String(50))  # "eng.1", "bra.1", "uefa.champions"
    league_name = Column(String(200))  # "Premier League"
    season = Column(String(20))  # "2025-26"
    round = Column(String(50))  # "Matchday 20" or "Quarter-Final"
    match_date = Column(Date)
    kickoff_time = Column(Time)
    
    home_team = Column(String(100))
    away_team = Column(String(100))
    home_score = Column(Integer)
    away_score = Column(Integer)
    halftime_home = Column(Integer)
    halftime_away = Column(Integer)
    
    # Goals timing
    home_first_half_goals = Column(Integer)
    home_second_half_goals = Column(Integer)
    away_first_half_goals = Column(Integer)
    away_second_half_goals = Column(Integer)
    
    # Match Stats
    home_possession = Column(Float)
    away_possession = Column(Float)
    home_shots = Column(Integer)
    away_shots = Column(Integer)
    home_shots_on_target = Column(Integer)
    away_shots_on_target = Column(Integer)
    home_corners = Column(Integer)
    away_corners = Column(Integer)
    home_fouls = Column(Integer)
    away_fouls = Column(Integer)
    home_yellow_cards = Column(Integer)
    away_yellow_cards = Column(Integer)
    home_red_cards = Column(Integer)
    away_red_cards = Column(Integer)
    
    # Betting Results
    total_goals = Column(Integer)
    btts = Column(Boolean)  # Both Teams To Score
    over_0_5 = Column(Boolean)
    over_1_5 = Column(Boolean)
    over_2_5 = Column(Boolean)
    over_3_5 = Column(Boolean)
    over_4_5 = Column(Boolean)
    first_half_over_0_5 = Column(Boolean)
    first_half_over_1_5 = Column(Boolean)
    
    # Odds (closing)
    home_odds = Column(Float)
    draw_odds = Column(Float)
    away_odds = Column(Float)
    over_2_5_odds = Column(Float)
    under_2_5_odds = Column(Float)
    btts_yes_odds = Column(Float)
    btts_no_odds = Column(Float)
    
    # Context
    home_form = Column(String(10))  # "WWDLW"
    away_form = Column(String(10))  # "LDWWL"
    home_position = Column(Integer)  # League position
    away_position = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SoccerTeamStats(Base):
    """Soccer team statistics."""
    __tablename__ = "soccer_team_stats"
    
    id = Column(Integer, primary_key=True)
    team = Column(String(100))
    league = Column(String(50))
    season = Column(String(20))
    
    # Record
    played = Column(Integer)
    wins = Column(Integer)
    draws = Column(Integer)
    losses = Column(Integer)
    home_wins = Column(Integer)
    home_draws = Column(Integer)
    home_losses = Column(Integer)
    away_wins = Column(Integer)
    away_draws = Column(Integer)
    away_losses = Column(Integer)
    
    # Goals
    goals_scored = Column(Integer)
    goals_conceded = Column(Integer)
    goal_difference = Column(Integer)
    home_goals_scored = Column(Integer)
    home_goals_conceded = Column(Integer)
    away_goals_scored = Column(Integer)
    away_goals_conceded = Column(Integer)
    
    # Clean Sheets
    clean_sheets = Column(Integer)
    home_clean_sheets = Column(Integer)
    away_clean_sheets = Column(Integer)
    failed_to_score = Column(Integer)
    
    # Betting Stats
    btts_percentage = Column(Float)
    home_btts_percentage = Column(Float)
    away_btts_percentage = Column(Float)
    
    over_2_5_percentage = Column(Float)
    home_over_2_5_percentage = Column(Float)
    away_over_2_5_percentage = Column(Float)
    
    over_1_5_percentage = Column(Float)
    under_1_5_percentage = Column(Float)
    
    # First Half
    first_half_goals_scored = Column(Integer)
    first_half_goals_conceded = Column(Integer)
    first_half_clean_sheets = Column(Integer)
    
    # Corners
    corners_for_avg = Column(Float)
    corners_against_avg = Column(Float)
    
    # Cards
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    
    # Form
    form = Column(String(10))  # "WWDLW"
    last_5_points = Column(Integer)
    position = Column(Integer)
    points = Column(Integer)
    
    updated_at = Column(DateTime, default=datetime.utcnow)


class SoccerPlayerStats(Base):
    """Soccer player statistics."""
    __tablename__ = "soccer_player_stats"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String(50))
    player_name = Column(String(100))
    team = Column(String(100))
    league = Column(String(50))
    season = Column(String(20))
    position = Column(String(10))  # "FW", "MF", "DF", "GK"
    
    # Appearances
    appearances = Column(Integer)
    starts = Column(Integer)
    minutes = Column(Integer)
    
    # Goals & Assists
    goals = Column(Integer)
    assists = Column(Integer)
    penalties_scored = Column(Integer)
    penalties_missed = Column(Integer)
    
    # Shooting
    shots = Column(Integer)
    shots_on_target = Column(Integer)
    shot_accuracy = Column(Float)
    goals_per_90 = Column(Float)
    
    # Passing
    passes = Column(Integer)
    pass_accuracy = Column(Float)
    key_passes = Column(Integer)
    crosses = Column(Integer)
    
    # Defending
    tackles = Column(Integer)
    interceptions = Column(Integer)
    clearances = Column(Integer)
    blocks = Column(Integer)
    
    # Discipline
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    fouls_committed = Column(Integer)
    fouls_drawn = Column(Integer)
    
    # Goalscorer Props
    anytime_scorer_appearances = Column(Integer)
    anytime_scorer_hits = Column(Integer)
    anytime_scorer_rate = Column(Float)
    
    # Home/Away Splits
    home_goals = Column(Integer)
    home_assists = Column(Integer)
    away_goals = Column(Integer)
    away_assists = Column(Integer)
    
    updated_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# ESPORTS MODELS
# ============================================================================

class EsportsMatch(Base):
    """Esports match model."""
    __tablename__ = "esports_matches"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(100), unique=True, nullable=False)
    game = Column(String(50))  # "lol", "valorant", "dota2", "cs2"
    
    # Tournament Info
    tournament = Column(String(200))  # "VCT 2026: Americas Kickoff"
    tournament_tier = Column(String(10))  # "S", "A", "B", "C"
    stage = Column(String(100))  # "Playoffs", "Groups", "Swiss"
    round = Column(String(100))  # "Grand Final", "Upper Bracket R1"
    
    match_date = Column(DateTime)
    
    # Teams
    team1 = Column(String(100))
    team2 = Column(String(100))
    team1_region = Column(String(50))
    team2_region = Column(String(50))
    
    # Score
    team1_score = Column(Integer)  # Maps won
    team2_score = Column(Integer)
    winner = Column(String(100))
    
    # Best of
    best_of = Column(Integer)  # 1, 3, 5
    
    # Maps (for multi-map games)
    maps_played = Column(JSON)  # JSON array of maps
    
    # Odds
    team1_odds = Column(Float)
    team2_odds = Column(Float)
    
    # Context
    team1_form = Column(String(10))  # "WWLWW"
    team2_form = Column(String(10))
    team1_world_rank = Column(Integer)
    team2_world_rank = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    map_stats = relationship("EsportsMapStats", back_populates="match", cascade="all, delete-orphan")
    player_stats = relationship("EsportsPlayerStats", back_populates="match", cascade="all, delete-orphan")


class EsportsMapStats(Base):
    """Esports map statistics (CS2, Valorant)."""
    __tablename__ = "esports_map_stats"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(100), ForeignKey("esports_matches.match_id"))
    map_number = Column(Integer)  # 1, 2, 3
    map_name = Column(String(50))  # "Inferno", "Ascent"
    
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    team1_first_half = Column(Integer)
    team2_first_half = Column(Integer)
    team1_second_half = Column(Integer)
    team2_second_half = Column(Integer)
    
    # Overtime
    overtime_rounds = Column(Integer)
    
    # Side Stats (CS2/Valorant)
    team1_ct_rounds = Column(Integer)
    team1_t_rounds = Column(Integer)
    team2_ct_rounds = Column(Integer)
    team2_t_rounds = Column(Integer)
    
    winner = Column(String(100))
    
    # Over/Under
    total_rounds = Column(Integer)
    over_22_5 = Column(Boolean)
    over_24_5 = Column(Boolean)
    over_26_5 = Column(Boolean)
    
    # Relationship
    match = relationship("EsportsMatch", back_populates="map_stats")


class EsportsPlayerStats(Base):
    """Esports player statistics."""
    __tablename__ = "esports_player_stats"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(100), ForeignKey("esports_matches.match_id"))
    map_number = Column(Integer)  # 0 for overall match
    
    player_name = Column(String(100))
    player_id = Column(String(50))
    team = Column(String(100))
    
    # Common Stats
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    kd_ratio = Column(Float)
    
    # Game Specific - CS2/Valorant
    adr = Column(Float)  # Average Damage per Round
    kast = Column(Float)  # Kill/Assist/Survive/Trade %
    hs_percentage = Column(Float)  # Headshot %
    first_kills = Column(Integer)
    first_deaths = Column(Integer)
    clutches_won = Column(Integer)
    clutches_played = Column(Integer)
    rating = Column(Float)  # HLTV/VLR rating
    acs = Column(Float)  # Average Combat Score (Valorant)
    
    # LoL/Dota
    cs = Column(Integer)  # Creep Score
    cs_per_min = Column(Float)
    gold = Column(Integer)
    gold_per_min = Column(Float)
    damage_dealt = Column(Integer)
    damage_taken = Column(Integer)
    vision_score = Column(Integer)
    wards_placed = Column(Integer)
    
    # Agent/Champion/Hero
    agent = Column(String(50))  # Valorant agent
    champion = Column(String(50))  # LoL champion
    hero = Column(String(50))  # Dota hero
    
    # Relationship
    match = relationship("EsportsMatch", back_populates="player_stats")


class EsportsTeamStats(Base):
    """Esports team statistics."""
    __tablename__ = "esports_team_stats"
    
    id = Column(Integer, primary_key=True)
    team = Column(String(100))
    game = Column(String(50))
    region = Column(String(50))
    
    # Period
    period = Column(String(100))  # "2026-01", "VCT 2026 Kickoff"
    
    # Record
    matches_played = Column(Integer)
    matches_won = Column(Integer)
    matches_lost = Column(Integer)
    win_rate = Column(Float)
    
    maps_played = Column(Integer)
    maps_won = Column(Integer)
    maps_lost = Column(Integer)
    map_win_rate = Column(Float)
    
    # Rankings
    world_rank = Column(Integer)
    regional_rank = Column(Integer)
    
    # Form
    form = Column(String(10))  # "WWLWW"
    current_streak = Column(String(10))  # "W3"
    
    # Map Pool (CS2/Valorant)
    best_map = Column(String(50))
    best_map_win_rate = Column(Float)
    worst_map = Column(String(50))
    worst_map_win_rate = Column(Float)
    map_pool = Column(JSON)  # JSON with all map stats
    
    # vs Tiers
    vs_s_tier_record = Column(String(20))  # "3-5"
    vs_a_tier_record = Column(String(20))
    vs_b_tier_record = Column(String(20))
    
    # Head to Head advantage
    h2h_advantages = Column(JSON)  # JSON with H2H vs specific teams
    
    updated_at = Column(DateTime, default=datetime.utcnow)


class EsportsPlayerPropsAnalysis(Base):
    """Esports player props analysis."""
    __tablename__ = "esports_player_props_analysis"
    
    id = Column(Integer, primary_key=True)
    player_name = Column(String(100))
    player_id = Column(String(50))
    team = Column(String(100))
    game = Column(String(50))
    
    prop_type = Column(String(50))  # "kills", "acs", "kd", "assists"
    line = Column(Float)
    
    # Overall
    season_avg = Column(Float)
    matches_played = Column(Integer)
    over_rate = Column(Float)
    
    # By Map (CS2/Valorant)
    by_map = Column(JSON)  # JSON {"inferno": {"avg": 18.5, "over_rate": 0.65}}
    
    # vs Team Tier
    vs_s_tier_avg = Column(Float)
    vs_s_tier_over_rate = Column(Float)
    vs_lower_tier_avg = Column(Float)
    vs_lower_tier_over_rate = Column(Float)
    
    # Home/LAN
    online_avg = Column(Float)
    online_over_rate = Column(Float)
    lan_avg = Column(Float)
    lan_over_rate = Column(Float)
    
    # By Agent/Champion
    by_agent = Column(JSON)  # JSON with per-agent stats
    
    # Form
    last_5_avg = Column(Float)
    last_5_over_rate = Column(Float)
    last_10_avg = Column(Float)
    last_10_over_rate = Column(Float)
    
    # After Results
    after_win_avg = Column(Float)
    after_loss_avg = Column(Float)
    after_3_win_streak_avg = Column(Float)
    after_3_loss_streak_avg = Column(Float)
    
    # vs Specific Teams
    vs_team_stats = Column(JSON)  # JSON with H2H stats
    
    updated_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# TENNIS MODELS
# ============================================================================

class TennisMatch(Base):
    """Tennis match model."""
    __tablename__ = "tennis_matches"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(100), unique=True, nullable=False)
    tour = Column(String(10))  # "atp", "wta"
    tournament = Column(String(200))
    tournament_category = Column(String(50))  # "grand_slam", "masters_1000", "atp_500", "atp_250"
    surface = Column(String(20))  # "hard", "clay", "grass"
    round = Column(String(50))  # "Final", "SF", "QF", "R16", "R32", "R64", "R128"
    match_date = Column(Date)
    
    player1 = Column(String(100))
    player2 = Column(String(100))
    player1_rank = Column(Integer)
    player2_rank = Column(Integer)
    player1_seed = Column(Integer)
    player2_seed = Column(Integer)
    
    winner = Column(String(100))
    score = Column(String(100))  # "6-4, 3-6, 7-5"
    
    # Sets
    player1_sets = Column(Integer)
    player2_sets = Column(Integer)
    
    # Games
    player1_games = Column(Integer)
    player2_games = Column(Integer)
    total_games = Column(Integer)
    
    # Tiebreaks
    tiebreaks_played = Column(Integer)
    
    # Set scores
    set1_p1 = Column(Integer)
    set1_p2 = Column(Integer)
    set2_p1 = Column(Integer)
    set2_p2 = Column(Integer)
    set3_p1 = Column(Integer)
    set3_p2 = Column(Integer)
    set4_p1 = Column(Integer)
    set4_p2 = Column(Integer)
    set5_p1 = Column(Integer)
    set5_p2 = Column(Integer)
    
    # Match duration
    duration_minutes = Column(Integer)
    
    # Stats
    player1_aces = Column(Integer)
    player2_aces = Column(Integer)
    player1_double_faults = Column(Integer)
    player2_double_faults = Column(Integer)
    player1_first_serve_pct = Column(Float)
    player2_first_serve_pct = Column(Float)
    player1_break_points_won = Column(Integer)
    player1_break_points_total = Column(Integer)
    player2_break_points_won = Column(Integer)
    player2_break_points_total = Column(Integer)
    
    # Odds
    player1_odds = Column(Float)
    player2_odds = Column(Float)
    total_games_line = Column(Float)
    over_odds = Column(Float)
    under_odds = Column(Float)
    
    # Betting Results
    over_20_5 = Column(Boolean)
    over_21_5 = Column(Boolean)
    over_22_5 = Column(Boolean)
    over_23_5 = Column(Boolean)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class TennisPlayerStats(Base):
    """Tennis player statistics."""
    __tablename__ = "tennis_player_stats"
    
    id = Column(Integer, primary_key=True)
    player_name = Column(String(100))
    player_id = Column(String(50))
    tour = Column(String(10))
    season = Column(String(20))
    
    # Rankings
    current_rank = Column(Integer)
    peak_rank = Column(Integer)
    
    # Record
    matches_played = Column(Integer)
    matches_won = Column(Integer)
    win_rate = Column(Float)
    
    # By Surface
    hard_played = Column(Integer)
    hard_won = Column(Integer)
    hard_win_rate = Column(Float)
    clay_played = Column(Integer)
    clay_won = Column(Integer)
    clay_win_rate = Column(Float)
    grass_played = Column(Integer)
    grass_won = Column(Integer)
    grass_win_rate = Column(Float)
    
    # By Tournament Category
    grand_slam_played = Column(Integer)
    grand_slam_won = Column(Integer)
    masters_played = Column(Integer)
    masters_won = Column(Integer)
    
    # Serve Stats
    aces_per_match = Column(Float)
    double_faults_per_match = Column(Float)
    first_serve_pct = Column(Float)
    first_serve_won_pct = Column(Float)
    second_serve_won_pct = Column(Float)
    service_games_won_pct = Column(Float)
    
    # Return Stats
    return_games_won_pct = Column(Float)
    break_points_converted_pct = Column(Float)
    
    # Tiebreaks
    tiebreaks_played = Column(Integer)
    tiebreaks_won = Column(Integer)
    tiebreak_win_rate = Column(Float)
    
    # Sets
    sets_played = Column(Integer)
    sets_won = Column(Integer)
    
    # Games
    avg_games_per_match = Column(Float)
    
    # vs Rankings
    vs_top10_record = Column(String(20))
    vs_top10_win_rate = Column(Float)
    vs_top50_record = Column(String(20))
    vs_top100_record = Column(String(20))
    
    # Form
    form = Column(String(10))
    current_streak = Column(String(10))
    
    updated_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# AGGREGATE ANALYSIS MODELS
# ============================================================================

class BettingPattern(Base):
    """Identified betting patterns."""
    __tablename__ = "betting_patterns"
    
    id = Column(Integer, primary_key=True)
    sport = Column(String(50))
    pattern_type = Column(String(50))  # "team_ats", "player_prop", "total_ou"
    entity = Column(String(100))  # Team or player name
    
    # Pattern Details
    condition = Column(String(200))  # "after_loss", "vs_top_defense", "home_favorite"
    line_type = Column(String(50))  # "spread", "total", "prop"
    line = Column(Float)
    
    # Stats
    sample_size = Column(Integer)
    hits = Column(Integer)
    misses = Column(Integer)
    hit_rate = Column(Float)
    
    # ROI
    avg_odds = Column(Float)
    roi = Column(Float)
    units_profit = Column(Float)
    
    # Confidence
    confidence_level = Column(String(20))  # "HIGH", "MEDIUM", "LOW"
    z_score = Column(Float)
    
    # Time Period
    period = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    
    updated_at = Column(DateTime, default=datetime.utcnow)


class ValueBetHistory(Base):
    """Value bets identified and tracked."""
    __tablename__ = "value_bets_history"
    
    id = Column(Integer, primary_key=True)
    
    # Bet Details
    sport = Column(String(50))
    match_id = Column(String(100))
    match_description = Column(String(300))
    bet_type = Column(String(50))  # "spread", "total", "prop", "moneyline"
    selection = Column(String(200))  # "Lakers -3.5", "Over 218.5", "LeBron Over 25.5 pts"
    
    # Value Calculation
    our_probability = Column(Float)
    implied_probability = Column(Float)
    edge = Column(Float)  # Expected value
    odds = Column(Float)
    
    # Analysis Used
    factors_used = Column(JSON)  # JSON list of factors
    confidence_score = Column(Float)
    
    # Result
    bet_placed = Column(Boolean)
    stake = Column(Float)
    result = Column(String(20))  # "WIN", "LOSS", "PUSH", "PENDING"
    profit_loss = Column(Float)
    
    # Timestamps
    identified_at = Column(DateTime, default=datetime.utcnow)
    match_time = Column(DateTime)
    settled_at = Column(DateTime)
