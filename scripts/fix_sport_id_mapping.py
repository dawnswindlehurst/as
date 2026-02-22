"""Fix sport_id mapping in existing data.

This script corrects the sport_id values in matches, tournaments, and teams
that were incorrectly saved using the Superbet API ID instead of the database ID.
"""
from database.db import get_db_session
from database.scorealarm_models import (
    ScorealarmSport, ScorealarmMatch, ScorealarmTournament, ScorealarmTeam
)


def fix_sport_ids():
    """Fix sport_id mapping in all affected tables."""
    db = get_db_session()
    
    try:
        # Create mapping: superbet_id -> db_id
        sports = db.query(ScorealarmSport).all()
        superbet_to_db = {s.superbet_id: s.id for s in sports}
        
        print("=== MAPPING ===")
        for superbet_id, db_id in superbet_to_db.items():
            sport = db.query(ScorealarmSport).filter(ScorealarmSport.id == db_id).first()
            print(f"Superbet {superbet_id} -> DB {db_id} ({sport.name})")
        
        # Fix matches
        print("\n=== FIXING MATCHES ===")
        for superbet_id, db_id in superbet_to_db.items():
            if superbet_id != db_id:  # Only fix if different
                count = db.query(ScorealarmMatch).filter(
                    ScorealarmMatch.sport_id == superbet_id
                ).update({ScorealarmMatch.sport_id: db_id})
                if count > 0:
                    print(f"Matches: superbet_id {superbet_id} -> db_id {db_id}: {count} records")
        
        # Fix tournaments
        print("\n=== FIXING TOURNAMENTS ===")
        for superbet_id, db_id in superbet_to_db.items():
            if superbet_id != db_id:
                count = db.query(ScorealarmTournament).filter(
                    ScorealarmTournament.sport_id == superbet_id
                ).update({ScorealarmTournament.sport_id: db_id})
                if count > 0:
                    print(f"Tournaments: superbet_id {superbet_id} -> db_id {db_id}: {count} records")
        
        # Fix teams
        print("\n=== FIXING TEAMS ===")
        for superbet_id, db_id in superbet_to_db.items():
            if superbet_id != db_id:
                count = db.query(ScorealarmTeam).filter(
                    ScorealarmTeam.sport_id == superbet_id
                ).update({ScorealarmTeam.sport_id: db_id})
                if count > 0:
                    print(f"Teams: superbet_id {superbet_id} -> db_id {db_id}: {count} records")
        
        db.commit()
        print("\n✅ Migration completed!")
    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    fix_sport_ids()
