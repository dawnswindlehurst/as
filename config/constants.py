"""Constants used throughout the application."""

# Games
SUPPORTED_GAMES = ["CS2", "LoL", "Dota2", "Valorant"]

# Bookmakers - Traditional
TRADITIONAL_BOOKMAKERS = ["Pinnacle", "bet365", "Betfair", "Rivalry"]

# Bookmakers - Crypto
CRYPTO_BOOKMAKERS = [
    "Stake",
    "Cloudbet",
    "Thunderpick",
    "Roobet",
    "Rollbit",
    "Duelbits",
    "Bitsler",
]

ALL_BOOKMAKERS = TRADITIONAL_BOOKMAKERS + CRYPTO_BOOKMAKERS

# Markets
MARKET_TYPES = [
    "match_winner",      # Moneyline
    "handicap",          # Spread
    "total_maps",        # Over/Under maps
    "total_rounds",      # Over/Under rounds
    "first_blood",       # First kill/objective
]

# Confidence Ranges (5% intervals from 55% to 100%)
CONFIDENCE_RANGES = [
    (0.55, 0.60),
    (0.60, 0.65),
    (0.65, 0.70),
    (0.70, 0.75),
    (0.75, 0.80),
    (0.80, 0.85),
    (0.85, 0.90),
    (0.90, 0.95),
    (0.95, 1.00),
]

# Model types
MODEL_TYPES = [
    "elo",
    "glicko",
    "logistic",
    "xgboost",
    "poisson",
    "ensemble",
]

# Bet statuses
BET_STATUS_PENDING = "pending"
BET_STATUS_WON = "won"
BET_STATUS_LOST = "lost"
BET_STATUS_VOID = "void"
BET_STATUS_CASHOUT = "cashout"

# Feature decay parameters
DECAY_HALF_LIFE_DAYS = 90  # Features decay with 90-day half-life

# Map pools (CS2 example)
CS2_MAP_POOL = [
    "Mirage",
    "Inferno",
    "Nuke",
    "Overpass",
    "Vertigo",
    "Ancient",
    "Anubis",
]

# Valorant map pool
VALORANT_MAP_POOL = [
    "Ascent",
    "Bind",
    "Haven",
    "Split",
    "Icebox",
    "Breeze",
    "Fracture",
    "Pearl",
    "Lotus",
    "Sunset",
]

# Timing windows for odds analysis (hours before match)
TIMING_WINDOWS = [
    (24, "24h"),
    (12, "12h"),
    (6, "6h"),
    (3, "3h"),
    (1, "1h"),
    (0, "closing"),
]

# ELO parameters
ELO_K_FACTOR = 32
ELO_INITIAL_RATING = 1500

# Glicko parameters
GLICKO_INITIAL_RATING = 1500
GLICKO_INITIAL_RD = 350
GLICKO_INITIAL_SIGMA = 0.06

# Minimum sample sizes for analysis
MIN_MATCHES_FOR_RATING = 10
MIN_MATCHES_FOR_H2H = 3
MIN_BETS_FOR_ANALYSIS = 20
