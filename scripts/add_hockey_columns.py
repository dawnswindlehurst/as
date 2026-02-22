"""Migration script to add ice hockey-specific match columns for value bet analysis."""
import sys
from sqlalchemy import text, inspect
from database.db import get_db_session, engine
from utils.logger import log


# Columns to add: (name, postgresql_type, sqlite_type)
NEW_COLUMNS = [
    # Score by period
    ("period1_home", "INTEGER", "INTEGER"),
    ("period1_away", "INTEGER", "INTEGER"),
    ("period2_home", "INTEGER", "INTEGER"),
    ("period2_away", "INTEGER", "INTEGER"),
    ("period3_home", "INTEGER", "INTEGER"),
    ("period3_away", "INTEGER", "INTEGER"),
    ("overtime_home", "INTEGER", "INTEGER"),
    ("overtime_away", "INTEGER", "INTEGER"),
    ("shootout_home", "INTEGER", "INTEGER"),
    ("shootout_away", "INTEGER", "INTEGER"),
    # Main statistics
    ("puck_possession_home", "FLOAT", "REAL"),
    ("puck_possession_away", "FLOAT", "REAL"),
    ("saves_home", "INTEGER", "INTEGER"),
    ("saves_away", "INTEGER", "INTEGER"),
    # Power play
    ("power_plays_home", "INTEGER", "INTEGER"),
    ("power_plays_away", "INTEGER", "INTEGER"),
    ("power_play_goals_home", "INTEGER", "INTEGER"),
    ("power_play_goals_away", "INTEGER", "INTEGER"),
    ("short_handed_goals_home", "INTEGER", "INTEGER"),
    ("short_handed_goals_away", "INTEGER", "INTEGER"),
    # Penalties
    ("penalties_home", "INTEGER", "INTEGER"),
    ("penalties_away", "INTEGER", "INTEGER"),
    ("penalty_minutes_home", "INTEGER", "INTEGER"),
    ("penalty_minutes_away", "INTEGER", "INTEGER"),
    # Calculated metrics
    ("save_percentage_home", "FLOAT", "REAL"),
    ("save_percentage_away", "FLOAT", "REAL"),
    ("shooting_percentage_home", "FLOAT", "REAL"),
    ("shooting_percentage_away", "FLOAT", "REAL"),
    # Goal events (raw)
    ("goal_scorers_raw", "JSONB", "TEXT"),
]


def migrate():
    """Add ice hockey columns to scorealarm_matches table."""
    log.info("=" * 60)
    log.info("🔧 DATABASE MIGRATION: Adding Hockey Detail Columns")
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
