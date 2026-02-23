"""Job to populate teams from Scorealarm."""
import asyncio
from typing import List

from database.db import get_db_session
from database.team_models import Team, TeamStats  # noqa: F401
from database.id_mapping_models import TeamIdMapping
from scrapers.superbet import ScorealarmClient, SuperbetClient
from utils.logger import log


# Sport ID mapping
SPORT_IDS = {
    "Basquete": 4,
    "Basketball": 4,
    "Futebol": 5,
    "Football": 5,
    "Soccer": 5,
}


class PopulateTeamsJob:
    """Job to fetch and store teams from Scorealarm."""

    def __init__(self, sport_ids: List[int] = None):
        self.sport_ids = sport_ids or [4, 5]  # Default: NBA and Soccer

    async def run(self):
        """Run the team population job."""
        log.info("=" * 60)
        log.info("🏆 STARTING TEAMS POPULATION FROM SCOREALARM")
        log.info("=" * 60)

        db = get_db_session()
        total_teams = 0

        try:
            async with ScorealarmClient() as scorealarm:
                async with SuperbetClient() as superbet:
                    # Get tournaments to find teams
                    for sport_id in self.sport_ids:
                        log.info(f"\n📊 Processing sport_id={sport_id}...")

                        tournaments = await superbet.get_tournaments_by_sport(sport_id)
                        log.info(f"   Found {len(tournaments)} tournaments")

                        teams_found = set()

                        for tournament in tournaments[:10]:  # Limit for now
                            try:
                                details = await scorealarm.get_tournament_details(tournament.tournament_id)
                                if not details:
                                    continue

                                latest_season = details.get_latest_season()
                                if not latest_season:
                                    continue

                                matches = await scorealarm.get_competition_events(
                                    season_id=latest_season.id,
                                    competition_id=details.competition_id
                                )

                                for match in matches:
                                    # Extract teams from matches
                                    for team_data in [match.team1, match.team2]:
                                        if team_data.id not in teams_found:
                                            teams_found.add(team_data.id)

                                            # Check if team exists
                                            existing = db.query(Team).filter(
                                                Team.scorealarm_id == str(team_data.id)
                                            ).first()

                                            if not existing:
                                                team = Team(
                                                    name=team_data.name,
                                                    sport_id=sport_id,
                                                    scorealarm_id=str(team_data.id),
                                                    league=tournament.tournament_name,
                                                )
                                                db.add(team)
                                                db.flush()  # Ensure team.id is populated
                                                total_teams += 1

                                                # Add mapping
                                                mapping = TeamIdMapping(
                                                    team_id=team.id,
                                                    platform="scorealarm",
                                                    external_id=str(team_data.id),
                                                    external_name=team_data.name,
                                                    matched_by="exact",
                                                )
                                                db.add(mapping)

                            except Exception as e:
                                log.error(f"Error processing tournament {tournament.tournament_id}: {e}")
                                continue

                        db.commit()
                        log.info(f"   ✅ Saved {len(teams_found)} teams for sport {sport_id}")

            log.info("=" * 60)
            log.info(f"✅ TEAMS POPULATION COMPLETED: {total_teams} new teams")
            log.info("=" * 60)

        except Exception as e:
            db.rollback()
            log.error(f"Teams population failed: {e}")
            raise
        finally:
            db.close()


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Populate teams from Scorealarm")
    parser.add_argument("--sports", nargs="+", type=int, default=[4, 5],
                        help="Sport IDs (default: 4=NBA, 5=Soccer)")
    args = parser.parse_args()

    job = PopulateTeamsJob(sport_ids=args.sports)
    asyncio.run(job.run())


if __name__ == "__main__":
    main()
