"""Paper trading database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database.models import Base


class PaperBet(Base):
    """Aposta simulada (paper trading)."""
    __tablename__ = "paper_bets"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("scorealarm_matches.id"))
    
    # Detalhes da aposta
    bet_on = Column(String(50))  # "team1", "team2", "draw", "over", "under"
    odds = Column(Float)
    stake = Column(Float, default=100.0)  # Stake fixa para paper trading
    
    # Análise no momento da aposta
    our_probability = Column(Float)
    implied_probability = Column(Float)
    edge = Column(Float)
    
    # Resultado
    status = Column(String(20), default="pending")  # pending, won, lost, void
    profit = Column(Float, nullable=True)
    
    # Timestamps
    placed_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)


class PaperTradingStats(Base):
    """Estatísticas agregadas por esporte."""
    __tablename__ = "paper_trading_stats"
    
    id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey("scorealarm_sports.id"))
    
    total_bets = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    
    total_staked = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    
    avg_odds = Column(Float, default=0.0)
    avg_edge = Column(Float, default=0.0)
    
    roi = Column(Float, default=0.0)  # profit / staked
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
