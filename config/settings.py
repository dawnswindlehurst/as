"""Application settings and configuration."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///capivara_bet.db")

# Oracle Cloud deployment
ORACLE_DEPLOYMENT = os.getenv("ORACLE_DEPLOYMENT", "false").lower() == "true"

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Scrapers
HLTV_BASE_URL = os.getenv("HLTV_BASE_URL", "https://www.hltv.org")
VLR_BASE_URL = os.getenv("VLR_BASE_URL", "https://www.vlr.gg")
ORACLE_ELIXIR_BASE_URL = os.getenv("ORACLE_ELIXIR_BASE_URL", "https://oracleselixir.com")
OPENDOTA_API_URL = os.getenv("OPENDOTA_API_URL", "https://api.opendota.com/api")

# Paper Trading
PAPER_TRADING_STAKE = float(os.getenv("PAPER_TRADING_STAKE", "100"))
PAPER_TRADING_CURRENCY = os.getenv("PAPER_TRADING_CURRENCY", "BRL")

# Model Settings
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.55"))
MIN_EDGE = float(os.getenv("MIN_EDGE", "0.03"))
MAX_EDGE = float(os.getenv("MAX_EDGE", "0.20"))

# Kelly Criterion
KELLY_FRACTION = float(os.getenv("KELLY_FRACTION", "0.25"))

# Scheduler
FETCH_ODDS_INTERVAL_MINUTES = int(os.getenv("FETCH_ODDS_INTERVAL_MINUTES", "15"))
GENERATE_BETS_INTERVAL_MINUTES = int(os.getenv("GENERATE_BETS_INTERVAL_MINUTES", "30"))
FETCH_RESULTS_INTERVAL_MINUTES = int(os.getenv("FETCH_RESULTS_INTERVAL_MINUTES", "60"))
DAILY_REPORT_HOUR = int(os.getenv("DAILY_REPORT_HOUR", "23"))

# Collection settings (Oracle Cloud)
COLLECTION_INTERVAL_HOURS = int(os.getenv("COLLECTION_INTERVAL_HOURS", "2"))
INITIAL_COLLECTION_DAYS = int(os.getenv("INITIAL_COLLECTION_DAYS", "180"))
ENABLE_INITIAL_COLLECTION = os.getenv("ENABLE_INITIAL_COLLECTION", "true").lower() == "true"

# Debug
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Superbet API
SUPERBET_BASE_URL = os.getenv(
    "SUPERBET_BASE_URL",
    "https://production-superbet-offer-br.freetls.fastly.net/v2/pt-BR"
)
SUPERBET_SPORT_IDS = {
    'cs2': 55,          # Counter-Strike 2
    'dota2': 54,        # Dota 2
    'valorant': 153,    # Valorant
    'lol': 39,          # League of Legends
    'tennis': 4,        # Tênis
    'football': 5,      # Futebol
}

# Cache Settings
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour default
TOURNAMENT_CACHE_TTL = int(os.getenv("TOURNAMENT_CACHE_TTL", "3600"))  # 1 hour

# Dashboard Settings
DASHBOARD_AUTO_REFRESH = os.getenv("DASHBOARD_AUTO_REFRESH", "False").lower() == "true"
DASHBOARD_REFRESH_INTERVAL = int(os.getenv("DASHBOARD_REFRESH_INTERVAL", "30"))  # seconds
DARK_MODE_DEFAULT = os.getenv("DARK_MODE_DEFAULT", "False").lower() == "true"
