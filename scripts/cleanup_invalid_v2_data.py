"""Cleanup V2 enrichment persisted for sports outside football/tennis."""
import argparse
from database.db import get_db_session
from database.scorealarm_models import ScorealarmMatch
from utils.logger import log

VALID_V2_SPORT_IDS = {55, 57}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove V2 enrichment data from sports other than football (55) and tennis (57)."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply cleanup changes. Without this flag, only prints how many rows would be affected.",
    )
    args = parser.parse_args()

    db = get_db_session()
    try:
        q = db.query(ScorealarmMatch).filter(~ScorealarmMatch.sport_id.in_(VALID_V2_SPORT_IDS)).filter(
            (ScorealarmMatch.enriched_at.isnot(None))
            | (ScorealarmMatch.match_stats_raw.isnot(None))
            | (ScorealarmMatch.live_events_raw.isnot(None))
            | (ScorealarmMatch.tennis_match_metrics.isnot(None))
            | (ScorealarmMatch.tennis_period_metrics.isnot(None))
            | (ScorealarmMatch.xg_home.isnot(None))
            | (ScorealarmMatch.xg_away.isnot(None))
            | (ScorealarmMatch.shots_on_goal_home.isnot(None))
            | (ScorealarmMatch.shots_on_goal_away.isnot(None))
            | (ScorealarmMatch.corners_home.isnot(None))
            | (ScorealarmMatch.corners_away.isnot(None))
            | (ScorealarmMatch.goal_events.isnot(None))
        )

        affected = q.count()
        log.info(f"Rows with invalid V2 enrichment (sport_id not in [55,57]): {affected}")
        if not args.apply:
            log.info("Dry-run only. Use --apply to persist cleanup.")
            return

        updated = q.update(
            {
                ScorealarmMatch.enriched_at: None,
                ScorealarmMatch.match_stats_raw: None,
                ScorealarmMatch.live_events_raw: None,
                ScorealarmMatch.tennis_match_metrics: None,
                ScorealarmMatch.tennis_period_metrics: None,
                ScorealarmMatch.xg_home: None,
                ScorealarmMatch.xg_away: None,
                ScorealarmMatch.shots_on_goal_home: None,
                ScorealarmMatch.shots_on_goal_away: None,
                ScorealarmMatch.corners_home: None,
                ScorealarmMatch.corners_away: None,
                ScorealarmMatch.goal_events: None,
            },
            synchronize_session=False,
        )
        db.commit()
        log.info(f"Cleanup committed. Rows updated: {updated}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
