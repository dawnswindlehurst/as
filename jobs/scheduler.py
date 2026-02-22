"""Job scheduler using APScheduler."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from config.settings import (
    FETCH_ODDS_INTERVAL_MINUTES,
    GENERATE_BETS_INTERVAL_MINUTES,
    FETCH_RESULTS_INTERVAL_MINUTES,
    DAILY_REPORT_HOUR,
)
from utils.logger import log
from jobs.generate_bets import generate_bets_job
from jobs.fetch_results import fetch_results_job
from jobs.daily_report import daily_report_job


class JobScheduler:
    """Scheduler for automated jobs."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """Start the scheduler."""
        # Generate bets job
        self.scheduler.add_job(
            generate_bets_job,
            IntervalTrigger(minutes=GENERATE_BETS_INTERVAL_MINUTES),
            id="generate_bets",
            name="Generate bet suggestions",
            replace_existing=True,
        )
        
        # Fetch results job
        self.scheduler.add_job(
            fetch_results_job,
            IntervalTrigger(minutes=FETCH_RESULTS_INTERVAL_MINUTES),
            id="fetch_results",
            name="Fetch match results",
            replace_existing=True,
        )
        
        # Daily report job
        self.scheduler.add_job(
            daily_report_job,
            CronTrigger(hour=DAILY_REPORT_HOUR, minute=0),
            id="daily_report",
            name="Send daily report",
            replace_existing=True,
        )
        
        self.scheduler.start()
        log.info("Job scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        log.info("Job scheduler stopped")
    
    def list_jobs(self):
        """List all scheduled jobs."""
        return self.scheduler.get_jobs()


# Global scheduler instance
job_scheduler = JobScheduler()
