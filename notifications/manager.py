"""Notification Manager for multiple channels."""
from typing import List, Optional
from notifications.telegram import TelegramNotifier
from notifications.discord import DiscordNotifier
from notifications.base import NotificationProvider
from utils.logger import logger as log


class NotificationManager:
    """Gerencia múltiplos canais de notificação."""
    
    def __init__(self):
        self.providers: List[NotificationProvider] = []
        
        # Auto-register providers configurados
        telegram = TelegramNotifier()
        if telegram.bot_token:
            self.providers.append(telegram)
            log.info("✅ Telegram configurado")
        
        discord = DiscordNotifier()
        if discord.webhook_url:
            self.providers.append(discord)
            log.info("✅ Discord configurado")
    
    async def notify_opportunity(self, opportunity: dict, min_edge: float = 0.05):
        """Notifica oportunidade se edge >= mínimo."""
        if opportunity.get('edge', 0) < min_edge:
            return
        
        for provider in self.providers:
            try:
                await provider.send_opportunity_alert(opportunity)
            except Exception as e:
                log.error(f"❌ Erro ao notificar: {e}")
    
    async def notify_all_opportunities(self, opportunities: List[dict], min_edge: float = 0.05):
        """Notifica todas as oportunidades com edge alto."""
        high_edge = [o for o in opportunities if o.get('edge', 0) >= min_edge]
        
        for opp in high_edge[:5]:  # Max 5 alertas por vez
            await self.notify_opportunity(opp, min_edge=0)
    
    async def send_daily_summary(self, stats: dict):
        """Envia resumo diário para todos os canais."""
        for provider in self.providers:
            try:
                await provider.send_daily_summary(stats)
            except Exception as e:
                log.error(f"❌ Erro ao enviar resumo: {e}")
    
    async def send_bet_result(self, bet: dict, won: bool):
        """Notifica resultado de aposta."""
        for provider in self.providers:
            if hasattr(provider, 'send_bet_result'):
                try:
                    await provider.send_bet_result(bet, won)
                except Exception as e:
                    log.error(f"❌ Erro ao notificar resultado: {e}")
