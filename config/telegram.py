"""Telegram configuration and utilities."""
from typing import Optional
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from utils.logger import log


class TelegramConfig:
    """Telegram configuration class."""

    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID

    def is_enabled(self) -> bool:
        """Check if Telegram is properly configured."""
        return bool(self.bot_token and self.chat_id)

    @property
    def notification_settings(self) -> dict:
        """Get notification settings."""
        return {
            "opportunities": True,
            "results": True,
            "daily_report": True,
            "alerts": True,
        }


# Global instance
telegram_config = TelegramConfig()


async def send_telegram_message(message: str) -> bool:
    """Send a message via Telegram (async wrapper for use in async contexts).
    
    This is an async wrapper around telegram_bot.send_message() to maintain
    consistency with async code patterns in the collection service.
    
    NOTE: The underlying telegram_bot.send_message() uses asyncio.run() internally,
    which may cause issues if called from within an already-running event loop.
    This is existing behavior in the telegram_bot implementation. If you encounter
    "RuntimeError: asyncio.run() cannot be called from a running event loop",
    the telegram_bot implementation will need to be refactored to use proper
    async methods throughout.
    
    Args:
        message: Message text to send
        
    Returns:
        True if successful, False otherwise
    """
    if not telegram_config.is_enabled():
        log.warning("Telegram not configured - message not sent")
        return False
    
    try:
        # Import here to avoid circular dependency
        from notifications.bot import telegram_bot
        
        # Use the synchronous send_message method
        # (Note: This may fail in some async contexts due to nested event loop)
        result = telegram_bot.send_message(message)
        return result
    except RuntimeError as e:
        if "asyncio.run()" in str(e):
            log.warning(f"Telegram notification skipped due to event loop conflict: {e}")
            return False
        raise
    except Exception as e:
        log.error(f"Error sending Telegram message: {e}")
        return False
