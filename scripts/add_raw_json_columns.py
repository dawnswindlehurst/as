"""Migration script to add raw enrichment JSON columns."""
import sys
from sqlalchemy import text, inspect
from database.db import get_db_session, engine
from utils.logger import log


def migrate():
    """Add JSON/JSONB columns for storing raw API data and tennis metrics."""
    log.info("="*60)
    log.info("🔧 DATABASE MIGRATION: Adding Raw JSON Columns")
    log.info("="*60)
    
    db = get_db_session()
    dialect = engine.dialect.name
    log.info(f"Database dialect: {dialect}")
    
    try:
        if dialect == 'postgresql':
            # PostgreSQL supports JSONB and IF NOT EXISTS
            log.info("Adding match_stats_raw JSONB column...")
            db.execute(text("""
                ALTER TABLE scorealarm_matches 
                ADD COLUMN IF NOT EXISTS match_stats_raw JSONB
            """))
            log.info("✅ match_stats_raw column added")
            
            log.info("Adding live_events_raw JSONB column...")
            db.execute(text("""
                ALTER TABLE scorealarm_matches 
                ADD COLUMN IF NOT EXISTS live_events_raw JSONB
            """))
            log.info("✅ live_events_raw column added")

            log.info("Adding tennis_match_metrics JSONB column...")
            db.execute(text("""
                ALTER TABLE scorealarm_matches
                ADD COLUMN IF NOT EXISTS tennis_match_metrics JSONB
            """))
            log.info("✅ tennis_match_metrics column added")

            log.info("Adding tennis_period_metrics JSONB column...")
            db.execute(text("""
                ALTER TABLE scorealarm_matches
                ADD COLUMN IF NOT EXISTS tennis_period_metrics JSONB
            """))
            log.info("✅ tennis_period_metrics column added")
            
        elif dialect == 'sqlite':
            # SQLite doesn't support IF NOT EXISTS in ALTER TABLE
            # Check if columns exist first
            log.info("Checking existing columns in SQLite...")
            
            # Try to add match_stats_raw
            try:
                db.execute(text("""
                    ALTER TABLE scorealarm_matches 
                    ADD COLUMN match_stats_raw TEXT
                """))
                log.info("✅ match_stats_raw column added")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    log.info("⚠️  match_stats_raw column already exists")
                else:
                    raise
            
            # Try to add live_events_raw
            try:
                db.execute(text("""
                    ALTER TABLE scorealarm_matches 
                    ADD COLUMN live_events_raw TEXT
                """))
                log.info("✅ live_events_raw column added")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    log.info("⚠️  live_events_raw column already exists")
                else:
                    raise

            try:
                db.execute(text("""
                    ALTER TABLE scorealarm_matches
                    ADD COLUMN tennis_match_metrics TEXT
                """))
                log.info("✅ tennis_match_metrics column added")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    log.info("⚠️  tennis_match_metrics column already exists")
                else:
                    raise

            try:
                db.execute(text("""
                    ALTER TABLE scorealarm_matches
                    ADD COLUMN tennis_period_metrics TEXT
                """))
                log.info("✅ tennis_period_metrics column added")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    log.info("⚠️  tennis_period_metrics column already exists")
                else:
                    raise
        else:
            log.warning(f"⚠️  Unsupported database dialect: {dialect}")
            log.info("Attempting to add columns with generic SQL...")
            
            # Generic approach
            try:
                db.execute(text("""
                    ALTER TABLE scorealarm_matches 
                    ADD COLUMN match_stats_raw TEXT
                """))
                log.info("✅ match_stats_raw column added")
            except Exception as e:
                log.warning(f"⚠️  Could not add match_stats_raw: {e}")
            
            try:
                db.execute(text("""
                    ALTER TABLE scorealarm_matches 
                    ADD COLUMN live_events_raw TEXT
                """))
                log.info("✅ live_events_raw column added")
            except Exception as e:
                log.warning(f"⚠️  Could not add live_events_raw: {e}")

            try:
                db.execute(text("""
                    ALTER TABLE scorealarm_matches
                    ADD COLUMN tennis_match_metrics TEXT
                """))
                log.info("✅ tennis_match_metrics column added")
            except Exception as e:
                log.warning(f"⚠️  Could not add tennis_match_metrics: {e}")

            try:
                db.execute(text("""
                    ALTER TABLE scorealarm_matches
                    ADD COLUMN tennis_period_metrics TEXT
                """))
                log.info("✅ tennis_period_metrics column added")
            except Exception as e:
                log.warning(f"⚠️  Could not add tennis_period_metrics: {e}")
        

        inspector = inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("scorealarm_matches")}
        for required in ("match_stats_raw", "live_events_raw", "tennis_match_metrics", "tennis_period_metrics"):
            if required in cols:
                log.info(f"✅ Column available after migration: {required}")
            else:
                log.warning(f"⚠️ Column missing after migration: {required}")

        # Commit changes
        db.commit()
        
        log.info("="*60)
        log.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
        log.info("="*60)
        
    except Exception as e:
        log.error(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        log.error(f"Migration error: {e}")
        sys.exit(1)
