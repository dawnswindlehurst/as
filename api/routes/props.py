"""Player props routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from api.dependencies import get_db
from api.schemas.player import PlayerPropsResponse, PlayerPropAnalysis, PlayerGameLog
from database.historical_models import NBAPlayerGameStats, NBAGame

router = APIRouter()


@router.get("/props/{player_id}")
async def get_player_props(
    player_id: str,
    db: Session = Depends(get_db)
):
    """
    Get player props analysis.
    
    Args:
        player_id: Player ID
        db: Database session
        
    Returns:
        Player props with averages and over rates
    """
    # Get player info
    player_info = db.query(
        NBAPlayerGameStats.player_id,
        NBAPlayerGameStats.player_name,
        NBAPlayerGameStats.team
    ).filter(
        NBAPlayerGameStats.player_id == player_id
    ).first()
    
    if not player_info:
        return {"error": "Player not found"}
    
    # Get all player stats for analysis
    all_stats = db.query(NBAPlayerGameStats, NBAGame).join(
        NBAGame,
        NBAPlayerGameStats.game_id == NBAGame.game_id
    ).filter(
        NBAPlayerGameStats.player_id == player_id
    ).order_by(
        NBAGame.game_date.desc()
    ).all()
    
    if not all_stats:
        return {
            "player_id": player_id,
            "player_name": player_info.player_name if player_info else "Unknown",
            "team": player_info.team if player_info else "Unknown",
            "props": [],
            "recent_games": []
        }
    
    # Calculate averages and rates
    props_analysis = []
    
    # Points prop
    points = [stat.points for stat, game in all_stats if stat.points is not None]
    if points:
        avg_points = sum(points) / len(points)
        last_5_points = sum(points[:5]) / min(5, len(points))
        last_10_points = sum(points[:10]) / min(10, len(points))
        
        # Calculate over rate for a typical line (using average)
        line = round(avg_points - 0.5, 1)  # Typical line slightly below average
        over_count = sum(1 for p in points if p > line)
        over_rate = (over_count / len(points)) * 100
        
        props_analysis.append({
            "prop_type": "points",
            "line": line,
            "average": round(avg_points, 1),
            "over_rate": round(over_rate, 1),
            "under_rate": round(100 - over_rate, 1),
            "last_5_avg": round(last_5_points, 1),
            "last_10_avg": round(last_10_points, 1),
            "home_avg": None,
            "away_avg": None
        })
    
    # Rebounds prop
    rebounds = [stat.rebounds_total for stat, game in all_stats if stat.rebounds_total is not None]
    if rebounds:
        avg_reb = sum(rebounds) / len(rebounds)
        last_5_reb = sum(rebounds[:5]) / min(5, len(rebounds))
        last_10_reb = sum(rebounds[:10]) / min(10, len(rebounds))
        
        line = round(avg_reb - 0.5, 1)
        over_count = sum(1 for r in rebounds if r > line)
        over_rate = (over_count / len(rebounds)) * 100
        
        props_analysis.append({
            "prop_type": "rebounds",
            "line": line,
            "average": round(avg_reb, 1),
            "over_rate": round(over_rate, 1),
            "under_rate": round(100 - over_rate, 1),
            "last_5_avg": round(last_5_reb, 1),
            "last_10_avg": round(last_10_reb, 1),
            "home_avg": None,
            "away_avg": None
        })
    
    # Assists prop
    assists = [stat.assists for stat, game in all_stats if stat.assists is not None]
    if assists:
        avg_ast = sum(assists) / len(assists)
        last_5_ast = sum(assists[:5]) / min(5, len(assists))
        last_10_ast = sum(assists[:10]) / min(10, len(assists))
        
        line = round(avg_ast - 0.5, 1)
        over_count = sum(1 for a in assists if a > line)
        over_rate = (over_count / len(assists)) * 100
        
        props_analysis.append({
            "prop_type": "assists",
            "line": line,
            "average": round(avg_ast, 1),
            "over_rate": round(over_rate, 1),
            "under_rate": round(100 - over_rate, 1),
            "last_5_avg": round(last_5_ast, 1),
            "last_10_avg": round(last_10_ast, 1),
            "home_avg": None,
            "away_avg": None
        })
    
    # Recent games
    recent_games = []
    for stat, game in all_stats[:10]:
        opponent = game.away_team if stat.is_home else game.home_team
        recent_games.append({
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
    
    return {
        "player_id": player_id,
        "player_name": player_info.player_name,
        "team": player_info.team,
        "props": props_analysis,
        "recent_games": recent_games
    }
