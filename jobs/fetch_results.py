"""Fetch results job."""
from utils.logger import log
from scrapers.results import ResultsScraper
from betting.settler import BetSettler
from notifications.notifications import notification_system


def fetch_results_job():
    """Job to fetch match results and settle bets."""
    try:
        log.info("Starting fetch results job")
        
        # Fetch results
        scraper = ResultsScraper()
        results = scraper.fetch_pending_results()
        
        if results:
            log.info(f"Fetched {len(results)} match results")
            
            # Update match results in database
            for result in results:
                scraper.update_match_result(
                    match_id=result["match_id"],
                    winner=result["winner"],
                    team1_score=result["team1_score"],
                    team2_score=result["team2_score"],
                )
        
        # Settle bets
        settler = BetSettler()
        settler.settle_bets()
        
        # Get settlement stats
        stats = settler.get_settlement_stats()
        
        if stats["total_settled"] > 0:
            log.info(f"Settled {stats['total_settled']} bets")
            
            # TODO: Send result notifications if desired
            
    except Exception as e:
        log.error(f"Error in fetch results job: {e}", exc_info=True)
