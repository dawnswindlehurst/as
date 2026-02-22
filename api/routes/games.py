"""Game routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from api.dependencies import get_db
from api.schemas.game import GameResponse, GameWithOdds, OddsSchema
from database.models import Match, Odds

router = APIRouter()


@router.get("/games", response_model=List[GameWithOdds])
async def get_games(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    league: Optional[str] = Query(None, description="League/tournament name"),
    game: Optional[str] = Query(None, description="Game type (cs2, lol, dota2, valorant, nba, etc)"),
    db: Session = Depends(get_db)
):
    """
    Get games by date and filters.
    
    Args:
        date: Date in YYYY-MM-DD format (default: today)
        league: Filter by league/tournament
        game: Filter by game type
        db: Database session
        
    Returns:
        List of games with odds
    """
    query = db.query(Match)
    
    # Date filter
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.utcnow().date()
    else:
        target_date = datetime.utcnow().date()
    
    # Filter by date range (whole day)
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    query = query.filter(
        and_(
            Match.start_time >= start_of_day,
            Match.start_time <= end_of_day
        )
    )
    
    # League filter
    if league:
        query = query.filter(Match.tournament.ilike(f"%{league}%"))
    
    # Game filter
    if game:
        query = query.filter(Match.game == game)
    
    matches = query.order_by(Match.start_time).all()
    
    # Add is_live field based on current time
    current_time = datetime.utcnow()
    result = []
    
    for match in matches:
        match_dict = {
            "id": match.id,
            "game": match.game,
            "team1": match.team1,
            "team2": match.team2,
            "start_time": match.start_time,
            "tournament": match.tournament,
            "best_of": match.best_of,
            "winner": match.winner,
            "team1_score": match.team1_score,
            "team2_score": match.team2_score,
            "finished": match.finished,
            "is_live": not match.finished and match.start_time <= current_time,
            "odds": [
                {
                    "bookmaker": odd.bookmaker,
                    "team1_odds": odd.team1_odds,
                    "team2_odds": odd.team2_odds,
                    "timestamp": odd.timestamp
                }
                for odd in match.odds
            ]
        }
        result.append(match_dict)
    
    return result


@router.get("/games/live", response_model=List[GameWithOdds])
async def get_live_games(
    game: Optional[str] = Query(None, description="Game type filter"),
    db: Session = Depends(get_db)
):
    """
    Get currently live games.
    
    Args:
        game: Filter by game type
        db: Database session
        
    Returns:
        List of live games
    """
    current_time = datetime.utcnow()
    
    # Games that started but haven't finished
    query = db.query(Match).filter(
        and_(
            Match.start_time <= current_time,
            Match.finished.is_(False)
        )
    )
    
    if game:
        query = query.filter(Match.game == game)
    
    matches = query.order_by(Match.start_time).all()
    
    result = []
    for match in matches:
        match_dict = {
            "id": match.id,
            "game": match.game,
            "team1": match.team1,
            "team2": match.team2,
            "start_time": match.start_time,
            "tournament": match.tournament,
            "best_of": match.best_of,
            "winner": match.winner,
            "team1_score": match.team1_score,
            "team2_score": match.team2_score,
            "finished": match.finished,
            "is_live": True,
            "odds": [
                {
                    "bookmaker": odd.bookmaker,
                    "team1_odds": odd.team1_odds,
                    "team2_odds": odd.team2_odds,
                    "timestamp": odd.timestamp
                }
                for odd in match.odds
            ]
        }
        result.append(match_dict)
    
    return result


@router.get("/games/{game_id}", response_model=GameWithOdds)
async def get_game_by_id(
    game_id: int,
    db: Session = Depends(get_db)
):
    """
    Get game details by ID.
    
    Args:
        game_id: Game ID
        db: Database session
        
    Returns:
        Game details with odds
    """
    match = db.query(Match).filter(Match.id == game_id).first()
    
    if not match:
        return {"error": "Game not found"}
    
    current_time = datetime.utcnow()
    
    return {
        "id": match.id,
        "game": match.game,
        "team1": match.team1,
        "team2": match.team2,
        "start_time": match.start_time,
        "tournament": match.tournament,
        "best_of": match.best_of,
        "winner": match.winner,
        "team1_score": match.team1_score,
        "team2_score": match.team2_score,
        "finished": match.finished,
        "is_live": not match.finished and match.start_time <= current_time,
        "odds": [
            {
                "bookmaker": odd.bookmaker,
                "team1_odds": odd.team1_odds,
                "team2_odds": odd.team2_odds,
                "timestamp": odd.timestamp
            }
            for odd in match.odds
        ]
    }
