"""Script to reset database and create new schema."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import MetaData
from database.db import engine
from database.base import Base

# Import all models to register them with the new Base
from database.core_models import Sport, Tournament, Season, Team, Player
from database.match_models import Match, MatchScore
from database.football_models import FootballStats
from database.basketball_models import BasketballStats
from database.tennis_models import TennisStats
from database.odds_models import OddsHistory, PlayerProp
from database.player_stats_models import PlayerGameLog, PlayerSeasonStats
from database.esports_models import EsportsStats


def reset_database():
    """Drop all tables and recreate with new schema."""
    print("=" * 60)
    print("⚠️  DATABASE RESET")
    print("=" * 60)

    confirm = input("This will DELETE ALL DATA. Type 'YES' to confirm: ")
    if confirm != "YES":
        print("Aborted.")
        return

    print("\n🗑️  Dropping all tables...")
    # Reflect all existing tables to ensure even legacy tables are dropped
    reflected_meta = MetaData()
    reflected_meta.reflect(bind=engine)
    reflected_meta.drop_all(bind=engine)

    print("✅ Creating new tables...")
    Base.metadata.create_all(bind=engine)

    print("\n📊 New tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"   - {table.name}")

    print("\n✅ Database reset complete!")
    print("=" * 60)


if __name__ == "__main__":
    reset_database()
