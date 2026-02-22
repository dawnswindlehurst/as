"""Job principal de Paper Trading."""
from sqlalchemy.orm import Session
from jobs.sync_matches import MatchSyncJob
from paper_trading.paper_trader import PaperTrader
from database.scorealarm_models import ScorealarmMatch, ScorealarmSport, ScorealarmTeamRating
from database.paper_trading_models import PaperTradingStats
from analysis.rating_system import EloRating
from analysis.value_detector import ValueBetDetector
from notifications.manager import NotificationManager
from utils.logger import logger as log


class PaperTradingJob:
    """Job principal que roda periodicamente."""
    
    def __init__(self, db: Session):
        self.db = db
        self.sync = MatchSyncJob(db)
        self.trader = PaperTrader(db, min_edge=0.05)
        self.elo = EloRating()
        self.notifier = NotificationManager()
        self.detector = ValueBetDetector(min_edge=0.05)
    
    async def run(self):
        """Executa ciclo completo."""
        log.info("🔄 Iniciando ciclo Paper Trading...")
        
        try:
            # 1. Sync jogos
            await self.sync.run()
            log.info("✅ Sync completo")
            
            # 2. Atualizar ratings dos times
            await self.update_team_ratings()
            log.info("✅ Ratings atualizados")
            
            # 3. Liquidar apostas de jogos finalizados
            await self.trader.settle_all_finished()
            log.info("✅ Apostas liquidadas")
            
            # 4. Buscar novas oportunidades
            opportunities = await self.detector.scan_all_upcoming(self.db)
            
            # Enriquecer oportunidades com nomes das partidas
            for opp in opportunities:
                match = self.db.query(ScorealarmMatch).filter(ScorealarmMatch.id == opp['match_id']).first()
                if match:
                    opp['match_name'] = f"{match.team1_name} vs {match.team2_name}"
            
            # 5. Notificar oportunidades com edge alto
            await self.notifier.notify_all_opportunities(opportunities, min_edge=0.05)
            
            # 6. Apostar automaticamente
            await self.trader.auto_bet_opportunities()
            log.info("✅ Novas apostas registradas")
            
            # 7. Log stats
            self.log_stats()
            
            log.info("✅ Ciclo Paper Trading completo")
        except Exception as e:
            log.error(f"❌ Erro no ciclo Paper Trading: {e}")
            raise
    
    async def update_team_ratings(self):
        """Atualiza ratings baseado em jogos finalizados."""
        # Buscar jogos finalizados recentemente que ainda não foram processados para rating
        finished_matches = self.db.query(ScorealarmMatch).filter(
            ScorealarmMatch.is_finished == True,
            ScorealarmMatch.team1_score.isnot(None),
            ScorealarmMatch.team2_score.isnot(None)
        ).order_by(ScorealarmMatch.finished_at.desc()).limit(100).all()
        
        updated_count = 0
        for match in finished_matches:
            try:
                # Buscar ou criar ratings dos times
                team1_rating = self._get_or_create_rating(match.team1_id)
                team2_rating = self._get_or_create_rating(match.team2_id)
                
                # Determinar resultado (1 = team1 venceu, 0 = team2 venceu, 0.5 = empate)
                if match.team1_score > match.team2_score:
                    result = 1.0
                elif match.team2_score > match.team1_score:
                    result = 0.0
                else:
                    result = 0.5
                
                # Atualizar ratings
                new_rating1, new_rating2 = self.elo.update_ratings(
                    team1_rating.elo_rating,
                    team2_rating.elo_rating,
                    result
                )
                
                team1_rating.elo_rating = new_rating1
                team1_rating.matches_played += 1
                team1_rating.last_match_date = match.finished_at or match.match_date
                
                team2_rating.elo_rating = new_rating2
                team2_rating.matches_played += 1
                team2_rating.last_match_date = match.finished_at or match.match_date
                
                updated_count += 1
            except Exception as e:
                log.error(f"Erro ao atualizar rating do match {match.id}: {e}")
        
        if updated_count > 0:
            self.db.commit()
            log.debug(f"  {updated_count} ratings atualizados")
    
    def _get_or_create_rating(self, team_id: int) -> ScorealarmTeamRating:
        """Busca ou cria rating do time."""
        rating = self.db.query(ScorealarmTeamRating).filter(ScorealarmTeamRating.team_id == team_id).first()
        
        if not rating:
            rating = ScorealarmTeamRating(
                team_id=team_id,
                elo_rating=EloRating.DEFAULT_RATING,
                glicko_rating=1500.0,
                glicko_rd=350.0,
                glicko_vol=0.06
            )
            self.db.add(rating)
        
        return rating
    
    def log_stats(self):
        """Loga estatísticas atuais."""
        stats = self.db.query(PaperTradingStats).all()
        
        if not stats:
            log.info("📊 Nenhuma estatística disponível ainda")
            return
        
        log.info("📊 Estatísticas por Esporte:")
        for s in stats:
            sport = self.db.query(ScorealarmSport).filter(ScorealarmSport.id == s.sport_id).first()
            sport_name = sport.name if sport else f"Sport {s.sport_id}"
            
            win_rate = (s.wins / s.total_bets * 100) if s.total_bets > 0 else 0
            
            log.info(
                f"  {sport_name}: {s.total_bets} bets | "
                f"Win: {s.wins}/{s.total_bets} ({win_rate:.1f}%) | "
                f"ROI: {s.roi*100:.1f}% | "
                f"Profit: R$ {s.total_profit:.2f}"
            )
