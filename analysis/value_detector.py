"""Detecção de Value Bets."""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from analysis.rating_system import EloRating
from database.scorealarm_models import ScorealarmMatch, OddsHistory, ScorealarmTeamRating


class ValueBetDetector:
    """Detecta apostas com edge positivo."""
    
    def __init__(self, min_edge: float = 0.03):  # 3% mínimo
        self.min_edge = min_edge
        self.elo = EloRating()
    
    def odds_to_probability(self, odds: float) -> float:
        """Converte odds decimal para probabilidade implícita."""
        if odds <= 1.0:
            return 0.0
        return 1 / odds
    
    def calculate_edge(self, our_probability: float, bookmaker_odds: float) -> float:
        """Calcula edge: nossa prob - prob implícita."""
        implied_prob = self.odds_to_probability(bookmaker_odds)
        return our_probability - implied_prob
    
    def analyze_match(self, match: ScorealarmMatch, team1_rating: float, team2_rating: float, odds: OddsHistory) -> List[dict]:
        """Analisa match e retorna oportunidades."""
        
        # Probabilidade baseada em ELO
        our_prob_team1 = self.elo.calculate_expected(team1_rating, team2_rating)
        our_prob_team2 = 1 - our_prob_team1
        
        # Edge
        edge_team1 = self.calculate_edge(our_prob_team1, odds.team1_odds)
        edge_team2 = self.calculate_edge(our_prob_team2, odds.team2_odds)
        
        opportunities = []
        
        if edge_team1 >= self.min_edge:
            opportunities.append({
                "match_id": match.id,
                "bet_on": "team1",
                "odds": odds.team1_odds,
                "our_probability": our_prob_team1,
                "implied_probability": self.odds_to_probability(odds.team1_odds),
                "edge": edge_team1
            })
        
        if edge_team2 >= self.min_edge:
            opportunities.append({
                "match_id": match.id,
                "bet_on": "team2",
                "odds": odds.team2_odds,
                "our_probability": our_prob_team2,
                "implied_probability": self.odds_to_probability(odds.team2_odds),
                "edge": edge_team2
            })
        
        return opportunities
    
    async def scan_all_upcoming(self, db: Session) -> List[dict]:
        """Escaneia todos os jogos próximos e retorna oportunidades."""
        matches = self._get_upcoming_matches(db, hours=48)
        all_opportunities = []
        
        for match in matches:
            team1_rating = self._get_team_rating(db, match.team1_id)
            team2_rating = self._get_team_rating(db, match.team2_id)
            latest_odds = self._get_latest_odds(db, match.id)
            
            if latest_odds:
                opps = self.analyze_match(match, team1_rating, team2_rating, latest_odds)
                all_opportunities.extend(opps)
        
        # Ordenar por edge (maior primeiro)
        return sorted(all_opportunities, key=lambda x: x["edge"], reverse=True)
    
    def _get_upcoming_matches(self, db: Session, hours: int = 48) -> List[ScorealarmMatch]:
        """Busca jogos das próximas N horas."""
        now = datetime.utcnow()
        future = now + timedelta(hours=hours)
        
        return db.query(ScorealarmMatch).filter(
            ScorealarmMatch.match_date >= now,
            ScorealarmMatch.match_date <= future,
            ScorealarmMatch.is_finished == False
        ).all()
    
    def _get_team_rating(self, db: Session, team_id: int) -> float:
        """Busca rating do time (usa default se não existir)."""
        rating = db.query(ScorealarmTeamRating).filter(ScorealarmTeamRating.team_id == team_id).first()
        if rating:
            return rating.elo_rating
        return EloRating.DEFAULT_RATING
    
    def _get_latest_odds(self, db: Session, match_id: int) -> Optional[OddsHistory]:
        """Busca odds mais recentes do match."""
        return db.query(OddsHistory).filter(
            OddsHistory.match_id == match_id,
            OddsHistory.market_type == "moneyline"
        ).order_by(OddsHistory.timestamp.desc()).first()
