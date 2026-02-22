"""Player routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db
from api.schemas.player import PlayerBase, PlayerGameLog
from database.historical_models import NBAPlayerGameStats, NBAGame

router = APIRouter()


@router.get("/players/search")
async def search_players(
    q: str = Query(..., description="Search query (player name)"),
    sport: Optional[str] = Query("nba", description="Sport type"),
    db: Session = Depends(get_db)
):
    """
    Search for players by name.
    
    Args:
        q: Search query
        sport: Sport type (default: nba)
        db: Database session
        
    Returns:
        List of matching players
    """
    if sport.lower() == "nba":
        # Search in NBA player stats
        players = db.query(
            NBAPlayerGameStats.player_id,
            NBAPlayerGameStats.player_name,
            NBAPlayerGameStats.team
        ).filter(
            NBAPlayerGameStats.player_name.ilike(f"%{q}%")
        ).distinct().limit(20).all()
        
        return [
            {
                "player_id": p.player_id,
                "player_name": p.player_name,
                "team": p.team,
                "sport": "nba"
            }
            for p in players
        ]
    
    return []


@router.get("/players/{player_id}/gamelog")
async def get_player_gamelog(
    player_id: str,
    limit: int = Query(10, description="Number of games to return"),
    db: Session = Depends(get_db)
):
    """
    Get player game log.
    
    Args:
        player_id: Player ID
        limit: Number of games to return
        db: Database session
        
    Returns:
        List of recent games
    """
    # Get player's recent games
    games = db.query(NBAPlayerGameStats, NBAGame).join(
        NBAGame,
        NBAPlayerGameStats.game_id == NBAGame.game_id
    ).filter(
        NBAPlayerGameStats.player_id == player_id
    ).order_by(
        NBAGame.game_date.desc()
    ).limit(limit).all()
    
    result = []
    for stat, game in games:
        opponent = game.away_team if stat.is_home else game.home_team
        
        result.append({
            "game_id": game.game_id,
            "game_date": game.game_date.isoformat() if game.game_date else None,
            "opponent": opponent,
            "is_home": stat.is_home,
            "minutes": stat.minutes,
            "points": stat.points,
            "rebounds_total": stat.rebounds_total,
            "assists": stat.assists,
            "steals": stat.steals,
            "blocks": stat.blocks
        })
    
    return result
