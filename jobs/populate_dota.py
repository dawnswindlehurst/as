"""Job to populate the database with Dota 2 match data from OpenDota API."""
import asyncio
from datetime import datetime, timezone
from typing import Optional
from database.db import get_db_session
from database.dota_models import DotaTeam, DotaMatch, DotaGame, DotaTeamStats
from scrapers.dota import DotaUnified, DotaMatch as ScraperMatch
from utils.logger import log


class PopulateDotaJob:
    """Populates the database with Dota 2 data from OpenDota API."""

    def __init__(self, fetch_history: bool = False):
        self.fetch_history = fetch_history
        self.scraper = DotaUnified()
        self.db = get_db_session()

    def run(self):
        """Execute the full population job."""
        log.info("Starting Dota 2 database population job")
        try:
            asyncio.run(self._run_async())
        finally:
            self.db.close()
            asyncio.run(self.scraper.close())
        log.info("Dota 2 population job completed")

    async def _run_async(self):
        """Async implementation of the run method."""
        matches = await self.scraper.get_pro_matches(100, fetch_history=self.fetch_history)
        log.info(f"Fetched {len(matches)} Dota 2 matches")

        saved = {"upcoming": 0, "live": 0, "completed": 0}

        for match in matches:
            try:
                # Salvar times
                team1_db = self._save_team(match.radiant_name, match.radiant_team_id)
                team2_db = self._save_team(match.dire_name, match.dire_team_id)

                # Salvar match
                self._save_match(match, team1_db, team2_db)
                saved[match.status] = saved.get(match.status, 0) + 1

                self.db.commit()

            except Exception as e:
                log.error(f"Error processing match {match.match_id}: {e}")
                self.db.rollback()

        log.info(f"Saved: {saved['upcoming']} upcoming, {saved['live']} live, {saved['completed']} completed")

    def _save_team(self, name: str, team_id: Optional[int]) -> DotaTeam:
        """Save or update a team in the database."""
        if not name or name in ("Radiant", "Dire"):
            name = "TBD"

        team = self.db.query(DotaTeam).filter_by(name=name).first()
        if team is None:
            team = DotaTeam(
                name=name,
                team_id=team_id,
            )
            self.db.add(team)
            self.db.flush()
            log.debug(f"Created new team: {name}")
        elif team_id and not team.team_id:
            team.team_id = team_id
        return team

    def _save_match(self, scraper_match: ScraperMatch,
                    team1_db: DotaTeam, team2_db: DotaTeam) -> DotaMatch:
        """Save or update a match in the database."""
        match = self.db.query(DotaMatch).filter_by(
            match_id=str(scraper_match.match_id)
        ).first()

        match_date: Optional[datetime] = None
        if scraper_match.start_time:
            try:
                match_date = datetime.utcfromtimestamp(scraper_match.start_time).replace(tzinfo=timezone.utc)
            except (ValueError, OSError):
                pass

        # Determine winner
        winner = ""
        if scraper_match.status == "completed" and scraper_match.radiant_win is not None:
            winner = team1_db.name if scraper_match.radiant_win else team2_db.name

        # Series type to best_of
        series_map = {0: 1, 1: 3, 2: 5}
        best_of = series_map.get(scraper_match.series_type, 1) if scraper_match.series_type is not None else 1

        if match is None:
            match = DotaMatch(
                match_id=str(scraper_match.match_id),
                team1_id=team1_db.id,
                team2_id=team2_db.id,
                team1_name=team1_db.name,
                team2_name=team2_db.name,
                team1_score=scraper_match.radiant_score,
                team2_score=scraper_match.dire_score,
                winner=winner,
                league=scraper_match.league_name,
                best_of=best_of,
                match_date=match_date,
                status=scraper_match.status,
                duration=scraper_match.duration,
            )
            self.db.add(match)
            self.db.flush()
            log.debug(f"Created new match: {scraper_match.match_id}")
        else:
            match.team1_id = team1_db.id
            match.team2_id = team2_db.id
            match.team1_name = team1_db.name
            match.team2_name = team2_db.name
            match.team1_score = scraper_match.radiant_score
            match.team2_score = scraper_match.dire_score
            match.winner = winner
            match.league = scraper_match.league_name
            match.best_of = best_of
            match.match_date = match_date
            match.status = scraper_match.status
            match.duration = scraper_match.duration
        return match


if __name__ == "__main__":
    import sys
    fetch_history = "--history" in sys.argv
    if fetch_history:
        log.info("Running with --history flag: fetching all data until 2024")
    job = PopulateDotaJob(fetch_history=fetch_history)
    job.run()
