"""Job to collect and save odds from Superbet API."""
import asyncio
from datetime import datetime, timezone
from typing import List, Optional

from database.db import get_db_session
from database.scorealarm_models import OddsHistory, ScorealarmMatch
from scrapers.superbet import SuperbetClient
from utils.logger import log


class PopulateOddsJob:
    """Job to fetch and store odds from Superbet."""

    # Sports to collect odds for
    SPORTS = {
        4: "Basquete",
        5: "Futebol",
        55: "CS2",
        54: "Dota 2",
        153: "Valorant",
        39: "LoL",
    }

    def __init__(self, sports: List[int] = None):
        self.sports = sports or [4, 5]  # Default: Basquete e Futebol

    async def run(self):
        """Run the odds collection job."""
        log.info("=" * 60)
        log.info("🎰 STARTING ODDS COLLECTION FROM SUPERBET")
        log.info("=" * 60)

        db = get_db_session()
        total_odds = 0

        try:
            async with SuperbetClient() as client:
                for sport_id in self.sports:
                    sport_name = self.SPORTS.get(sport_id, f"Sport {sport_id}")
                    log.info(f"\n📊 Collecting {sport_name}...")

                    # Get events
                    events = await client.get_events_by_sport(sport_id)
                    log.info(f"   Found {len(events)} events")

                    for event in events:
                        odds_count = await self._save_event_odds(db, event, sport_id)
                        total_odds += odds_count

                    db.commit()
                    log.info(f"   ✅ {sport_name} complete")

            log.info("=" * 60)
            log.info(f"✅ ODDS COLLECTION COMPLETED: {total_odds} odds saved")
            log.info("=" * 60)

        except Exception as e:
            db.rollback()
            log.error(f"Odds collection failed: {e}")
            raise
        finally:
            db.close()

    async def _save_event_odds(self, db, event, sport_id: int) -> int:
        """Save odds for a single event."""
        odds_count = 0
        event_id = str(event.event_id)

        # Try to find matching ScorealarmMatch
        scorealarm_match = db.query(ScorealarmMatch).filter(
            ScorealarmMatch.offer_id == f"ax:match:{event_id}"
        ).first()

        match_id = scorealarm_match.id if scorealarm_match else None

        for market in event.markets:
            market_name = market.market_name.lower()

            # Determine market type
            if 'vencedor' in market_name or 'resultado final' in market_name:
                market_type = 'moneyline'
            elif 'handicap' in market_name or 'spread' in market_name:
                market_type = 'spread'
            elif 'total' in market_name or 'mais/menos' in market_name:
                market_type = 'over_under'
            elif 'jogador' in market_name:
                market_type = 'player_prop'
            else:
                market_type = 'other'

            # Parse odds
            team1_odds = None
            team2_odds = None
            draw_odds = None
            line = None
            player_name = None
            prop_type = None

            for odd in market.odds_list:
                outcome = odd.outcome_name.lower()

                if market_type == 'moneyline':
                    if '1' in outcome or event.team1.lower() in outcome:
                        team1_odds = odd.odds
                    elif '2' in outcome or event.team2.lower() in outcome:
                        team2_odds = odd.odds
                    elif 'empate' in outcome or 'draw' in outcome:
                        draw_odds = odd.odds

                elif market_type == 'player_prop':
                    # Parse player prop: "Player Name - Mais de 25.5"
                    if ' - mais de ' in outcome:
                        parts = outcome.split(' - mais de ')
                        player_name = parts[0].title()
                        try:
                            line = float(parts[1])
                        except (ValueError, IndexError):
                            pass
                    elif ' - menos de ' in outcome:
                        parts = outcome.split(' - menos de ')
                        player_name = parts[0].title()
                        try:
                            line = float(parts[1])
                        except (ValueError, IndexError):
                            pass

                    # Extract prop type from market name
                    if 'pontos' in market_name:
                        prop_type = 'points'
                    elif 'rebotes' in market_name:
                        prop_type = 'rebounds'
                    elif 'assistências' in market_name:
                        prop_type = 'assists'
                    elif 'pts+reb+ast' in market_name:
                        prop_type = 'pts_reb_ast'

            # Save to database
            odds_record = OddsHistory(
                match_id=match_id,
                superbet_event_id=event_id,
                market_type=market_type,
                team1_odds=team1_odds,
                team2_odds=team2_odds,
                draw_odds=draw_odds,
                line=line,
                player_name=player_name,
                prop_type=prop_type,
                outcome_name=market.market_name,
                bookmaker='superbet',
                timestamp=datetime.now(timezone.utc),
            )
            db.add(odds_record)
            odds_count += 1

        return odds_count


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Collect odds from Superbet")
    parser.add_argument("--sports", nargs="+", type=int, default=[4, 5],
                        help="Sport IDs to collect (default: 4=Basquete, 5=Futebol)")
    args = parser.parse_args()

    job = PopulateOddsJob(sports=args.sports)
    asyncio.run(job.run())


if __name__ == "__main__":
    main()
