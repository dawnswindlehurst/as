"""Daily report job."""
from datetime import datetime, timedelta
from utils.logger import log
from betting.analyzer import BetAnalyzer
from notifications.notifications import notification_system
from database.db import get_db
from database.models import Bet


def daily_report_job():
    """Job to send daily summary report."""
    try:
        log.info("Generating daily report")
        
        analyzer = BetAnalyzer()
        
        # Get today's bets
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        with get_db() as db:
            today_bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.settled_at >= today_start,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            today_wins = sum(1 for b in today_bets if b.status == "won")
            today_profit = sum(b.profit for b in today_bets)
            today_stake = sum(b.stake for b in today_bets)
        
        # Get overall stats
        overall_stats = analyzer.get_overall_stats()
        
        stats = {
            "today_bets": len(today_bets),
            "won": today_wins,
            "lost": len(today_bets) - today_wins,
            "win_rate": today_wins / len(today_bets) if today_bets else 0,
            "profit": today_profit,
            "roi": (today_profit / today_stake) if today_stake > 0 else 0,
            "total_bets": overall_stats.get("total_bets", 0),
            "overall_roi": overall_stats.get("roi", 0),
            "total_profit": overall_stats.get("total_profit", 0),
        }
        
        # Send report
        notification_system.send_daily_report(stats)
        
        log.info("Daily report sent")
        
    except Exception as e:
        log.error(f"Error in daily report job: {e}", exc_info=True)
