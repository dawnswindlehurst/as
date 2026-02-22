"""Base notification provider interface."""
from abc import ABC, abstractmethod
from typing import Dict


class NotificationProvider(ABC):
    """Base para providers de notificação."""
    
    @abstractmethod
    async def send_message(self, message: str) -> bool:
        """Send a plain text message.
        
        Args:
            message: Message text
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def send_opportunity_alert(self, opportunity: dict) -> bool:
        """Send opportunity alert.
        
        Args:
            opportunity: Opportunity dictionary with bet information
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def send_daily_summary(self, stats: dict) -> bool:
        """Send daily summary.
        
        Args:
            stats: Daily statistics dictionary
            
        Returns:
            True if successful
        """
        pass
