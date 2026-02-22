"""Job de sincronização inteligente de partidas."""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from scrapers.superbet import ScorealarmClient
from database.scorealarm_models import (
    ScorealarmMatch, ScorealarmSport, ScorealarmTeam, 
    ScorealarmTournament, ScorealarmCategory, ScorealarmSeason, OddsHistory
)
from utils.logger import logger as log


class MatchSyncJob:
    """Sincroniza jogos de forma inteligente."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def sync_upcoming(self, hours: int = 48):
        """Busca jogos das próximas 48h para apostar."""
        log.info(f"🔍 Sincronizando jogos das próximas {hours} horas...")
        
        async with ScorealarmClient() as client:
            # Buscar jogos futuros de cada esporte
            sports = self.db.query(ScorealarmSport).all()
            total_synced = 0
            
            for sport in sports:
                try:
                    # Aqui você implementaria a busca de jogos usando o ScorealarmClient
                    # Por enquanto apenas logamos
                    log.debug(f"  Processando {sport.name}...")
                    # matches = await client.get_upcoming_matches(sport.id, hours=hours)
                    # total_synced += len(matches)
                except Exception as e:
                    log.error(f"  Erro ao buscar jogos de {sport.name}: {e}")
            
            log.info(f"✅ {total_synced} jogos futuros sincronizados")
    
    async def sync_finished(self, hours: int = 2):
        """Busca jogos finalizados das últimas 2h para liquidar apostas."""
        log.info(f"🏁 Sincronizando jogos finalizados das últimas {hours} horas...")
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Buscar jogos recentes que ainda não foram marcados como finalizados
        pending_matches = self.db.query(ScorealarmMatch).filter(
            ScorealarmMatch.match_date >= cutoff,
            ScorealarmMatch.is_finished == False
        ).all()
        
        updated_count = 0
        async with ScorealarmClient() as client:
            for match in pending_matches:
                try:
                    # Aqui você implementaria a busca de resultados
                    # Por enquanto apenas marcamos como exemplo
                    # result = await client.get_match_result(match.platform_id)
                    # if result and result.is_finished:
                    #     match.is_finished = True
                    #     match.team1_score = result.team1_score
                    #     match.team2_score = result.team2_score
                    #     match.finished_at = datetime.utcnow()
                    #     updated_count += 1
                    pass
                except Exception as e:
                    log.error(f"  Erro ao atualizar match {match.id}: {e}")
        
        if updated_count > 0:
            self.db.commit()
        
        log.info(f"✅ {updated_count} jogos marcados como finalizados")
    
    async def sync_odds(self):
        """Atualiza odds dos jogos pendentes."""
        log.info("💰 Atualizando odds dos jogos pendentes...")
        
        # Buscar jogos futuros
        now = datetime.utcnow()
        future = now + timedelta(hours=48)
        
        upcoming_matches = self.db.query(ScorealarmMatch).filter(
            ScorealarmMatch.match_date >= now,
            ScorealarmMatch.match_date <= future,
            ScorealarmMatch.is_finished == False
        ).all()
        
        odds_updated = 0
        async with ScorealarmClient() as client:
            for match in upcoming_matches:
                try:
                    # Aqui você implementaria a busca de odds
                    # Por enquanto apenas logamos
                    # odds = await client.get_match_odds(match.offer_id)
                    # if odds:
                    #     odds_history = OddsHistory(
                    #         match_id=match.id,
                    #         market_type="moneyline",
                    #         team1_odds=odds.team1,
                    #         team2_odds=odds.team2,
                    #         bookmaker="superbet"
                    #     )
                    #     self.db.add(odds_history)
                    #     odds_updated += 1
                    pass
                except Exception as e:
                    log.error(f"  Erro ao atualizar odds do match {match.id}: {e}")
        
        if odds_updated > 0:
            self.db.commit()
        
        log.info(f"✅ Odds atualizadas para {odds_updated} jogos")
    
    async def run(self):
        """Executa sync completo."""
        log.info("🔄 Iniciando sincronização completa...")
        await self.sync_upcoming()
        await self.sync_finished()
        await self.sync_odds()
        log.info("✅ Sincronização completa")
