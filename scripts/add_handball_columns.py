"""Migration script to add handball-specific match columns for value bet analysis."""
import sys
from sqlalchemy import text, inspect
from database.db import get_db_session, engine
from utils.logger import log


# Columns to add: (name, postgresql_type, sqlite_type)
NEW_COLUMNS = [
    # Score by half
    ("first_half_home", "INTEGER", "INTEGER"),
    ("first_half_away", "INTEGER", "INTEGER"),
    ("second_half_home", "INTEGER", "INTEGER"),
    ("second_half_away", "INTEGER", "INTEGER"),
    ("overtime1_home", "INTEGER", "INTEGER"),
    ("overtime1_away", "INTEGER", "INTEGER"),
    ("overtime2_home", "INTEGER", "INTEGER"),
    ("overtime2_away", "INTEGER", "INTEGER"),
    # Shots
    ("shots_off_goal_home", "INTEGER", "INTEGER"),
    ("shots_off_goal_away", "INTEGER", "INTEGER"),
    ("shots_blocked_home", "INTEGER", "INTEGER"),
    ("shots_blocked_away", "INTEGER", "INTEGER"),
    # Goalkeeper
    ("goalkeeper_saves_home", "INTEGER", "INTEGER"),
    ("goalkeeper_saves_away", "INTEGER", "INTEGER"),
    # Goal types
    ("breakthrough_goals_home", "INTEGER", "INTEGER"),
    ("breakthrough_goals_away", "INTEGER", "INTEGER"),
    ("fast_break_goals_home", "INTEGER", "INTEGER"),
    ("fast_break_goals_away", "INTEGER", "INTEGER"),
    ("pivot_goals_home", "INTEGER", "INTEGER"),
    ("pivot_goals_away", "INTEGER", "INTEGER"),
    ("penalty_goals_home", "INTEGER", "INTEGER"),
    ("penalty_goals_away", "INTEGER", "INTEGER"),
    # Discipline
    ("yellow_cards_home", "INTEGER", "INTEGER"),
    ("yellow_cards_away", "INTEGER", "INTEGER"),
    ("red_cards_home", "INTEGER", "INTEGER"),
    ("red_cards_away", "INTEGER", "INTEGER"),
    ("suspensions_home", "INTEGER", "INTEGER"),
    ("suspensions_away", "INTEGER", "INTEGER"),
    ("suspension_minutes_home", "INTEGER", "INTEGER"),
    ("suspension_minutes_away", "INTEGER", "INTEGER"),
    # Other stats
    ("penalties_against_home", "INTEGER", "INTEGER"),
    ("penalties_against_away", "INTEGER", "INTEGER"),
    ("timeouts_home", "INTEGER", "INTEGER"),
    ("timeouts_away", "INTEGER", "INTEGER"),
    # Calculated metrics
    ("goals_per_half_home", "JSONB", "TEXT"),
    ("goals_per_half_away", "JSONB", "TEXT"),
]


def migrate():
    """Add handball columns to scorealarm_matches table."""
    log.info("=" * 60)
    log.info("🔧 DATABASE MIGRATION: Adding Handball Detail Columns")
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
