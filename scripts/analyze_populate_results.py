"""Analyze populated Scorealarm matches (missing results + examples by sport)."""
from collections import defaultdict
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import and_, or_, func
from sqlalchemy.exc import OperationalError

from database.db import get_db_session
from database.scorealarm_models import (
    ScorealarmMatch,
    ScorealarmSport,
    ScorealarmTournament,
    ScorealarmSeason,
)


def main() -> None:
    db = get_db_session()
    try:
        try:
            total_matches = db.query(func.count(ScorealarmMatch.id)).scalar() or 0
        except OperationalError as exc:
            print("⚠️ Não foi possível consultar scorealarm_matches.")
            print(f"Detalhe: {exc}")
            print("Dica: defina DATABASE_URL para o banco da VPS com dados populados.")
            return
        no_score_count = db.query(func.count(ScorealarmMatch.id)).filter(
            ScorealarmMatch.team1_score.is_(None),
            ScorealarmMatch.team2_score.is_(None),
        ).scalar() or 0

        not_finished_count = db.query(func.count(ScorealarmMatch.id)).filter(
            or_(
                ScorealarmMatch.is_finished.is_(False),
                ScorealarmMatch.match_status != 100,
            )
        ).scalar() or 0

        unresolved_count = db.query(func.count(ScorealarmMatch.id)).filter(
            and_(
                ScorealarmMatch.team1_score.is_(None),
                ScorealarmMatch.team2_score.is_(None),
                or_(
                    ScorealarmMatch.is_finished.is_(False),
                    ScorealarmMatch.match_status != 100,
                ),
            )
        ).scalar() or 0

        print("=" * 72)
        print("ANÁLISE DE RESULTADOS DO POPULATE")
        print("=" * 72)
        print(f"Total de partidas: {total_matches}")
        print(f"Sem placar (team1_score/team2_score nulos): {no_score_count}")
        print(f"Não finalizadas (is_finished=false ou status!=100): {not_finished_count}")
        print(f"Provavelmente não ocorreram ainda (interseção): {unresolved_count}")

        no_result_examples = (
            db.query(
                ScorealarmMatch.id,
                ScorealarmSport.name.label("sport"),
                ScorealarmTournament.name.label("tournament"),
                ScorealarmSeason.name.label("season"),
                ScorealarmMatch.match_date,
                ScorealarmMatch.match_status,
                ScorealarmMatch.is_finished,
            )
            .join(ScorealarmSport, ScorealarmSport.id == ScorealarmMatch.sport_id, isouter=True)
            .join(ScorealarmTournament, ScorealarmTournament.id == ScorealarmMatch.tournament_id, isouter=True)
            .join(ScorealarmSeason, ScorealarmSeason.id == ScorealarmMatch.season_id, isouter=True)
            .filter(
                ScorealarmMatch.team1_score.is_(None),
                ScorealarmMatch.team2_score.is_(None),
            )
            .order_by(ScorealarmMatch.match_date.desc())
            .limit(20)
            .all()
        )

        print("\nExemplos de partidas sem resultado (top 20 por data):")
        for row in no_result_examples:
            print(
                f"- id={row.id} | esporte={row.sport} | torneio={row.tournament} | "
                f"season={row.season} | data={row.match_date} | status={row.match_status} | "
                f"finished={row.is_finished}"
            )

        with_result_rows = (
            db.query(
                ScorealarmSport.name.label("sport"),
                ScorealarmMatch.id,
                ScorealarmTournament.name.label("tournament"),
                ScorealarmSeason.name.label("season"),
                ScorealarmMatch.match_date,
                ScorealarmMatch.team1_score,
                ScorealarmMatch.team2_score,
                ScorealarmMatch.match_status,
                ScorealarmMatch.is_finished,
            )
            .join(ScorealarmSport, ScorealarmSport.id == ScorealarmMatch.sport_id)
            .join(ScorealarmTournament, ScorealarmTournament.id == ScorealarmMatch.tournament_id, isouter=True)
            .join(ScorealarmSeason, ScorealarmSeason.id == ScorealarmMatch.season_id, isouter=True)
            .filter(
                or_(
                    ScorealarmMatch.team1_score.is_not(None),
                    ScorealarmMatch.team2_score.is_not(None),
                )
            )
            .order_by(ScorealarmSport.name.asc(), ScorealarmMatch.match_date.desc())
            .all()
        )

        per_sport_examples = defaultdict(list)
        for row in with_result_rows:
            if len(per_sport_examples[row.sport]) < 3:
                per_sport_examples[row.sport].append(row)

        print("\nExemplos de partidas com resultado (até 3 por esporte):")
        for sport in sorted(per_sport_examples.keys()):
            print(f"\n[{sport}]")
            for row in per_sport_examples[sport]:
                print(
                    f"- id={row.id} | {row.team1_score}-{row.team2_score} | "
                    f"torneio={row.tournament} | season={row.season} | "
                    f"data={row.match_date} | status={row.match_status} | finished={row.is_finished}"
                )

    finally:
        db.close()


if __name__ == "__main__":
    main()
