"""Job to populate the database with LoL match data from the LoL Esports API."""
import asyncio
from datetime import datetime, timezone
from typing import Optional
from database.db import get_db_session
from database.lol_models import LolTeam, LolMatch, LolGame, LolTeamStats
from scrapers.lol import LoLUnified, LoLMatch as ScraperMatch, LoLTeam as ScraperTeam
from utils.logger import log


class PopulateLolJob:
    """Populates the database with LoL data from the LoL Esports API."""

    def __init__(self):
        self.scraper = LoLUnified()
        self.db = get_db_session()

    def run(self):
        """Execute the full population job."""
        log.info("Starting LoL database population job")
        try:
            asyncio.run(self._run_async())
        finally:
            self.db.close()
            asyncio.run(self.scraper.close())
        log.info("LoL population job completed")

    async def _run_async(self):
        """Async implementation of the run method."""
        matches = await self.scraper.get_upcoming_matches()
        log.info(f"Fetched {len(matches)} LoL matches")

        saved = {"upcoming": 0, "tbd": 0, "live": 0, "completed": 0}

        for match in matches:
            try:
                # Salvar times (mesmo TBD, para referência)
                team1_db = self._save_team(match.team1)
                team2_db = self._save_team(match.team2)

                # Salvar match
                match_db = self._save_match(match, team1_db, team2_db)
                saved[match.status] = saved.get(match.status, 0) + 1

                # Buscar detalhes dos games se completed
                if match.status == "completed":
                    if match.games:
                        for game in match.games:
                            self._save_game(match_db.match_id, game)
                    else:
                        details = await self.scraper.get_match_details(match.match_id)
                        if details and details.games:
                            for game in details.games:
                                self._save_game(match_db.match_id, game)

                self.db.commit()

                # Só atualizar stats para times reais (não TBD) em matches completed
                if match.status == "completed":
                    if team1_db.name != "TBD":
                        self._update_team_stats(team1_db, match.league)
                    if team2_db.name != "TBD":
                        self._update_team_stats(team2_db, match.league)
                    self.db.commit()

            except Exception as e:
                log.error(f"Error processing match {match.match_id}: {e}")
                self.db.rollback()

        log.info(f"Saved: {saved['upcoming']} upcoming, {saved['tbd']} TBD, {saved['live']} live, {saved['completed']} completed")

    def _save_team(self, scraper_team: ScraperTeam) -> LolTeam:
        """Save or update a team in the database.

        Args:
            scraper_team: LoLTeam object from scraper

        Returns:
            LolTeam database object
        """
        team = self.db.query(LolTeam).filter_by(name=scraper_team.name).first()
        if team is None:
            team = LolTeam(
                name=scraper_team.name,
                code=scraper_team.code,
                league=scraper_team.league,
                region=scraper_team.region,
                logo=scraper_team.logo,
            )
            self.db.add(team)
            self.db.flush()
            log.debug(f"Created new team: {scraper_team.name}")
        else:
            team.code = scraper_team.code
            team.league = scraper_team.league
            team.region = scraper_team.region
            team.logo = scraper_team.logo
        return team

    def _save_match(self, scraper_match: ScraperMatch,
                    team1_db: LolTeam, team2_db: LolTeam) -> LolMatch:
        """Save or update a match in the database.

        Args:
            scraper_match: LoLMatch object from scraper
            team1_db: LolTeam record for team1
            team2_db: LolTeam record for team2

        Returns:
            LolMatch database object
        """
        match = self.db.query(LolMatch).filter_by(
            match_id=scraper_match.match_id
        ).first()

        match_date: Optional[datetime] = None
        if scraper_match.date:
            try:
                match_date = datetime.fromisoformat(
                    scraper_match.date.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        if match is None:
            match = LolMatch(
                match_id=scraper_match.match_id,
                team1_id=team1_db.id,
                team2_id=team2_db.id,
                team1_name=scraper_match.team1.name,
                team2_name=scraper_match.team2.name,
                team1_score=scraper_match.score1,
                team2_score=scraper_match.score2,
                winner=scraper_match.winner,
                league=scraper_match.league,
                tournament=scraper_match.tournament,
                best_of=scraper_match.best_of,
                match_date=match_date,
                status=scraper_match.status,
                url=scraper_match.url,
            )
            self.db.add(match)
            self.db.flush()
            log.debug(f"Created new match: {scraper_match.match_id}")
        else:
            match.team1_id = team1_db.id
            match.team2_id = team2_db.id
            match.team1_name = scraper_match.team1.name
            match.team2_name = scraper_match.team2.name
            match.team1_score = scraper_match.score1
            match.team2_score = scraper_match.score2
            match.winner = scraper_match.winner
            match.league = scraper_match.league
            match.tournament = scraper_match.tournament
            match.best_of = scraper_match.best_of
            match.match_date = match_date
            match.status = scraper_match.status
            match.url = scraper_match.url
        return match

    def _save_game(self, match_id: str, game) -> LolGame:
        """Save or update a game in the database.

        Args:
            match_id: Match ID string (FK to lol_matches.match_id)
            game: LoLGameResult object from scraper

        Returns:
            LolGame database object
        """
        existing = self.db.query(LolGame).filter_by(
            match_id=match_id,
            game_number=game.game_number,
        ).first()

        if existing is None:
            db_game = LolGame(
                match_id=match_id,
                game_number=game.game_number,
                blue_team=game.blue_team,
                red_team=game.red_team,
                winner=game.winner,
                duration=game.duration,
                blue_picks=game.blue_picks,
                red_picks=game.red_picks,
                blue_bans=game.blue_bans,
                red_bans=game.red_bans,
            )
            self.db.add(db_game)
            self.db.flush()
            log.debug(f"Created game {game.game_number} for match {match_id}")
        else:
            existing.blue_team = game.blue_team
            existing.red_team = game.red_team
            existing.winner = game.winner
            existing.duration = game.duration
            existing.blue_picks = game.blue_picks
            existing.red_picks = game.red_picks
            existing.blue_bans = game.blue_bans
            existing.red_bans = game.red_bans
            db_game = existing
        return db_game

    def _update_team_stats(self, team_db: LolTeam, league: str) -> LolTeamStats:
        """Recalculate and update team statistics for a given league.

        Args:
            team_db: LolTeam database object
            league: League name

        Returns:
            LolTeamStats database object
        """
        stats = self.db.query(LolTeamStats).filter_by(
            team_id=team_db.id,
            league=league,
        ).first()

        if stats is None:
            stats = LolTeamStats(
                team_id=team_db.id,
                team_name=team_db.name,
                league=league,
            )
            self.db.add(stats)

        # Recalculate from completed matches (ordered by date for correct streak)
        completed = self.db.query(LolMatch).filter(
            (LolMatch.team1_id == team_db.id) | (LolMatch.team2_id == team_db.id),
            LolMatch.league == league,
            LolMatch.status == "completed",
        ).order_by(LolMatch.match_date.asc().nullslast()).all()

        wins = 0
        losses = 0
        blue_wins = 0
        blue_losses = 0
        red_wins = 0
        red_losses = 0
        streak = 0
        best_streak = 0
        results = []

        for m in completed:
            won = m.winner == team_db.name
            results.append(won)
            if won:
                wins += 1
            else:
                losses += 1

            # Determine side from individual game records
            games = self.db.query(LolGame).filter_by(match_id=m.match_id).all()
            if games:
                on_blue = any(g.blue_team == team_db.name for g in games)
                on_red = any(g.red_team == team_db.name for g in games)
            else:
                # Fallback: team1 is blue side, team2 is red side
                on_blue = m.team1_id == team_db.id
                on_red = m.team2_id == team_db.id

            if on_blue:
                if won:
                    blue_wins += 1
                else:
                    blue_losses += 1
            elif on_red:
                if won:
                    red_wins += 1
                else:
                    red_losses += 1

        # Calculate current streak (from most recent results)
        if results:
            last = results[-1]
            for r in reversed(results):
                if r == last:
                    streak += 1
                else:
                    break
            if not last:
                streak = -streak  # negative streak = losing streak

        # Best streak
        cur = 0
        for r in results:
            if r:
                cur += 1
                best_streak = max(best_streak, cur)
            else:
                cur = 0

        total = wins + losses
        stats.team_name = team_db.name
        stats.wins = wins
        stats.losses = losses
        stats.win_rate = wins / total if total > 0 else 0.0
        stats.blue_side_wins = blue_wins
        stats.blue_side_losses = blue_losses
        stats.red_side_wins = red_wins
        stats.red_side_losses = red_losses
        stats.current_streak = streak
        stats.best_streak = best_streak
        stats.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return stats


if __name__ == "__main__":
    job = PopulateLolJob()
    job.run()
