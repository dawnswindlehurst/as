"""Discord notifications for Paper Trading."""
import httpx
from notifications.base import NotificationProvider
from utils.logger import logger as log
import os


class DiscordNotifier(NotificationProvider):
    """Notificações via Discord Webhook."""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    
    async def send_message(self, message: str) -> bool:
        """Envia mensagem para o canal."""
        if not self.webhook_url:
            log.warning("⚠️ Discord não configurado")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json={"content": message}
                )
                return response.status_code in [200, 204]
        except Exception as e:
            log.error(f"❌ Erro Discord: {e}")
            return False
    
    async def send_opportunity_alert(self, opp: dict) -> bool:
        """Alerta de oportunidade."""
        message = f"""
🎯 **OPORTUNIDADE DETECTADA!**

🏟️ {opp.get('match_name', 'N/A')}
🎲 Apostar: **{opp['bet_on']}**
💰 Odds: **{opp['odds']:.2f}**
📊 Edge: **{opp['edge']*100:.1f}%**

⚡ Paper Trading ativo
        """
        return await self.send_message(message.strip())
    
    async def send_daily_summary(self, stats: dict) -> bool:
        """Resumo diário."""
        message = f"""
📊 **RESUMO DIÁRIO - CAPIVARA BET**

💰 Profit: R$ {stats.get('daily_profit', 0):.2f}
📈 ROI: {stats.get('roi', 0):.1f}%
🎯 Win Rate: {stats.get('win_rate', 0):.1f}%
✅ Ganhas: {stats.get('wins', 0)} | ❌ Perdidas: {stats.get('losses', 0)}

🦫 Paper Trading Mode
        """
        return await self.send_message(message.strip())
