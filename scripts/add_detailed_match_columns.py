"""Migration script to add detailed match data columns for value bet analysis."""
import sys
from sqlalchemy import text, inspect
from database.db import get_db_session, engine
from utils.logger import log


# Columns to add: (name, postgresql_type, sqlite_type)
NEW_COLUMNS = [
    # Raw data
    ("match_statistics_raw", "JSONB", "TEXT"),
    ("score_trend_raw", "JSONB", "TEXT"),
    # Game metadata
    ("venue_id", "INTEGER", "INTEGER"),
    ("coverage_level", "JSONB", "TEXT"),
    ("number_of_periods", "INTEGER", "INTEGER"),
    ("period_duration", "INTEGER", "INTEGER"),
    ("leading_team", "INTEGER", "INTEGER"),
    # Tennis-specific
    ("ground_type", "INTEGER", "INTEGER"),
    ("team1_seed", "INTEGER", "INTEGER"),
    ("team2_seed", "INTEGER", "INTEGER"),
    ("tournament_round", "VARCHAR(100)", "TEXT"),
    # Basketball shooting
    ("ft_made_home", "INTEGER", "INTEGER"),
    ("ft_attempted_home", "INTEGER", "INTEGER"),
    ("ft_made_away", "INTEGER", "INTEGER"),
    ("ft_attempted_away", "INTEGER", "INTEGER"),
    ("fg2_made_home", "INTEGER", "INTEGER"),
    ("fg2_attempted_home", "INTEGER", "INTEGER"),
    ("fg2_made_away", "INTEGER", "INTEGER"),
    ("fg2_attempted_away", "INTEGER", "INTEGER"),
    ("fg3_made_home", "INTEGER", "INTEGER"),
    ("fg3_attempted_home", "INTEGER", "INTEGER"),
    ("fg3_made_away", "INTEGER", "INTEGER"),
    ("fg3_attempted_away", "INTEGER", "INTEGER"),
    # Basketball box score
    ("rebounds_home", "INTEGER", "INTEGER"),
    ("rebounds_away", "INTEGER", "INTEGER"),
    ("assists_home", "INTEGER", "INTEGER"),
    ("assists_away", "INTEGER", "INTEGER"),
    ("turnovers_home", "INTEGER", "INTEGER"),
    ("turnovers_away", "INTEGER", "INTEGER"),
    ("steals_home", "INTEGER", "INTEGER"),
    ("steals_away", "INTEGER", "INTEGER"),
    ("blocks_home", "INTEGER", "INTEGER"),
    ("blocks_away", "INTEGER", "INTEGER"),
    ("fouls_home", "INTEGER", "INTEGER"),
    ("fouls_away", "INTEGER", "INTEGER"),
    # Basketball game flow
    ("biggest_lead_home", "INTEGER", "INTEGER"),
    ("biggest_lead_away", "INTEGER", "INTEGER"),
    ("time_in_lead_home", "VARCHAR(10)", "TEXT"),
    ("time_in_lead_away", "VARCHAR(10)", "TEXT"),
    ("lead_changes", "INTEGER", "INTEGER"),
]


def migrate():
    """Add detailed match data columns to scorealarm_matches table."""
    log.info("=" * 60)
    log.info("🔧 DATABASE MIGRATION: Adding Detailed Match Columns")
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
