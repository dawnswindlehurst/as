"""Job to populate Valorant data from VLR.gg."""
import asyncio
from typing import Optional
from database.db import get_db_session
from database.valorant_models import ValorantTeam, ValorantMatch
from scrapers.vlr import VLRUnified, VLRMatch
from utils.logger import log


class PopulateValorantJob:
    """Job to fetch and store Valorant matches."""
    
    def __init__(self, fetch_rankings: bool = False):
        self.fetch_rankings = fetch_rankings
        self.vlr = VLRUnified()
    
    def run(self):
        """Run the job synchronously."""
        log.info("Starting Valorant database population job")
        try:
            asyncio.run(self._run_async())
        except Exception as e:
            log.error(f"Valorant job failed: {e}")
        finally:
            asyncio.run(self.vlr.close())
        log.info("Valorant population job completed")
    
    async def _run_async(self):
        """Async job execution."""
        # Fetch rankings first if requested
        if self.fetch_rankings:
            await self._fetch_rankings()
        
        # Fetch all matches
        matches = await self.vlr.get_all_matches()
        log.info(f"Fetched {len(matches)} Valorant matches")
        
        # Save to database
        db = get_db_session()
        try:
            upcoming = live = completed = 0
            
            for match in matches:
                saved = self._save_match(db, match)
                if saved:
                    if match.status == "upcoming":
                        upcoming += 1
                    elif match.status == "live":
                        live += 1
                    else:
                        completed += 1
            
            db.commit()
            log.info(f"Saved: {upcoming} upcoming, {live} live, {completed} completed")
            
        except Exception as e:
            db.rollback()
            log.error(f"Error saving Valorant matches: {e}")
            raise
        finally:
            db.close()
    
    async def _fetch_rankings(self):
        """Fetch and save team rankings."""
        teams = await self.vlr.get_all_rankings()
        
        db = get_db_session()
        try:
            for team_data in teams:
                existing = db.query(ValorantTeam).filter_by(name=team_data.name).first()
                
                if existing:
                    existing.rank = team_data.rank
                    existing.region = team_data.region
                    existing.logo = team_data.logo
                    existing.country = team_data.country
                    existing.record = team_data.record
                    existing.wins = team_data.wins
                    existing.losses = team_data.losses
                    existing.earnings = team_data.earnings
                else:
                    team = ValorantTeam(
                        name=team_data.name,
                        logo=team_data.logo,
                        country=team_data.country,
                        region=team_data.region,
                        rank=team_data.rank,
                        record=team_data.record,
                        wins=team_data.wins,
                        losses=team_data.losses,
                        earnings=team_data.earnings,
                    )
                    db.add(team)
            
            db.commit()
            log.info(f"Saved {len(teams)} team rankings")
            
        except Exception as e:
            db.rollback()
            log.error(f"Error saving rankings: {e}")
        finally:
            db.close()
    
    def _save_match(self, db, match: VLRMatch) -> bool:
        """Save a single match to database."""
        if not match.match_id:
            return False
        
        try:
            existing = db.query(ValorantMatch).filter_by(match_id=match.match_id).first()
            
            # Get or create teams
            team1_id = self._get_or_create_team(db, match.team1, match.flag1)
            team2_id = self._get_or_create_team(db, match.team2, match.flag2)
            
            # Determine winner
            winner = None
            if match.status == "completed" and match.team1_score != match.team2_score:
                winner = match.team1 if match.team1_score > match.team2_score else match.team2
            
            if existing:
                existing.team1_score = match.team1_score
                existing.team2_score = match.team2_score
                existing.status = match.status
                existing.winner = winner
                existing.time_until = match.time_until_match
            else:
                new_match = ValorantMatch(
                    match_id=match.match_id,
                    team1_id=team1_id,
                    team2_id=team2_id,
                    team1_name=match.team1,
                    team2_name=match.team2,
                    team1_score=match.team1_score,
                    team2_score=match.team2_score,
                    winner=winner,
                    event=match.match_event,
                    series=match.match_series,
                    time_until=match.time_until_match,
                    status=match.status,
                    url=match.match_page,
                    flag1=match.flag1,
                    flag2=match.flag2,
                )
                db.add(new_match)
            
            return True
            
        except Exception as e:
            log.error(f"Error saving match {match.match_id}: {e}")
            return False
    
    def _get_or_create_team(self, db, name: str, flag: str = "") -> Optional[int]:
        """Get existing team or create new one."""
        if not name or name == "TBD":
            return None
        
        team = db.query(ValorantTeam).filter_by(name=name).first()
        if team:
            return team.id
        
        new_team = ValorantTeam(name=name, country=flag)
        db.add(new_team)
        db.flush()
        return new_team.id


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Populate Valorant data")
    parser.add_argument("--rankings", action="store_true", help="Also fetch team rankings")
    args = parser.parse_args()
    
    job = PopulateValorantJob(fetch_rankings=args.rankings)
    job.run()


if __name__ == "__main__":
    main()
