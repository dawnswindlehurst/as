"""Data collection service for Oracle Cloud deployment."""
import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from database.models import CollectionStatus, Match, Odds
from config.oracle import (
    COLLECTION_INTERVAL_HOURS,
    INITIAL_COLLECTION_DAYS,
    ENABLE_INITIAL_COLLECTION,
    RATE_LIMITS,
    MAX_WORKERS,
    BATCH_SIZE,
    NOTIFY_ON_COLLECTION_COMPLETE,
    NOTIFY_ON_ERROR,
    ODDS_MATCH_TIME_WINDOW_HOURS,
)
from config.telegram import send_telegram_message
from utils.logger import log
import json

# Import esports scrapers
from scrapers.hltv.hltv_unified import HLTVUnified
from scrapers.vlr.vlr_unified import VLRUnified
from scrapers.dota import DotaUnified
from scrapers.lol.lol_unified import LoLUnified

# Import odds scrapers
from scrapers.scraper_manager import scraper_manager
from scrapers.active.superbet import SuperbetScraper
from scrapers.active.stake import StakeScraper


class CollectionService:
    """Service for managing data collection from all sources."""
    
    def __init__(self):
        self.interval_hours = COLLECTION_INTERVAL_HOURS
        self.initial_days = INITIAL_COLLECTION_DAYS
        self.scheduler = AsyncIOScheduler()
        self.rate_limiters: Dict[str, asyncio.Semaphore] = {}
        
        # Initialize rate limiters
        for source, limit in RATE_LIMITS.items():
            self.rate_limiters[source] = asyncio.Semaphore(limit)
        
        # Register odds scrapers on initialization
        if not scraper_manager.has_scrapers():
            scraper_manager.register_scraper(SuperbetScraper())
            scraper_manager.register_scraper(StakeScraper())
            log.info("Registered odds scrapers (Superbet, Stake)")
    
    def get_db(self) -> Session:
        """Get database session."""
        return SessionLocal()
    
    def is_initial_collection_done(self, db: Session) -> bool:
        """Check if initial collection has been completed."""
        status = db.query(CollectionStatus).filter(
            CollectionStatus.collection_type == "initial",
            CollectionStatus.status == "completed"
        ).first()
        
        return status is not None
    
    def create_collection_record(
        self, 
        db: Session, 
        collection_type: str, 
        source: str, 
        game: Optional[str] = None
    ) -> CollectionStatus:
        """Create a new collection status record."""
        record = CollectionStatus(
            collection_type=collection_type,
            source=source,
            game=game,
            status="pending",
            started_at=datetime.utcnow()
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    def update_collection_status(
        self,
        db: Session,
        record_id: int,
        status: str,
        processed: Optional[int] = None,
        failed: Optional[int] = None,
        total: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Update collection status record."""
        record = db.query(CollectionStatus).filter(
            CollectionStatus.id == record_id
        ).first()
        
        if record:
            record.status = status
            if processed is not None:
                record.processed_items = processed
            if failed is not None:
                record.failed_items = failed
            if total is not None:
                record.total_items = total
            if error_message:
                record.error_message = error_message
            
            if status == "completed":
                record.completed_at = datetime.utcnow()
                record.last_collection_at = datetime.utcnow()
            elif status == "failed":
                record.retry_count = (record.retry_count or 0) + 1
            
            record.updated_at = datetime.utcnow()
            db.commit()
    
    async def collect_with_rate_limit(
        self,
        source: str,
        collect_func,
        *args,
        **kwargs
    ):
        """Execute collection function with rate limiting."""
        semaphore = self.rate_limiters.get(source)
        if semaphore:
            async with semaphore:
                return await collect_func(*args, **kwargs)
        else:
            return await collect_func(*args, **kwargs)
    
    async def collect_traditional_sports_data(
        self,
        db: Session,
        collection_type: str,
        days_back: Optional[int] = None
    ):
        """Collect traditional sports data (NBA, Football, Tennis)."""
        log.info(f"Starting traditional sports data collection ({collection_type})")
        
        sources = [
            ("scorealarm", "nba", "NBA"),
            ("scorealarm", "football", "Football"),
            ("scorealarm", "tennis", "Tennis"),
        ]
        
        for source, game, display_name in sources:
            record = self.create_collection_record(db, collection_type, source, game)
            
            try:
                log.info(f"Collecting {display_name} data...")
                record = db.query(CollectionStatus).filter(
                    CollectionStatus.id == record.id
                ).first()
                record.status = "running"
                db.commit()
                
                # TODO: Implement actual traditional sports scraping
                # For now, simulate collection
                await asyncio.sleep(2)
                
                self.update_collection_status(
                    db, record.id, "completed",
                    processed=0, total=0
                )
                log.info(f"{display_name} data collection completed")
                
            except Exception as e:
                log.error(f"Error collecting {display_name} data: {str(e)}")
                self.update_collection_status(
                    db, record.id, "failed",
                    error_message=str(e)
                )
    
    async def collect_esports_data(
        self,
        db: Session,
        collection_type: str,
        days_back: Optional[int] = None
    ):
        """Collect esports data (HLTV, VLR, OpenDota, LoL)."""
        log.info(f"Starting esports data collection ({collection_type})")
        
        sources = [
            ("hltv", "cs2", "CS2/HLTV", HLTVUnified),
            ("vlr", "valorant", "Valorant", VLRUnified),
            ("opendota", "dota2", "Dota 2", DotaUnified),
            ("lol", "lol", "League of Legends", LoLUnified),
        ]
        
        for source, game, display_name, scraper_class in sources:
            record = self.create_collection_record(db, collection_type, source, game)
            
            try:
                log.info(f"Collecting {display_name} data...")
                record = db.query(CollectionStatus).filter(
                    CollectionStatus.id == record.id
                ).first()
                record.status = "running"
                db.commit()
                
                # Initialize scraper
                scraper = scraper_class()
                matches_saved = 0
                
                # Fetch matches based on the scraper type
                if source == "hltv":
                    # Get recent results for historical data
                    if collection_type == "initial" and days_back:
                        matches = await scraper.get_results(limit=100)
                    else:
                        # Get upcoming matches for periodic collection
                        matches = await scraper.get_matches(limit=50)
                    
                    # Save matches to database
                    for match in matches:
                        try:
                            # Check if match already exists
                            existing = db.query(Match).filter(
                                Match.game == game,
                                Match.team1 == match.team1.name,
                                Match.team2 == match.team2.name,
                                Match.start_time == match.date
                            ).first()
                            
                            if not existing:
                                db_match = Match(
                                    game=game,
                                    team1=match.team1.name,
                                    team2=match.team2.name,
                                    start_time=match.date,
                                    tournament=match.event.name if hasattr(match, 'event') and match.event else None,
                                    best_of=match.format if hasattr(match, 'format') else 1
                                )
                                db.add(db_match)
                                matches_saved += 1
                        except Exception as e:
                            db.rollback()
                            log.error(f"Error saving HLTV match: {e}")
                            continue
                
                elif source == "vlr":
                    # Get matches from VLR
                    if collection_type == "initial" and days_back:
                        matches = await scraper.get_results(num_pages=3)
                    else:
                        matches = await scraper.get_upcoming_matches()
                    
                    # Save matches to database
                    for match in matches:
                        try:
                            # ValorantResult uses time_completed (for results)
                            # ValorantMatch uses unix_timestamp (for upcoming)
                            match_time = None
                            if hasattr(match, 'unix_timestamp') and match.unix_timestamp:
                                # This is a ValorantMatch with unix_timestamp - convert to datetime
                                try:
                                    match_time = datetime.fromtimestamp(int(match.unix_timestamp))
                                except (ValueError, TypeError):
                                    match_time = None
                            
                            # Skip if we don't have a valid datetime
                            if not match_time:
                                continue
                            
                            # Check if match already exists
                            existing = db.query(Match).filter(
                                Match.game == game,
                                Match.team1 == match.team1,
                                Match.team2 == match.team2,
                                Match.start_time == match_time
                            ).first()
                            
                            if not existing:
                                # Try to extract best_of from match_series if available
                                best_of = 1  # Default
                                if hasattr(match, 'match_series') and match.match_series:
                                    series_lower = match.match_series.lower()
                                    if 'bo5' in series_lower or 'best of 5' in series_lower:
                                        best_of = 5
                                    elif 'bo3' in series_lower or 'best of 3' in series_lower:
                                        best_of = 3
                                
                                db_match = Match(
                                    game=game,
                                    team1=match.team1,
                                    team2=match.team2,
                                    start_time=match_time,
                                    tournament=match.match_event if hasattr(match, 'match_event') else None,
                                    best_of=best_of
                                )
                                db.add(db_match)
                                matches_saved += 1
                        except Exception as e:
                            db.rollback()
                            log.error(f"Error saving VLR match: {e}")
                            continue
                
                elif source == "opendota":
                    # Get Dota 2 matches
                    matches = await scraper.get_pro_matches(limit=100 if collection_type == "initial" else 50)
                    
                    # Save matches to database
                    for match in matches:
                        try:
                            # Convert Unix timestamp to datetime
                            match_start_time = datetime.fromtimestamp(match.start_time) if match.start_time else None
                            
                            # Check if match already exists
                            existing = db.query(Match).filter(
                                Match.game == game,
                                Match.team1 == match.radiant_name,
                                Match.team2 == match.dire_name,
                                Match.start_time == match_start_time
                            ).first()
                            
                            if not existing:
                                db_match = Match(
                                    game=game,
                                    team1=match.radiant_name or f"Team {match.radiant_team_id}",
                                    team2=match.dire_name or f"Team {match.dire_team_id}",
                                    start_time=match_start_time,
                                    tournament=match.league_name,
                                    finished=True,
                                    winner=match.radiant_name if match.radiant_win else match.dire_name,
                                    team1_score=1 if match.radiant_win else 0,
                                    team2_score=0 if match.radiant_win else 1
                                )
                                db.add(db_match)
                                matches_saved += 1
                        except Exception as e:
                            db.rollback()
                            log.error(f"Error saving Dota match: {e}")
                            continue
                
                elif source == "lol":
                    # Get LoL matches
                    if collection_type == "initial" and days_back:
                        matches = await scraper.get_completed_matches()
                    else:
                        matches = await scraper.get_upcoming_matches()
                    
                    # Save matches to database
                    for match in matches:
                        try:
                            # LoLMatch from lolesports_client.py uses team1_name/team2_name and start_time (string)
                            # Parse start_time from ISO 8601 string to datetime
                            match_start_time = None
                            if hasattr(match, 'start_time') and match.start_time:
                                try:
                                    # Parse ISO 8601 datetime string
                                    match_start_time = datetime.fromisoformat(match.start_time.replace('Z', '+00:00'))
                                except (ValueError, AttributeError):
                                    match_start_time = None
                            
                            # Get team names - LoLMatch from lolesports_client uses team1_name/team2_name
                            team1_name = match.team1_name if hasattr(match, 'team1_name') else str(match.team1)
                            team2_name = match.team2_name if hasattr(match, 'team2_name') else str(match.team2)
                            
                            existing = db.query(Match).filter(
                                Match.game == game,
                                Match.team1 == team1_name,
                                Match.team2 == team2_name,
                                Match.start_time == match_start_time
                            ).first()
                            
                            if not existing:
                                # Get league name
                                league_name = match.league_name if hasattr(match, 'league_name') else None
                                
                                db_match = Match(
                                    game=game,
                                    team1=team1_name,
                                    team2=team2_name,
                                    start_time=match_start_time,
                                    tournament=league_name,
                                    best_of=match.best_of if hasattr(match, 'best_of') else 1
                                )
                                db.add(db_match)
                                matches_saved += 1
                        except Exception as e:
                            db.rollback()
                            log.error(f"Error saving LoL match: {e}")
                            continue
                
                # Commit all matches
                db.commit()
                
                # Close the scraper if it has a close method
                if hasattr(scraper, 'close'):
                    await scraper.close()
                
                self.update_collection_status(
                    db, record.id, "completed",
                    processed=matches_saved, total=matches_saved
                )
                log.info(f"{display_name} data collection completed - {matches_saved} matches saved")
                
            except Exception as e:
                log.error(f"Error collecting {display_name} data: {str(e)}")
                self.update_collection_status(
                    db, record.id, "failed",
                    error_message=str(e)
                )
    
    async def collect_odds_data(
        self,
        db: Session,
        collection_type: str,
        days_back: Optional[int] = None
    ):
        """Collect odds data from Superbet and Stake."""
        log.info(f"Starting odds data collection ({collection_type})")
        
        record = self.create_collection_record(db, collection_type, "bookmakers")
        
        try:
            log.info("Collecting odds from enabled bookmakers...")
            record = db.query(CollectionStatus).filter(
                CollectionStatus.id == record.id
            ).first()
            record.status = "running"
            db.commit()
            
            # Fetch odds from all enabled scrapers (registered during initialization)
            odds_by_bookmaker = await scraper_manager.fetch_all_odds()
            
            total_odds_saved = 0
            
            # Process odds from each bookmaker
            for bookmaker, odds_list in odds_by_bookmaker.items():
                log.info(f"Processing {len(odds_list)} odds from {bookmaker}")
                
                for odds_data in odds_list:
                    try:
                        # Find matching match in database
                        # Try to match by team names and approximate time
                        team_home = odds_data.team_home
                        team_away = odds_data.team_away
                        
                        # Look for a match within configured time window of the odds timestamp
                        time_window_start = odds_data.timestamp - timedelta(hours=ODDS_MATCH_TIME_WINDOW_HOURS)
                        time_window_end = odds_data.timestamp + timedelta(hours=ODDS_MATCH_TIME_WINDOW_HOURS)
                        
                        match = db.query(Match).filter(
                            Match.team1 == team_home,
                            Match.team2 == team_away,
                            Match.start_time >= time_window_start,
                            Match.start_time <= time_window_end
                        ).first()
                        
                        if not match:
                            # Try reverse team order
                            match = db.query(Match).filter(
                                Match.team1 == team_away,
                                Match.team2 == team_home,
                                Match.start_time >= time_window_start,
                                Match.start_time <= time_window_end
                            ).first()
                        
                        if match:
                            # Check if odds already exist for this match and bookmaker
                            existing_odds = db.query(Odds).filter(
                                Odds.match_id == match.id,
                                Odds.bookmaker == bookmaker,
                                Odds.market_type == "match_winner"
                            ).first()
                            
                            if not existing_odds:
                                # Create new odds entry
                                db_odds = Odds(
                                    match_id=match.id,
                                    bookmaker=bookmaker,
                                    market_type="match_winner",
                                    team1_odds=odds_data.odds_home,
                                    team2_odds=odds_data.odds_away,
                                    draw_odds=odds_data.odds_draw,
                                    timestamp=odds_data.timestamp
                                )
                                db.add(db_odds)
                                total_odds_saved += 1
                            else:
                                # Update existing odds
                                existing_odds.team1_odds = odds_data.odds_home
                                existing_odds.team2_odds = odds_data.odds_away
                                existing_odds.draw_odds = odds_data.odds_draw
                                existing_odds.timestamp = odds_data.timestamp
                                total_odds_saved += 1
                        else:
                            log.debug(f"No matching match found for odds: {team_home} vs {team_away}")
                    
                    except Exception as e:
                        log.error(f"Error saving odds from {bookmaker}: {e}")
                        continue
            
            # Commit all odds
            db.commit()
            
            self.update_collection_status(
                db, record.id, "completed",
                processed=total_odds_saved, total=total_odds_saved
            )
            log.info(f"Odds collection completed - {total_odds_saved} odds saved")
            
        except Exception as e:
            log.error(f"Error collecting odds: {str(e)}")
            self.update_collection_status(
                db, record.id, "failed",
                error_message=str(e)
            )
    
    async def run_initial_collection(self):
        """Execute initial retroactive data collection."""
        log.info("=" * 80)
        log.info("STARTING INITIAL DATA COLLECTION")
        log.info(f"Collecting data from last {self.initial_days} days")
        log.info("=" * 80)
        
        db = self.get_db()
        
        try:
            # Check if already done
            if self.is_initial_collection_done(db):
                log.info("Initial collection already completed, skipping...")
                return
            
            start_time = datetime.utcnow()
            
            # Collect all data sources
            await self.collect_traditional_sports_data(db, "initial", self.initial_days)
            await self.collect_esports_data(db, "initial", self.initial_days)
            await self.collect_odds_data(db, "initial", self.initial_days)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            log.info("=" * 80)
            log.info(f"INITIAL COLLECTION COMPLETED in {duration:.2f} seconds")
            log.info("=" * 80)
            
            # Send notification
            if NOTIFY_ON_COLLECTION_COMPLETE:
                message = (
                    f"✅ *Initial Data Collection Complete*\n\n"
                    f"Duration: {duration:.2f} seconds\n"
                    f"Historical data from last {self.initial_days} days loaded."
                )
                try:
                    await send_telegram_message(message)
                except Exception as e:
                    log.warning(f"Failed to send Telegram notification: {str(e)}")
        
        except Exception as e:
            log.error(f"Initial collection failed: {str(e)}")
            
            if NOTIFY_ON_ERROR:
                message = (
                    f"❌ *Initial Data Collection Failed*\n\n"
                    f"Error: {str(e)}"
                )
                try:
                    await send_telegram_message(message)
                except Exception as ex:
                    log.warning(f"Failed to send Telegram notification: {str(ex)}")
            
            raise
        
        finally:
            db.close()
    
    async def run_periodic_collection(self):
        """Execute periodic data collection (every X hours)."""
        log.info("Starting periodic data collection...")
        
        db = self.get_db()
        
        try:
            start_time = datetime.utcnow()
            
            # Collect only new data (no historical lookback)
            await self.collect_traditional_sports_data(db, "periodic")
            await self.collect_esports_data(db, "periodic")
            await self.collect_odds_data(db, "periodic")
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            log.info(f"Periodic collection completed in {duration:.2f} seconds")
        
        except Exception as e:
            log.error(f"Periodic collection failed: {str(e)}")
            
            if NOTIFY_ON_ERROR:
                message = (
                    f"⚠️ *Periodic Collection Error*\n\n"
                    f"Error: {str(e)}"
                )
                try:
                    await send_telegram_message(message)
                except Exception as ex:
                    log.warning(f"Failed to send Telegram notification: {str(ex)}")
        
        finally:
            db.close()
    
    async def start(self):
        """Start the collection service."""
        log.info("=" * 80)
        log.info("CAPIVARA BET COLLECTION SERVICE")
        log.info(f"Collection Interval: {self.interval_hours} hours")
        log.info(f"Initial Collection: {ENABLE_INITIAL_COLLECTION}")
        log.info(f"Initial Days: {self.initial_days}")
        log.info("=" * 80)
        
        # Run initial collection if enabled and not done
        if ENABLE_INITIAL_COLLECTION:
            db = self.get_db()
            try:
                if not self.is_initial_collection_done(db):
                    await self.run_initial_collection()
                else:
                    log.info("Initial collection already completed")
            finally:
                db.close()
        
        # Schedule periodic collection
        self.scheduler.add_job(
            self.run_periodic_collection,
            IntervalTrigger(hours=self.interval_hours),
            id="periodic_collection",
            name="Periodic Data Collection",
            replace_existing=True,
        )
        
        log.info(f"Scheduled periodic collection every {self.interval_hours} hours")
        
        # Start scheduler
        self.scheduler.start()
        log.info("Collection service started successfully")
        
        # Keep service running
        try:
            while True:
                await asyncio.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            log.info("Shutting down collection service...")
            self.scheduler.shutdown()


async def main():
    """Main entry point."""
    service = CollectionService()
    await service.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Collection service stopped by user")
    except Exception as e:
        log.error(f"Collection service error: {str(e)}")
        sys.exit(1)
