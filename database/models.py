"""Database models using SQLAlchemy."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Match(Base):
    """Match model."""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True)
    game = Column(String(50), nullable=False)
    team1 = Column(String(100), nullable=False)
    team2 = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    tournament = Column(String(200))
    best_of = Column(Integer, default=1)
    
    # Result
    winner = Column(String(100))
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    finished = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    odds = relationship("Odds", back_populates="match", cascade="all, delete-orphan")
    bets = relationship("Bet", back_populates="match", cascade="all, delete-orphan")


class Odds(Base):
    """Odds model."""
    __tablename__ = "odds"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    bookmaker = Column(String(50), nullable=False)
    market_type = Column(String(50), nullable=False)
    
    # Odds values
    team1_odds = Column(Float)
    team2_odds = Column(Float)
    draw_odds = Column(Float)
    
    # Line/Handicap value (for spreads, totals)
    line = Column(Float)
    
    # Timing
    is_opening = Column(Boolean, default=False)
    is_closing = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship("Match", back_populates="odds")


class Prediction(Base):
    """Model prediction."""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    model_type = Column(String(50), nullable=False)
    
    # Predictions
    team1_win_prob = Column(Float, nullable=False)
    team2_win_prob = Column(Float, nullable=False)
    
    # Additional predictions (for totals, etc.)
    predictions_json = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    match = relationship("Match")


class Bet(Base):
    """Bet model."""
    __tablename__ = "bets"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    # Bet details
    bookmaker = Column(String(50), nullable=False)
    market_type = Column(String(50), nullable=False)
    selection = Column(String(100), nullable=False)
    odds = Column(Float, nullable=False)
    stake = Column(Float, nullable=False)
    
    # Model confidence
    model_probability = Column(Float, nullable=False)
    implied_probability = Column(Float, nullable=False)
    edge = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Kelly sizing
    kelly_stake = Column(Float)
    
    # Status
    status = Column(String(20), default="pending")  # pending, won, lost, void, cashout
    confirmed = Column(Boolean, default=False)
    
    # Result
    profit = Column(Float)
    settled_at = Column(DateTime)
    
    # CLV tracking
    closing_odds = Column(Float)
    clv = Column(Float)  # Closing Line Value
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text)
    
    # Relationship
    match = relationship("Match", back_populates="bets")


class TeamRating(Base):
    """Team rating model."""
    __tablename__ = "team_ratings"
    
    id = Column(Integer, primary_key=True)
    team = Column(String(100), nullable=False)
    game = Column(String(50), nullable=False)
    
    # ELO
    elo_rating = Column(Float, default=1500)
    
    # Glicko-2
    glicko_rating = Column(Float, default=1500)
    glicko_rd = Column(Float, default=350)
    glicko_sigma = Column(Float, default=0.06)
    
    # Stats
    matches_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    
    # Map-specific (for CS2, Valorant)
    map_ratings = Column(JSON)  # {map_name: rating}
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PerformanceMetric(Base):
    """Performance tracking metrics."""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True)
    
    # Filters
    game = Column(String(50))
    bookmaker = Column(String(50))
    market_type = Column(String(50))
    confidence_range_low = Column(Float)
    confidence_range_high = Column(Float)
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    
    # Metrics
    total_bets = Column(Integer, default=0)
    won_bets = Column(Integer, default=0)
    lost_bets = Column(Integer, default=0)
    void_bets = Column(Integer, default=0)
    
    total_stake = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    win_rate = Column(Float, default=0.0)
    avg_odds = Column(Float, default=0.0)
    avg_edge = Column(Float, default=0.0)
    avg_clv = Column(Float, default=0.0)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)


class CollectionStatus(Base):
    """Collection status and control table."""
    __tablename__ = "collection_status"
    
    id = Column(Integer, primary_key=True)
    
    # Collection type
    collection_type = Column(String(50), nullable=False)  # initial, periodic
    source = Column(String(50), nullable=False)  # scorealarm, hltv, vlr, opendota, superbet
    game = Column(String(50))  # specific game/sport
    
    # Status
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    
    # Progress tracking
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    last_collection_at = Column(DateTime)
    next_collection_at = Column(DateTime)
    
    # Error tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    collection_metadata = Column(JSON)  # Additional collection-specific metadata
