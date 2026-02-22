"""Oracle Cloud specific configuration."""
import os
from typing import Dict

# Oracle deployment flag
ORACLE_DEPLOYMENT = os.getenv("ORACLE_DEPLOYMENT", "false").lower() == "true"

# Collection settings
COLLECTION_INTERVAL_HOURS = int(os.getenv("COLLECTION_INTERVAL_HOURS", "2"))
INITIAL_COLLECTION_DAYS = int(os.getenv("INITIAL_COLLECTION_DAYS", "180"))
ENABLE_INITIAL_COLLECTION = os.getenv("ENABLE_INITIAL_COLLECTION", "true").lower() == "true"

# Odds matching settings
ODDS_MATCH_TIME_WINDOW_HOURS = int(os.getenv("ODDS_MATCH_TIME_WINDOW_HOURS", "24"))

# Rate limiting (requests per minute)
RATE_LIMITS: Dict[str, int] = {
    "traditional_sports": int(os.getenv("TRADITIONAL_SPORTS_RATE_LIMIT", "10")),
    "hltv": int(os.getenv("HLTV_RATE_LIMIT", "5")),
    "vlr": int(os.getenv("VLR_RATE_LIMIT", "5")),
    "opendota": int(os.getenv("OPENDOTA_RATE_LIMIT", "10")),
    "superbet": int(os.getenv("SUPERBET_RATE_LIMIT", "20")),
}

# Resource limits (optimized for 12GB RAM)
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))

# Notification settings
NOTIFY_ON_COLLECTION_COMPLETE = os.getenv("NOTIFY_ON_COLLECTION_COMPLETE", "true").lower() == "true"
NOTIFY_ON_ERROR = os.getenv("NOTIFY_ON_ERROR", "true").lower() == "true"

# PostgreSQL connection pool settings (for Oracle deployment)
if ORACLE_DEPLOYMENT:
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
else:
    DB_POOL_SIZE = 5
    DB_MAX_OVERFLOW = 10
    DB_POOL_TIMEOUT = 30
    DB_POOL_RECYCLE = 3600
