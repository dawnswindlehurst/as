"""Job to populate ALL NBA player data from ESPN."""
import time
from database.db import get_db_session
from database.player_models import Player, PlayerGameLog, PlayerSeasonStats
from database.team_models import Team  # noqa: F401
from scrapers.espn_nba import ESPNNBACollector
from utils.logger import log

NBA_SPORT_ID = 4


class PopulateNBAPlayersJob:
    """Job to fetch and store ALL NBA player data."""

    # Temporadas para buscar (2025 = 2024-25, 2024 = 2023-24, etc)
    SEASONS = [2025, 2024, 2023]

    def __init__(self, fetch_gamelogs: bool = False, max_games_per_season: int = 82):
        self.fetch_gamelogs = fetch_gamelogs
        self.max_games = max_games_per_season
        self.espn = ESPNNBACollector()

    def run(self):
        """Run the job."""
        log.info("=" * 60)
        log.info("🏀 STARTING FULL NBA PLAYERS POPULATION")
        log.info("=" * 60)

        db = get_db_session()
        try:
            # 1. Get ALL players from ALL teams
            players = self.espn.get_all_players()
            log.info(f"Fetched {len(players)} players from ESPN")

            # 2. Save players to database
            saved = 0
            # Pre-fetch all teams with ESPN IDs to avoid N+1 queries
            teams_by_espn_id = {
                t.espn_id: t.id
                for t in db.query(Team).filter(Team.espn_id.isnot(None)).all()
            }
            for player_data in players:
                existing = db.query(Player).filter_by(espn_id=player_data.espn_id).first()

                # Try to link with Team via ESPN ID if teams are populated
                team_id = teams_by_espn_id.get(str(player_data.team_id)) if player_data.team_id else None

                if existing:
                    existing.name = player_data.name
                    existing.team_id = team_id
                    existing.position = player_data.position
                    existing.jersey_number = player_data.jersey
                    existing.is_active = True
                else:
                    player = Player(
                        espn_id=player_data.espn_id,
                        name=player_data.name,
                        sport_id=NBA_SPORT_ID,
                        team_id=team_id,
                        position=player_data.position,
                        jersey_number=player_data.jersey,
                        is_active=True,
                    )
                    db.add(player)
                    saved += 1

            db.commit()
            log.info(f"Saved {saved} new players, updated {len(players) - saved} existing")

            # 3. Fetch gamelogs for ALL players if requested
            if self.fetch_gamelogs:
                self._fetch_all_gamelogs(db)

        except Exception as e:
            db.rollback()
            log.error(f"NBA players job failed: {e}")
            raise
        finally:
            db.close()

        log.info("=" * 60)
        log.info("✅ NBA PLAYERS POPULATION COMPLETED")
        log.info("=" * 60)

    def _fetch_all_gamelogs(self, db):
        """Fetch game logs for ALL players, ALL seasons."""
        players = db.query(Player).filter_by(is_active=True, sport_id=NBA_SPORT_ID).all()
        total = len(players)

        log.info(f"Fetching gamelogs for {total} players across {len(self.SEASONS)} seasons")

        for idx, player in enumerate(players, 1):
            try:
                log.info(f"[{idx}/{total}] Processing {player.name}...")

                total_games = 0

                for season in self.SEASONS:
                    season_str = f"{season-1}-{str(season)[2:]}"  # 2025 -> "2024-25"

                    # Check if we already have this season
                    existing_stats = db.query(PlayerSeasonStats).filter_by(
                        player_id=player.id, season=season_str
                    ).first()

                    if existing_stats and existing_stats.games_played >= 10:
                        log.debug(f"  Season {season_str} already populated, skipping")
                        continue

                    # Fetch from ESPN
                    time.sleep(0.3)  # Rate limiting
                    games = self.espn.get_player_gamelog(
                        player.espn_id,
                        season=season,
                        limit=self.max_games
                    )

                    if not games:
                        continue

                    # Save gamelogs
                    for game in games:
                        # Check if game already exists
                        existing_game = db.query(PlayerGameLog).filter_by(
                            player_id=player.id,
                            game_id=game.game_id
                        ).first() if game.game_id else None

                        if existing_game:
                            continue

                        gamelog = PlayerGameLog(
                            player_id=player.id,
                            sport_id=NBA_SPORT_ID,
                            game_id=game.game_id,
                            season=season_str,
                            points=game.points,
                            rebounds=game.rebounds,
                            assists=game.assists,
                            steals=game.steals,
                            blocks=game.blocks,
                            turnovers=game.turnovers,
                            fouls=game.fouls,
                            fgm=game.fgm,
                            fga=game.fga,
                            fg3m=game.fg3m,
                            fg3a=game.fg3a,
                            ftm=game.ftm,
                            fta=game.fta,
                            minutes=game.minutes,
                            pts_reb=game.points + game.rebounds,
                            pts_ast=game.points + game.assists,
                            reb_ast=game.rebounds + game.assists,
                            pts_reb_ast=game.points + game.rebounds + game.assists,
                        )
                        db.add(gamelog)
                        total_games += 1

                    # Update season stats
                    self._update_season_stats(db, player, games, season_str)

                db.commit()

                if total_games > 0:
                    log.info(f"  ✓ Saved {total_games} games for {player.name}")

                # Progress update every 50 players
                if idx % 50 == 0:
                    log.info(f"Progress: {idx}/{total} players processed ({idx*100//total}%)")

            except Exception as e:
                log.error(f"Error processing {player.name}: {e}")
                db.rollback()
                continue

    def _update_season_stats(self, db, player: Player, games, season: str):
        """Calculate and save season stats."""
        if not games:
            return

        n = len(games)

        # Calculate averages
        ppg = sum(g.points for g in games) / n
        rpg = sum(g.rebounds for g in games) / n
        apg = sum(g.assists for g in games) / n
        spg = sum(g.steals for g in games) / n
        bpg = sum(g.blocks for g in games) / n
        topg = sum(g.turnovers for g in games) / n
        mpg = sum(g.minutes for g in games) / n

        total_fgm = sum(g.fgm for g in games)
        total_fga = sum(g.fga for g in games)
        total_fg3m = sum(g.fg3m for g in games)
        total_fg3a = sum(g.fg3a for g in games)
        total_ftm = sum(g.ftm for g in games)
        total_fta = sum(g.fta for g in games)

        fg_pct = total_fgm / total_fga if total_fga > 0 else 0
        fg3_pct = total_fg3m / total_fg3a if total_fg3a > 0 else 0
        ft_pct = total_ftm / total_fta if total_fta > 0 else 0

        # Update or create season stats
        existing = db.query(PlayerSeasonStats).filter_by(
            player_id=player.id, season=season
        ).first()

        if existing:
            existing.games_played = n
            existing.ppg = round(ppg, 1)
            existing.rpg = round(rpg, 1)
            existing.apg = round(apg, 1)
            existing.spg = round(spg, 1)
            existing.bpg = round(bpg, 1)
            existing.topg = round(topg, 1)
            existing.mpg = round(mpg, 1)
            existing.fg_pct = round(fg_pct, 3)
            existing.fg3_pct = round(fg3_pct, 3)
            existing.ft_pct = round(ft_pct, 3)
            existing.pts_reb_avg = round(ppg + rpg, 1)
            existing.pts_ast_avg = round(ppg + apg, 1)
            existing.reb_ast_avg = round(rpg + apg, 1)
            existing.pts_reb_ast_avg = round(ppg + rpg + apg, 1)
        else:
            stats = PlayerSeasonStats(
                player_id=player.id,
                sport_id=NBA_SPORT_ID,
                season=season,
                games_played=n,
                ppg=round(ppg, 1),
                rpg=round(rpg, 1),
                apg=round(apg, 1),
                spg=round(spg, 1),
                bpg=round(bpg, 1),
                topg=round(topg, 1),
                mpg=round(mpg, 1),
                fg_pct=round(fg_pct, 3),
                fg3_pct=round(fg3_pct, 3),
                ft_pct=round(ft_pct, 3),
                pts_reb_avg=round(ppg + rpg, 1),
                pts_ast_avg=round(ppg + apg, 1),
                reb_ast_avg=round(rpg + apg, 1),
                pts_reb_ast_avg=round(ppg + rpg + apg, 1),
            )
            db.add(stats)


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Populate ALL NBA players")
    parser.add_argument("--gamelogs", action="store_true", help="Also fetch game logs")
    parser.add_argument("--max-games", type=int, default=82, help="Max games per season")
    args = parser.parse_args()
    
    job = PopulateNBAPlayersJob(fetch_gamelogs=args.gamelogs, max_games_per_season=args.max_games)
    job.run()


if __name__ == "__main__":
    main()
