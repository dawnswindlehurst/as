"""Telegram notifications for Paper Trading."""
import httpx
from typing import Optional
from notifications.base import NotificationProvider
from utils.logger import logger as log
import os


class TelegramNotifier(NotificationProvider):
    """Notificações via Telegram Bot."""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
    
    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Envia mensagem para o chat."""
        if not self.bot_token or not self.chat_id:
            log.warning("⚠️ Telegram não configurado")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": parse_mode
                    }
                )
                return response.status_code == 200
        except Exception as e:
            log.error(f"❌ Erro Telegram: {e}")
            return False
    
    async def send_opportunity_alert(self, opp: dict) -> bool:
        """Alerta de oportunidade com edge alto."""
        message = f"""
🎯 <b>OPORTUNIDADE DETECTADA!</b>

🏟️ {opp.get('match_name', 'N/A')}
🎲 Apostar: <b>{opp['bet_on']}</b>
💰 Odds: <b>{opp['odds']:.2f}</b>
📊 Edge: <b>{opp['edge']*100:.1f}%</b>

📈 Nossa prob: {opp['our_probability']*100:.1f}%
📉 Prob implícita: {opp['implied_probability']*100:.1f}%

⚡ Paper Trading ativo
        """
        return await self.send_message(message.strip())
    
    async def send_daily_summary(self, stats: dict) -> bool:
        """Resumo diário de performance."""
        message = f"""
📊 <b>RESUMO DIÁRIO - CAPIVARA BET</b>

💰 Profit hoje: R$ {stats.get('daily_profit', 0):.2f}
📈 ROI: {stats.get('roi', 0):.1f}%
🎯 Win Rate: {stats.get('win_rate', 0):.1f}%

✅ Ganhas: {stats.get('wins', 0)}
❌ Perdidas: {stats.get('losses', 0)}
⏳ Pendentes: {stats.get('pending', 0)}

🏆 Top esporte: {stats.get('top_sport', 'N/A')}

🦫 Paper Trading Mode
        """
        return await self.send_message(message.strip())
    
    async def send_bet_result(self, bet: dict, won: bool) -> bool:
        """Notifica resultado de aposta."""
        emoji = "✅" if won else "❌"
        profit = bet.get('profit', 0)
        
        message = f"""
{emoji} <b>APOSTA {'GANHA' if won else 'PERDIDA'}</b>

🏟️ {bet.get('match_name', 'N/A')}
🎲 Apostou: {bet['bet_on']}
💰 Odds: {bet['odds']:.2f}
📊 Profit: R$ {profit:+.2f}
        """
        return await self.send_message(message.strip())
