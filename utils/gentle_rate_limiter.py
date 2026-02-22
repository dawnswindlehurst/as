"""Gentle rate limiter for historical data population."""
import asyncio
from datetime import datetime, timezone
from utils.logger import log


class GentleRateLimiter:
    """Rate limit gentil - não força o servidor."""
    
    def __init__(
        self,
        requests_per_minute: int = 10,  # Bem conservador
        delay_between_requests: float = 3.0,  # 3 segundos entre requests
        delay_between_sports: int = 30,  # 30 segundos entre esportes
        delay_between_tournaments: int = 5,  # 5 segundos entre torneios
        night_mode_speedup: bool = True,  # Mais rápido de madrugada
    ):
        self.rpm = requests_per_minute
        self.delay = delay_between_requests
        self.delay_sport = delay_between_sports
        self.delay_tournament = delay_between_tournaments
        self.night_mode = night_mode_speedup
        
        self.total_requests = 0
        self.start_time = None
    
    def get_current_delay(self) -> float:
        """Delay menor de madrugada (menos tráfego no servidor)."""
        if not self.night_mode:
            return self.delay
        
        hour = datetime.now(timezone.utc).hour
        
        # 02:00 - 05:59 UTC = menos tráfego
        if 2 <= hour < 6:
            return self.delay * 0.5  # 50% mais rápido
        
        return self.delay
    
    async def wait(self):
        """Aguarda entre requests."""
        delay = self.get_current_delay()
        await asyncio.sleep(delay)
        self.total_requests += 1
    
    async def wait_between_sports(self):
        """Pausa maior entre esportes."""
        log.info(f"⏳ Pausa de {self.delay_sport}s entre esportes...")
        await asyncio.sleep(self.delay_sport)
    
    async def wait_between_tournaments(self):
        """Pausa entre torneios."""
        await asyncio.sleep(self.delay_tournament)
    
    def get_stats(self) -> dict:
        """Estatísticas do populamento."""
        if not self.start_time:
            return {}
        
        elapsed = datetime.now(timezone.utc) - self.start_time
        elapsed_minutes = max(elapsed.total_seconds() / 60, 1)
        rate = self.total_requests / elapsed_minutes
        
        return {
            "requests": self.total_requests,
            "elapsed": str(elapsed).split('.')[0],  # HH:MM:SS
            "rate": f"{rate:.1f} req/min"
        }
