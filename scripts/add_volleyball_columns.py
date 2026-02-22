"""Migration script to add volleyball-specific match columns for value bet analysis."""
import sys
from sqlalchemy import text, inspect
from database.db import get_db_session, engine
from utils.logger import log


# Columns to add: (name, postgresql_type, sqlite_type)
NEW_COLUMNS = [
    # Sets won
    ("sets_home", "INTEGER", "INTEGER"),
    ("sets_away", "INTEGER", "INTEGER"),
    # Points per set
    ("set1_home", "INTEGER", "INTEGER"),
    ("set1_away", "INTEGER", "INTEGER"),
    ("set2_home", "INTEGER", "INTEGER"),
    ("set2_away", "INTEGER", "INTEGER"),
    ("set3_home", "INTEGER", "INTEGER"),
    ("set3_away", "INTEGER", "INTEGER"),
    ("set4_home", "INTEGER", "INTEGER"),
    ("set4_away", "INTEGER", "INTEGER"),
    ("set5_home", "INTEGER", "INTEGER"),
    ("set5_away", "INTEGER", "INTEGER"),
    # Calculated totals
    ("total_points_home", "INTEGER", "INTEGER"),
    ("total_points_away", "INTEGER", "INTEGER"),
    ("total_sets_played", "INTEGER", "INTEGER"),
    # Derived metrics
    ("avg_points_per_set_home", "FLOAT", "REAL"),
    ("avg_points_per_set_away", "FLOAT", "REAL"),
    ("point_diff_per_set", "JSONB", "TEXT"),
]


def migrate():
    """Add volleyball columns to scorealarm_matches table."""
    log.info("=" * 60)
    log.info("🔧 DATABASE MIGRATION: Adding Volleyball Detail Columns")
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
