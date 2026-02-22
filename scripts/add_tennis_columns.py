"""Migration script to add detailed tennis match columns for value bet analysis."""
import sys
from sqlalchemy import text, inspect
from database.db import get_db_session, engine
from utils.logger import log


# Columns to add: (name, postgresql_type, sqlite_type)
NEW_COLUMNS = [
    # Tournament/competition info
    ("prize_money", "INTEGER", "INTEGER"),
    ("prize_currency", "VARCHAR(10)", "TEXT"),
    # Set durations
    ("set1_duration", "INTEGER", "INTEGER"),
    ("set2_duration", "INTEGER", "INTEGER"),
    ("set3_duration", "INTEGER", "INTEGER"),
    ("set4_duration", "INTEGER", "INTEGER"),
    ("set5_duration", "INTEGER", "INTEGER"),
    ("total_duration", "INTEGER", "INTEGER"),
    # Serve statistics
    ("aces_home", "INTEGER", "INTEGER"),
    ("aces_away", "INTEGER", "INTEGER"),
    ("double_faults_home", "INTEGER", "INTEGER"),
    ("double_faults_away", "INTEGER", "INTEGER"),
    ("first_serve_pct_home", "FLOAT", "REAL"),
    ("first_serve_pct_away", "FLOAT", "REAL"),
    ("first_serve_won_pct_home", "FLOAT", "REAL"),
    ("first_serve_won_pct_away", "FLOAT", "REAL"),
    ("second_serve_won_pct_home", "FLOAT", "REAL"),
    ("second_serve_won_pct_away", "FLOAT", "REAL"),
    # Break points
    ("break_points_faced_home", "INTEGER", "INTEGER"),
    ("break_points_saved_home", "INTEGER", "INTEGER"),
    ("break_points_faced_away", "INTEGER", "INTEGER"),
    ("break_points_saved_away", "INTEGER", "INTEGER"),
    ("break_points_converted_home", "INTEGER", "INTEGER"),
    ("break_points_converted_away", "INTEGER", "INTEGER"),
    # Service games
    ("service_games_won_home", "INTEGER", "INTEGER"),
    ("service_games_total_home", "INTEGER", "INTEGER"),
    ("service_games_won_away", "INTEGER", "INTEGER"),
    ("service_games_total_away", "INTEGER", "INTEGER"),
    # Total games (for over/under)
    ("total_games", "INTEGER", "INTEGER"),
    # Point by point raw data
    ("point_by_point_raw", "JSONB", "TEXT"),
]


def migrate():
    """Add detailed tennis columns to scorealarm_matches table."""
    log.info("=" * 60)
    log.info("🔧 DATABASE MIGRATION: Adding Tennis Detail Columns")
    log.info("=" * 60)

    db = get_db_session()
    dialect = engine.dialect.name
    log.info(f"Database dialect: {dialect}")

    try:
        inspector = inspect(engine)
        existing_cols = {c["name"] for c in inspector.get_columns("scorealarm_matches")}

        added = 0
        skipped = 0

        for col_name, pg_type, sqlite_type in NEW_COLUMNS:
            if col_name in existing_cols:
                log.info(f"⚠️  Column already exists, skipping: {col_name}")
                skipped += 1
                continue

            col_type = pg_type if dialect == "postgresql" else sqlite_type

            if dialect == "postgresql":
                sql = f"ALTER TABLE scorealarm_matches ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
            else:
                sql = f"ALTER TABLE scorealarm_matches ADD COLUMN {col_name} {col_type}"

            try:
                db.execute(text(sql))
                log.info(f"✅ Added column: {col_name} ({col_type})")
                added += 1
            except Exception as exc:
                err = str(exc).lower()
                if "duplicate column" in err or "already exists" in err:
                    log.info(f"⚠️  Column already exists: {col_name}")
                    skipped += 1
                else:
                    raise

        db.commit()

        # Verify
        inspector2 = inspect(engine)
        final_cols = {c["name"] for c in inspector2.get_columns("scorealarm_matches")}
        missing = [col for col, _, _ in NEW_COLUMNS if col not in final_cols]
        if missing:
            log.warning(f"⚠️  Columns still missing after migration: {missing}")
        else:
            log.info(f"✅ All {len(NEW_COLUMNS)} columns verified in table")

        log.info("=" * 60)
        log.info(f"✅ MIGRATION COMPLETED: {added} added, {skipped} already existed")
        log.info("=" * 60)

    except Exception as exc:
        log.error(f"❌ Migration failed: {exc}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        migrate()
    except Exception as exc:
        log.error(f"Migration error: {exc}")
        sys.exit(1)
