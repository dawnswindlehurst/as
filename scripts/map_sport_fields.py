"""Map Scorealarm V2 stats/event fields per sport using historical fixtures.

This script scans finished matches per sport, fetches fixture overviews through
same Scorealarm V2 flow used by football enrichment, and saves a per-sport JSON
summary under analysis/sport_field_mapping/.
"""

import argparse
import asyncio
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.exc import OperationalError

from utils.logger import log


SCRIPT_VERSION = "2026.02.20"


def slugify(value: str) -> str:
    """Create filesystem-safe slug for sport names."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "unknown"


def normalize_fixture_id(offer_id: str | None) -> str | None:
    """Normalize fixture id to ax:match:* format expected by V2 endpoints."""
    if not offer_id:
        return None
    offer_id = str(offer_id).strip()
    if not offer_id:
        return None
    if offer_id.startswith("ax:match:"):
        return offer_id
    if offer_id.isdigit():
        return f"ax:match:{offer_id}"
    return offer_id


class SportFieldMapper:
    """Analyze field coverage by sport using V2 fixture overviews."""

    def __init__(
        self,
        per_sport_limit: int = 5,
        max_ids_per_sport: int = 100,
        stop_on_first_data: bool = True,
        only_sports: set[int] | None = None,
    ):
        # Lazy imports avoid loading DB/client side effects for --help output.
        from database.db import get_db_session

        self.ScorealarmMatch = None
        self.ScorealarmSport = None
        self.ScorealarmClient = None
        self.db = get_db_session()
        self.per_sport_limit = per_sport_limit
        self.max_ids_per_sport = max_ids_per_sport
        self.stop_on_first_data = stop_on_first_data
        self.only_sports = only_sports or set()
        self.output_dir = Path("analysis/sport_field_mapping")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _sports_to_process(self) -> list[Any]:
        if self.ScorealarmSport is None:
            from database.scorealarm_models import ScorealarmSport

            self.ScorealarmSport = ScorealarmSport

        query = self.db.query(self.ScorealarmSport).order_by(self.ScorealarmSport.id.asc())
        if self.only_sports:
            query = query.filter(self.ScorealarmSport.id.in_(self.only_sports))
        return query.all()

    def _candidate_matches(self, sport_id: int) -> list[Any]:
        if self.ScorealarmMatch is None:
            from database.scorealarm_models import ScorealarmMatch

            self.ScorealarmMatch = ScorealarmMatch

        return (
            self.db.query(self.ScorealarmMatch)
            .filter(
                self.ScorealarmMatch.sport_id == sport_id,
                self.ScorealarmMatch.is_finished.is_(True),
                self.ScorealarmMatch.offer_id.isnot(None),
            )
            .order_by(self.ScorealarmMatch.match_date.desc())
            .limit(self.max_ids_per_sport)
            .all()
        )

    async def run(self):
        try:
            sports = self._sports_to_process()
        except OperationalError as exc:
            log.error(f"Database schema is not ready for mapping: {exc}")
            log.error("Run migrations/population first so scorealarm_sports and matches exist.")
            return

        if not sports:
            log.warning("No sports found to process.")
            return

        if self.ScorealarmClient is None:
            from scrapers.superbet.scorealarm_client import ScorealarmClient

            self.ScorealarmClient = ScorealarmClient

        async with self.ScorealarmClient() as client:
            for sport in sports:
                candidates = self._candidate_matches(sport.id)
                if not candidates:
                    log.info(f"[{sport.name}] no finished matches found, skipping")
                    continue

                print(f"\n=== {sport.name} (sport_id={sport.id}) ===")

                stat_types = Counter()
                stat_names = Counter()
                event_types = Counter()
                event_subtypes = Counter()

                sample_rows: list[dict[str, Any]] = []
                checked_ids = 0
                with_data = 0

                for match in candidates:
                    if checked_ids >= self.max_ids_per_sport:
                        break

                    fixture_id = normalize_fixture_id(match.offer_id)
                    if not fixture_id:
                        continue

                    checked_ids += 1
                    fixture_stats = await client.get_fixture_stats(fixture_id, sport_hint=sport.name)
                    if not fixture_stats:
                        print(f"  match_id={match.id} fixture={fixture_id} -> NO_DATA")
                        sample_rows.append(
                            {
                                "match_id": match.id,
                                "fixture_id": fixture_id,
                                "status": "NO_DATA",
                            }
                        )
                        continue

                    stats = fixture_stats.match_stats or []
                    events = fixture_stats.live_events or []

                    print(f"  match_id={match.id} stats={len(stats)} events={len(events)}")

                    for s in stats:
                        stat_types[s.type] += 1
                        if s.stat_name:
                            stat_names[s.stat_name] += 1
                    for e in events:
                        event_types[e.type] += 1
                        event_subtypes[e.subtype] += 1

                    sample_rows.append(
                        {
                            "match_id": match.id,
                            "fixture_id": fixture_id,
                            "status": "OK",
                            "stats_count": len(stats),
                            "events_count": len(events),
                            "stats": [
                                {
                                    "type": s.type,
                                    "stat_name": s.stat_name,
                                    "team1": s.team1,
                                    "team2": s.team2,
                                }
                                for s in stats
                            ],
                            "events": [
                                {
                                    "type": e.type,
                                    "subtype": e.subtype,
                                    "side": e.side,
                                    "minute": e.minute,
                                    "added_time": e.added_time,
                                    "score": e.score,
                                }
                                for e in events
                            ],
                        }
                    )
                    with_data += 1

                    if self.stop_on_first_data and (stat_types or event_types):
                        print("  ✅ Campos encontrados; encerrando busca antecipadamente para este esporte")
                        break

                    if with_data >= self.per_sport_limit:
                        break

                summary = {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "sport": {
                        "id": sport.id,
                        "name": sport.name,
                    },
                    "scan": {
                        "max_ids_per_sport": self.max_ids_per_sport,
                        "checked_ids": checked_ids,
                        "matches_with_data": with_data,
                        "stop_on_first_data": self.stop_on_first_data,
                        "target_matches_with_data": self.per_sport_limit,
                    },
                    "samples": sample_rows,
                    "top_stat_types": stat_types.most_common(30),
                    "top_stat_names": stat_names.most_common(50),
                    "top_event_types": event_types.most_common(20),
                    "top_event_subtypes": event_subtypes.most_common(20),
                }

                print(f"  Top stat types: {summary['top_stat_types'][:15]}")
                print(f"  Top stat names: {summary['top_stat_names'][:15]}")
                print(f"  Top event types: {summary['top_event_types'][:15]}")
                print(f"  Top event subtypes: {summary['top_event_subtypes'][:15]}")

                out_name = f"sport_{sport.id}_{slugify(sport.name)}.json"
                out_path = self.output_dir / out_name
                out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  Saved -> {out_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan up to N finished matches per sport and map V2 stat/event fields "
            "into analysis/sport_field_mapping/*.json"
        )
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"map_sport_fields.py {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--per-sport-limit",
        type=int,
        default=5,
        help="How many matches with data to keep per sport when not stopping early (default: 5)",
    )
    parser.add_argument(
        "--max-ids-per-sport",
        type=int,
        default=100,
        help="Maximum fixture IDs to try per sport before giving up (default: 100)",
    )
    parser.add_argument(
        "--stop-on-first-data",
        action="store_true",
        default=True,
        help="Stop as soon as fields are found for the sport (default: enabled)",
    )
    parser.add_argument(
        "--no-stop-on-first-data",
        action="store_true",
        help="Disable early stop and continue collecting until --per-sport-limit or --max-ids-per-sport",
    )
    parser.add_argument(
        "--sports",
        type=str,
        default="",
        help="Comma-separated sport ids to process (default: all sports)",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    only_sports = {
        int(part.strip())
        for part in args.sports.split(",")
        if part.strip()
    }

    stop_on_first_data = args.stop_on_first_data and not args.no_stop_on_first_data

    mapper = SportFieldMapper(
        per_sport_limit=args.per_sport_limit,
        max_ids_per_sport=args.max_ids_per_sport,
        stop_on_first_data=stop_on_first_data,
        only_sports=only_sports,
    )
    await mapper.run()


if __name__ == "__main__":
    asyncio.run(main())
