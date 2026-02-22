"""Telegram bot for notifications."""
import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from config.telegram import telegram_config
from utils.logger import log


class TelegramBot:
    """Telegram bot for sending notifications."""
    
    def __init__(self):
        self.config = telegram_config
        self.bot: Optional[Bot] = None
        
        if self.config.is_enabled():
            try:
                self.bot = Bot(token=self.config.bot_token)
                log.info("Telegram bot initialized")
            except Exception as e:
                log.error(f"Failed to initialize Telegram bot: {e}")
    
    async def _send_async(self, message: str):
        """Send a message asynchronously.
        
        Args:
            message: Message text
        """
        await self.bot.send_message(
            chat_id=self.config.chat_id,
            text=message,
            parse_mode="Markdown"
        )
    
    def send_message(self, message: str) -> bool:
        """Send a message via Telegram.
        
        Args:
            message: Message text
            
        Returns:
            True if successful
        """
        if not self.bot or not self.config.chat_id:
            log.warning("Telegram not configured")
            return False
        
        try:
            asyncio.run(self._send_async(message))
            log.debug(f"Sent Telegram message: {message[:50]}...")
            return True
        except TelegramError as e:
            log.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            log.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_opportunity_alert(self, opportunity: dict) -> bool:
        """Send betting opportunity alert.
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            True if successful
        """
        message = self._format_opportunity(opportunity)
        return self.send_message(message)
    
    def send_result_notification(self, bet: dict) -> bool:
        """Send bet result notification.
        
        Args:
            bet: Bet dictionary
            
        Returns:
            True if successful
        """
        message = self._format_result(bet)
        return self.send_message(message)
    
    def _format_opportunity(self, opp: dict) -> str:
        """Format opportunity as message.
        
        Args:
            opp: Opportunity dictionary
            
        Returns:
            Formatted message
        """
        return f"""
🎯 *Betting Opportunity*

*Match:* {opp.get('team1', 'TBA')} vs {opp.get('team2', 'TBA')}
*Game:* {opp.get('game', 'Unknown')}
*Market:* {opp.get('market_type', 'match_winner')}
*Selection:* {opp.get('selection', '')}

*Bookmaker:* {opp.get('bookmaker', '')}
*Odds:* {opp.get('market_odds', 0):.2f}

*Model Probability:* {opp.get('model_probability', 0):.1%}
*Edge:* {opp.get('edge', 0):.1%}

*Suggested Stake:* R$ {opp.get('stake', 100):.2f}
"""
    
    def _format_result(self, bet: dict) -> str:
        """Format bet result as message.
        
        Args:
            bet: Bet dictionary
            
        Returns:
            Formatted message
        """
        status_emoji = "✅" if bet.get('status') == 'won' else "❌"
        profit = bet.get('profit', 0)
        profit_sign = "+" if profit >= 0 else ""
        
        return f"""
{status_emoji} *Bet Result*

*Match:* {bet.get('team1', 'TBA')} vs {bet.get('team2', 'TBA')}
*Selection:* {bet.get('selection', '')}
*Odds:* {bet.get('odds', 0):.2f}

*Status:* {bet.get('status', '').upper()}
*Profit:* {profit_sign}R$ {profit:.2f}

*Stake:* R$ {bet.get('stake', 0):.2f}
*CLV:* {bet.get('clv', 0):.2%}
"""


# Global bot instance
telegram_bot = TelegramBot()
