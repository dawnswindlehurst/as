"""Sistema de Paper Trading."""
from datetime import datetime
from sqlalchemy.orm import Session
from database.paper_trading_models import PaperBet, PaperTradingStats
from database.scorealarm_models import ScorealarmMatch, ScorealarmSport
from analysis.value_detector import ValueBetDetector
from utils.logger import logger as log


class PaperTrader:
    """Sistema de Paper Trading."""
    
    def __init__(self, db: Session, min_edge: float = 0.05, stake: float = 100.0):
        self.db = db
        self.min_edge = min_edge
        self.stake = stake
        self.detector = ValueBetDetector(min_edge=min_edge)
    
    async def place_paper_bet(self, opportunity: dict) -> PaperBet:
        """Registra aposta simulada."""
        bet = PaperBet(
            match_id=opportunity["match_id"],
            bet_on=opportunity["bet_on"],
            odds=opportunity["odds"],
            stake=self.stake,
            our_probability=opportunity["our_probability"],
            implied_probability=opportunity["implied_probability"],
            edge=opportunity["edge"],
            status="pending"
        )
        self.db.add(bet)
        self.db.commit()
        
        log.info(f"📝 Paper bet placed: Match {bet.match_id}, {bet.bet_on} @ {bet.odds}, edge={bet.edge:.2%}")
        return bet
    
    async def settle_bet(self, bet: PaperBet, match: ScorealarmMatch):
        """Liquida aposta baseado no resultado."""
        winner = self._determine_winner(match)
        
        if bet.bet_on == winner:
            bet.status = "won"
            bet.profit = (bet.odds - 1) * bet.stake
        else:
            bet.status = "lost"
            bet.profit = -bet.stake
        
        bet.settled_at = datetime.utcnow()
        self.db.commit()
        
        log.info(f"💰 Bet settled: Match {bet.match_id}, status={bet.status}, profit={bet.profit:.2f}")
        
        # Atualizar stats
        await self._update_stats(match.sport_id, bet)
    
    async def settle_all_finished(self):
        """Liquida todas as apostas de jogos finalizados."""
        pending_bets = self.db.query(PaperBet).filter(
            PaperBet.status == "pending"
        ).all()
        
        settled_count = 0
        for bet in pending_bets:
            match = self.db.query(ScorealarmMatch).filter(
                ScorealarmMatch.id == bet.match_id,
                ScorealarmMatch.is_finished == True
            ).first()
            
            if match:
                await self.settle_bet(bet, match)
                settled_count += 1
        
        log.info(f"✅ {settled_count} apostas liquidadas")
    
    async def auto_bet_opportunities(self):
        """Automaticamente aposta em oportunidades detectadas."""
        opportunities = await self.detector.scan_all_upcoming(self.db)
        
        placed_count = 0
        for opp in opportunities:
            # Verificar se já apostamos neste match
            existing = self.db.query(PaperBet).filter(
                PaperBet.match_id == opp["match_id"],
                PaperBet.bet_on == opp["bet_on"]
            ).first()
            
            if not existing:
                await self.place_paper_bet(opp)
                placed_count += 1
        
        log.info(f"✅ {placed_count} novas apostas registradas de {len(opportunities)} oportunidades")
    
    def _determine_winner(self, match: ScorealarmMatch) -> str:
        """Determina o vencedor do match."""
        if match.team1_score is None or match.team2_score is None:
            return "void"
        
        if match.team1_score > match.team2_score:
            return "team1"
        elif match.team2_score > match.team1_score:
            return "team2"
        return "draw"
    
    async def _update_stats(self, sport_id: int, bet: PaperBet):
        """Atualiza estatísticas do esporte."""
        stats = self.db.query(PaperTradingStats).filter(
            PaperTradingStats.sport_id == sport_id
        ).first()
        
        if not stats:
            stats = PaperTradingStats(sport_id=sport_id)
            self.db.add(stats)
        
        stats.total_bets += 1
        stats.total_staked += bet.stake
        stats.total_profit += bet.profit if bet.profit else 0
        
        if bet.status == "won":
            stats.wins += 1
        elif bet.status == "lost":
            stats.losses += 1
        
        # Recalcular médias
        if stats.total_bets > 0:
            # Calcular avg_odds e avg_edge considerando todas as apostas
            all_bets = self.db.query(PaperBet).join(
                ScorealarmMatch, PaperBet.match_id == ScorealarmMatch.id
            ).filter(
                ScorealarmMatch.sport_id == sport_id
            ).all()
            
            if all_bets:
                stats.avg_odds = sum(b.odds for b in all_bets) / len(all_bets)
                stats.avg_edge = sum(b.edge for b in all_bets) / len(all_bets)
        
        stats.roi = stats.total_profit / stats.total_staked if stats.total_staked > 0 else 0
        
        self.db.commit()
