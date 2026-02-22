"""Migration script to add columns for water polo, table tennis, rugby, and bandy."""
import sys
from sqlalchemy import text, inspect
from database.db import get_db_session, engine
from utils.logger import log


# Columns to add: (name, postgresql_type, sqlite_type)
NEW_COLUMNS = [
    # Water Polo - Score by quarter (4 quarters of 8 min)
    ("wp_quarter1_home", "INTEGER", "INTEGER"),
    ("wp_quarter1_away", "INTEGER", "INTEGER"),
    ("wp_quarter2_home", "INTEGER", "INTEGER"),
    ("wp_quarter2_away", "INTEGER", "INTEGER"),
    ("wp_quarter3_home", "INTEGER", "INTEGER"),
    ("wp_quarter3_away", "INTEGER", "INTEGER"),
    ("wp_quarter4_home", "INTEGER", "INTEGER"),
    ("wp_quarter4_away", "INTEGER", "INTEGER"),
    # Water Polo - Half totals
    ("wp_first_half_home", "INTEGER", "INTEGER"),
    ("wp_first_half_away", "INTEGER", "INTEGER"),
    ("wp_second_half_home", "INTEGER", "INTEGER"),
    ("wp_second_half_away", "INTEGER", "INTEGER"),
    # Water Polo - Calculated metrics
    ("wp_total_goals_home", "INTEGER", "INTEGER"),
    ("wp_total_goals_away", "INTEGER", "INTEGER"),
    ("wp_goals_per_quarter_home", "FLOAT", "REAL"),
    ("wp_goals_per_quarter_away", "FLOAT", "REAL"),

    # Table Tennis - Sets won
    ("tt_sets_home", "INTEGER", "INTEGER"),
    ("tt_sets_away", "INTEGER", "INTEGER"),
    # Table Tennis - Points per set (up to 7 sets)
    ("tt_set1_home", "INTEGER", "INTEGER"),
    ("tt_set1_away", "INTEGER", "INTEGER"),
    ("tt_set2_home", "INTEGER", "INTEGER"),
    ("tt_set2_away", "INTEGER", "INTEGER"),
    ("tt_set3_home", "INTEGER", "INTEGER"),
    ("tt_set3_away", "INTEGER", "INTEGER"),
    ("tt_set4_home", "INTEGER", "INTEGER"),
    ("tt_set4_away", "INTEGER", "INTEGER"),
    ("tt_set5_home", "INTEGER", "INTEGER"),
    ("tt_set5_away", "INTEGER", "INTEGER"),
    ("tt_set6_home", "INTEGER", "INTEGER"),
    ("tt_set6_away", "INTEGER", "INTEGER"),
    ("tt_set7_home", "INTEGER", "INTEGER"),
    ("tt_set7_away", "INTEGER", "INTEGER"),
    # Table Tennis - Calculated totals and metrics
    ("tt_total_points_home", "INTEGER", "INTEGER"),
    ("tt_total_points_away", "INTEGER", "INTEGER"),
    ("tt_total_sets_played", "INTEGER", "INTEGER"),
    ("tt_avg_points_per_set_home", "FLOAT", "REAL"),
    ("tt_avg_points_per_set_away", "FLOAT", "REAL"),
    ("tt_close_sets", "INTEGER", "INTEGER"),
    ("tt_deuce_sets", "INTEGER", "INTEGER"),

    # Rugby - Score by half
    ("rugby_first_half_home", "INTEGER", "INTEGER"),
    ("rugby_first_half_away", "INTEGER", "INTEGER"),
    ("rugby_second_half_home", "INTEGER", "INTEGER"),
    ("rugby_second_half_away", "INTEGER", "INTEGER"),
    # Rugby - Totals
    ("rugby_total_points_home", "INTEGER", "INTEGER"),
    ("rugby_total_points_away", "INTEGER", "INTEGER"),
    # Rugby - Derived metrics
    ("rugby_first_half_margin", "INTEGER", "INTEGER"),
    ("rugby_second_half_margin", "INTEGER", "INTEGER"),
    ("rugby_comeback", "BOOLEAN", "INTEGER"),
    ("rugby_points_per_half_home", "FLOAT", "REAL"),
    ("rugby_points_per_half_away", "FLOAT", "REAL"),

    # Bandy - Score by half
    ("bandy_first_half_home", "INTEGER", "INTEGER"),
    ("bandy_first_half_away", "INTEGER", "INTEGER"),
    ("bandy_second_half_home", "INTEGER", "INTEGER"),
    ("bandy_second_half_away", "INTEGER", "INTEGER"),
    # Bandy - Totals
    ("bandy_total_goals_home", "INTEGER", "INTEGER"),
    ("bandy_total_goals_away", "INTEGER", "INTEGER"),
    # Bandy - Derived metrics
    ("bandy_first_half_margin", "INTEGER", "INTEGER"),
    ("bandy_second_half_margin", "INTEGER", "INTEGER"),
    ("bandy_comeback", "BOOLEAN", "INTEGER"),
    ("bandy_goals_per_half_home", "FLOAT", "REAL"),
    ("bandy_goals_per_half_away", "FLOAT", "REAL"),
]


def migrate():
    """Add water polo, table tennis, rugby, and bandy columns to scorealarm_matches table."""
    log.info("=" * 60)
    log.info("🔧 DATABASE MIGRATION: Adding Water Polo, Table Tennis, Rugby, Bandy Columns")
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
