"""Database utility functions for common queries."""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from database.scorealarm_models import ScorealarmMatch


def get_pending_matches(db: Session, sport_id: int = None) -> List[ScorealarmMatch]:
    """Get pending matches ordered by date.
    
    Args:
        db: SQLAlchemy session
        sport_id: Optional sport ID to filter by
        
    Returns:
        List of pending matches ordered by match date
    """
    query = db.query(ScorealarmMatch).filter(
        ScorealarmMatch.is_finished.is_(False)
    )
    if sport_id:
        query = query.filter(ScorealarmMatch.sport_id == sport_id)
    return query.order_by(ScorealarmMatch.match_date.asc()).all()


def get_upcoming_matches(db: Session, hours: int = 24) -> List[ScorealarmMatch]:
    """Get upcoming matches in the next X hours.
    
    Args:
        db: SQLAlchemy session
        hours: Number of hours to look ahead (default: 24)
        
    Returns:
        List of upcoming matches in the specified timeframe
    """
    now = datetime.utcnow()
    limit = now + timedelta(hours=hours)
    return db.query(ScorealarmMatch).filter(
        ScorealarmMatch.is_finished.is_(False),
        ScorealarmMatch.match_date >= now,
        ScorealarmMatch.match_date <= limit
    ).order_by(ScorealarmMatch.match_date.asc()).all()


def mark_match_finished(db: Session, match_id: int, team1_score: int, team2_score: int):
    """Mark match as finished with scores.
    
    Args:
        db: SQLAlchemy session
        match_id: ID of the match to mark as finished
        team1_score: Final score for team 1
        team2_score: Final score for team 2
    """
    match = db.query(ScorealarmMatch).filter(ScorealarmMatch.id == match_id).first()
    if match:
        match.is_finished = True
        match.finished_at = datetime.utcnow()
        match.team1_score = team1_score
        match.team2_score = team2_score
        db.commit()
