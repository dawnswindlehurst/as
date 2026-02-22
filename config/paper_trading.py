"""Paper trading configuration."""

# Paper trading setup
PAPER_TRADING_CONFIG = {
    'stake': 10.00,  # R$ 10,00 per bet
    'currency': 'BRL',
    'duration': '1_week_to_1_month',
    'initial_bankroll': 1000.00,  # R$ 1,000.00 initial (simulated)
    'min_edge': 0.03,  # 3% minimum edge
    'min_confidence': 0.55,  # 55% minimum confidence
}

# Sports to test
SPORTS = {
    'CS2': {'sport_id': 55, 'name': 'Counter-Strike 2'},
    'Dota2': {'sport_id': 54, 'name': 'Dota 2'},
    'Valorant': {'sport_id': 153, 'name': 'Valorant'},
    'LoL': {'sport_id': 39, 'name': 'League of Legends'},
    # Traditional sports for comparison
    'Tennis': {'sport_id': 4, 'name': 'Tênis'},
    'Football': {'sport_id': 5, 'name': 'Futebol'},
}

# Markets to test
MARKETS = {
    # eSports Markets
    'match_winner': 'Vencedor da Partida (ML)',
    'map_handicap': 'Handicap de Mapas',
    'total_maps': 'Total de Mapas',
    'map_winner': 'Vencedor do Mapa',
    'round_handicap': 'Handicap de Rounds',
    'total_rounds': 'Total de Rounds',
    'first_blood': 'First Blood',
    'first_tower': 'First Tower',
    'total_kills': 'Total de Kills',
    
    # Tennis Markets
    'set_handicap': 'Handicap de Sets',
    'total_sets': 'Total de Sets',
    'game_handicap': 'Handicap de Games',
    'total_games': 'Total de Games',
    
    # Football Markets
    '1x2': 'Resultado Final',
    'draw_no_bet': 'Draw No Bet',
    'asian_handicap': 'Handicap Asiático',
    'over_under_goals': 'Over/Under Gols',
    'btts': 'Ambas Marcam',
}

# Models to test
MODELS = ['elo', 'glicko', 'logistic', 'xgboost', 'poisson', 'ensemble']

# Other dimensions for analysis
OTHER_DIMENSIONS = {
    'by_weekday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'by_hour': ['Morning (6-12)', 'Afternoon (12-18)', 'Evening (18-24)', 'Night (0-6)'],
    'by_tier': ['S-Tier', 'A-Tier', 'B-Tier', 'C-Tier'],
    'by_region': ['NA', 'EU', 'LATAM', 'APAC', 'BR'],
    'by_format': ['BO1', 'BO2', 'BO3', 'BO5'],
    'by_favorite': ['Favorite', 'Underdog'],
    'by_edge': ['3-5%', '5-8%', '8-12%', '12%+'],
}
