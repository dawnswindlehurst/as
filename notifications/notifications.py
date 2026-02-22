"""Notification system."""
from typing import List, Dict
from notifications.bot import telegram_bot
from utils.logger import log


class NotificationSystem:
    """Handle all system notifications."""
    
    def __init__(self):
        self.telegram = telegram_bot
    
    def notify_opportunities(self, opportunities: List[Dict]):
        """Send notifications for new opportunities.
        
        Args:
            opportunities: List of opportunities
        """
        if not opportunities:
            return
        
        log.info(f"Sending notifications for {len(opportunities)} opportunities")
        
        for opp in opportunities:
            self.telegram.send_opportunity_alert(opp)
    
    def notify_results(self, results: List[Dict]):
        """Send notifications for bet results.
        
        Args:
            results: List of bet results
        """
        if not results:
            return
        
        log.info(f"Sending notifications for {len(results)} results")
        
        for result in results:
            self.telegram.send_result_notification(result)
    
    def send_daily_report(self, stats: Dict):
        """Send daily summary report.
        
        Args:
            stats: Statistics dictionary
        """
        message = self._format_daily_report(stats)
        self.telegram.send_message(message)
    
    def _format_daily_report(self, stats: Dict) -> str:
        """Format daily report message.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Formatted message
        """
        return f"""
📊 *Daily Report*

*Today's Bets:* {stats.get('today_bets', 0)}
*Won:* {stats.get('won', 0)}
*Lost:* {stats.get('lost', 0)}
*Win Rate:* {stats.get('win_rate', 0):.1%}

*Today's Profit:* R$ {stats.get('profit', 0):.2f}
*Today's ROI:* {stats.get('roi', 0):.1%}

*Overall Stats:*
*Total Bets:* {stats.get('total_bets', 0)}
*Overall ROI:* {stats.get('overall_roi', 0):.1%}
*Total Profit:* R$ {stats.get('total_profit', 0):.2f}
"""


# Global notification system
notification_system = NotificationSystem()
