"""Job para resumo diário às 21h UTC."""
from datetime import datetime, timedelta
from database.db import get_db_session
from database.paper_trading_models import PaperBet, PaperTradingStats
from database.scorealarm_models import ScorealarmSport
from notifications.manager import NotificationManager
from utils.logger import logger as log


class DailySummaryJob:
    """Envia resumo diário às 21h UTC."""
    
    def __init__(self):
        self.db = get_db_session()
        self.notifier = NotificationManager()
    
    async def run(self):
        """Calcula e envia resumo diário."""
        log.info("📊 Gerando resumo diário...")
        
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Bets do dia
            daily_bets = self.db.query(PaperBet).filter(
                PaperBet.settled_at >= today_start
            ).all()
            
            wins = len([b for b in daily_bets if b.status == "won"])
            losses = len([b for b in daily_bets if b.status == "lost"])
            daily_profit = sum(b.profit for b in daily_bets if b.profit)
            
            pending = self.db.query(PaperBet).filter(PaperBet.status == "pending").count()
            
            # Top esporte
            top_sport = self.db.query(PaperTradingStats).order_by(
                PaperTradingStats.roi.desc()
            ).first()
            
            top_sport_name = "N/A"
            if top_sport:
                sport = self.db.query(ScorealarmSport).filter(
                    ScorealarmSport.id == top_sport.sport_id
                ).first()
                top_sport_name = sport.name if sport else "N/A"
            
            stats = {
                "daily_profit": daily_profit,
                "wins": wins,
                "losses": losses,
                "win_rate": (wins / max(wins + losses, 1)) * 100,
                "roi": (daily_profit / max((wins + losses) * 100, 1)) * 100,
                "pending": pending,
                "top_sport": top_sport_name
            }
            
            await self.notifier.send_daily_summary(stats)
            log.info("✅ Resumo diário enviado")
            
        except Exception as e:
            log.error(f"❌ Erro ao gerar resumo diário: {e}")
        finally:
            self.db.close()
