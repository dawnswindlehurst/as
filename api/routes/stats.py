"""Stats routes for dashboard."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from api.dependencies import get_db
from database.historical_models import EsportsMatch, EsportsPlayerStats

router = APIRouter()


@router.get("/stats/overview")
async def get_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get overview statistics.
    
    Returns:
        Overview stats including total matches and breakdown by game
    """
    # Total matches
    total_matches = db.query(func.count(EsportsMatch.id)).scalar() or 0
    
    # Total finished matches
    finished_matches = db.query(func.count(EsportsMatch.id)).filter(
        EsportsMatch.winner.isnot(None)
    ).scalar() or 0
    
    # Breakdown by game
    game_breakdown = db.query(
        EsportsMatch.game,
        func.count(EsportsMatch.id).label('count')
    ).group_by(EsportsMatch.game).all()
    
    breakdown = {game: count for game, count in game_breakdown}
    
    # Recent matches count (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_count = db.query(func.count(EsportsMatch.id)).filter(
        EsportsMatch.match_date >= seven_days_ago
    ).scalar() or 0
    
    return {
        "total_matches": total_matches,
        "finished_matches": finished_matches,
        "recent_matches": recent_count,
        "breakdown_by_game": breakdown
    }


@router.get("/stats/teams")
async def get_team_stats(
    game: Optional[str] = Query(None, description="Filter by game type"),
    limit: int = Query(20, description="Number of teams to return"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get team rankings with win rate.
    
    Args:
        game: Filter by game type (valorant, cs2, lol, dota2)
        limit: Number of teams to return
        
    Returns:
        List of teams with their statistics
    """
    # Build query to get all matches
    query = db.query(EsportsMatch).filter(EsportsMatch.winner.isnot(None))
    
    if game:
        query = query.filter(EsportsMatch.game == game)
    
    matches = query.all()
    
    # Calculate team stats
    team_stats = {}
    
    for match in matches:
        # Process team1
        if match.team1 not in team_stats:
            team_stats[match.team1] = {
                "team": match.team1,
                "game": match.game,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0
            }
        
        team_stats[match.team1]["matches_played"] += 1
        if match.winner == match.team1:
            team_stats[match.team1]["wins"] += 1
        else:
            team_stats[match.team1]["losses"] += 1
        
        # Process team2
        if match.team2 not in team_stats:
            team_stats[match.team2] = {
                "team": match.team2,
                "game": match.game,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0
            }
        
        team_stats[match.team2]["matches_played"] += 1
        if match.winner == match.team2:
            team_stats[match.team2]["wins"] += 1
        else:
            team_stats[match.team2]["losses"] += 1
    
    # Calculate win rates and filter teams with at least 3 matches
    result = []
    for team, stats in team_stats.items():
        if stats["matches_played"] >= 3:
            stats["win_rate"] = round(stats["wins"] / stats["matches_played"] * 100, 2)
            result.append(stats)
    
    # Sort by win rate and then by matches played
    result.sort(key=lambda x: (x["win_rate"], x["matches_played"]), reverse=True)
    
    return result[:limit]


@router.get("/stats/recent-results")
async def get_recent_results(
    limit: int = Query(10, description="Number of results to return"),
    game: Optional[str] = Query(None, description="Filter by game type"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get recent match results.
    
    Args:
        limit: Number of results to return
        game: Filter by game type
        
    Returns:
        List of recent matches
    """
    query = db.query(EsportsMatch).filter(EsportsMatch.winner.isnot(None))
    
    if game:
        query = query.filter(EsportsMatch.game == game)
    
    matches = query.order_by(desc(EsportsMatch.match_date)).limit(limit).all()
    
    result = []
    for match in matches:
        result.append({
            "id": match.id,
            "game": match.game,
            "tournament": match.tournament,
            "match_date": match.match_date.isoformat() if match.match_date else None,
            "team1": match.team1,
            "team2": match.team2,
            "team1_score": match.team1_score,
            "team2_score": match.team2_score,
            "winner": match.winner,
            "best_of": match.best_of
        })
    
    return result


@router.get("/stats/tournaments")
async def get_tournaments(
    game: Optional[str] = Query(None, description="Filter by game type"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get active tournaments with match counts.
    
    Args:
        game: Filter by game type
        
    Returns:
        List of tournaments with match counts
    """
    query = db.query(
        EsportsMatch.tournament,
        EsportsMatch.game,
        func.count(EsportsMatch.id).label('match_count'),
        func.max(EsportsMatch.match_date).label('latest_match')
    ).group_by(EsportsMatch.tournament, EsportsMatch.game)
    
    if game:
        query = query.filter(EsportsMatch.game == game)
    
    tournaments = query.order_by(desc('latest_match')).all()
    
    result = []
    for tournament, game_name, match_count, latest_match in tournaments:
        result.append({
            "tournament": tournament,
            "game": game_name,
            "match_count": match_count,
            "latest_match": latest_match.isoformat() if latest_match else None
        })
    
    return result


@router.get("/teams")
async def get_teams(
    game: Optional[str] = Query(None, description="Filter by game type (valorant, cs2, lol, dota2, nba)"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get teams by sport/game.
    
    Args:
        game: Filter by game type (valorant, cs2, lol, dota2, nba)
        
    Returns:
        List of teams for the specified game
    """
    if not game:
        raise HTTPException(status_code=400, detail="Game parameter is required")
    
    # Get unique teams for the specified game
    teams_query = db.query(
        EsportsMatch.team1.label('team'),
        EsportsMatch.game
    ).filter(EsportsMatch.game == game).union(
        db.query(
            EsportsMatch.team2.label('team'),
            EsportsMatch.game
        ).filter(EsportsMatch.game == game)
    )
    
    teams = teams_query.distinct().all()
    
    # Calculate basic stats for each team
    result = []
    for team_row in teams:
        team_name = team_row.team
        
        # Count matches
        matches_count = db.query(func.count(EsportsMatch.id)).filter(
            EsportsMatch.game == game,
            ((EsportsMatch.team1 == team_name) | (EsportsMatch.team2 == team_name))
        ).scalar() or 0
        
        # Count wins
        wins_count = db.query(func.count(EsportsMatch.id)).filter(
            EsportsMatch.game == game,
            EsportsMatch.winner == team_name
        ).scalar() or 0
        
        win_rate = (wins_count / matches_count * 100) if matches_count > 0 else 0
        
        result.append({
            "team": team_name,
            "game": game,
            "matches_played": matches_count,
            "wins": wins_count,
            "win_rate": round(win_rate, 1)
        })
    
    # Sort by matches played and win rate
    result.sort(key=lambda x: (x["matches_played"], x["win_rate"]), reverse=True)
    
    return result


@router.get("/teams/{team_name}/players")
async def get_team_players(
    team_name: str,
    game: Optional[str] = Query(None, description="Filter by game type"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get players for a specific team.
    
    Args:
        team_name: Team name
        game: Optional game filter
        
    Returns:
        List of players from the team
    """
    # Query distinct players from the team
    query = db.query(
        EsportsPlayerStats.player_id,
        EsportsPlayerStats.player_name,
        EsportsPlayerStats.team,
        func.count(EsportsPlayerStats.id).label('matches_played')
    ).filter(
        EsportsPlayerStats.team == team_name
    ).group_by(
        EsportsPlayerStats.player_id,
        EsportsPlayerStats.player_name,
        EsportsPlayerStats.team
    )
    
    players = query.all()
    
    result = []
    for player in players:
        # Get player stats averages
        stats = db.query(
            func.avg(EsportsPlayerStats.kills).label('avg_kills'),
            func.avg(EsportsPlayerStats.deaths).label('avg_deaths'),
            func.avg(EsportsPlayerStats.assists).label('avg_assists'),
            func.avg(EsportsPlayerStats.kd_ratio).label('avg_kd')
        ).filter(
            EsportsPlayerStats.player_id == player.player_id,
            EsportsPlayerStats.team == team_name
        ).first()
        
        result.append({
            "player_id": player.player_id,
            "player_name": player.player_name,
            "team": player.team,
            "matches_played": player.matches_played,
            "avg_kills": round(stats.avg_kills, 1) if stats.avg_kills else 0,
            "avg_deaths": round(stats.avg_deaths, 1) if stats.avg_deaths else 0,
            "avg_assists": round(stats.avg_assists, 1) if stats.avg_assists else 0,
            "avg_kd": round(stats.avg_kd, 2) if stats.avg_kd else 0
        })
    
    # Sort by matches played
    result.sort(key=lambda x: x["matches_played"], reverse=True)
    
    return result


@router.get("/players/{player_id}/stats")
async def get_player_stats(
    player_id: str,
    limit: int = Query(20, description="Number of recent matches to return"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed statistics for a specific player.
    
    Args:
        player_id: Player ID
        limit: Number of recent matches
        
    Returns:
        Player statistics including averages and recent matches
    """
    # Get player info
    player_info = db.query(
        EsportsPlayerStats.player_id,
        EsportsPlayerStats.player_name,
        EsportsPlayerStats.team
    ).filter(
        EsportsPlayerStats.player_id == player_id
    ).first()
    
    if not player_info:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Get all player stats with match info
    player_stats = db.query(
        EsportsPlayerStats,
        EsportsMatch
    ).join(
        EsportsMatch,
        EsportsPlayerStats.match_id == EsportsMatch.match_id
    ).filter(
        EsportsPlayerStats.player_id == player_id
    ).order_by(
        desc(EsportsMatch.match_date)
    ).limit(limit).all()
    
    # Calculate averages
    if player_stats:
        stats_list = [stat for stat, _ in player_stats]
        
        total_matches = len(stats_list)
        avg_kills = sum(s.kills or 0 for s in stats_list) / total_matches
        avg_deaths = sum(s.deaths or 0 for s in stats_list) / total_matches
        avg_assists = sum(s.assists or 0 for s in stats_list) / total_matches
        avg_kd = sum(s.kd_ratio or 0 for s in stats_list) / total_matches
        
        # Game-specific averages
        avg_adr = sum(s.adr or 0 for s in stats_list if s.adr) / len([s for s in stats_list if s.adr]) if any(s.adr for s in stats_list) else None
        avg_acs = sum(s.acs or 0 for s in stats_list if s.acs) / len([s for s in stats_list if s.acs]) if any(s.acs for s in stats_list) else None
        
        averages = {
            "kills": round(avg_kills, 1),
            "deaths": round(avg_deaths, 1),
            "assists": round(avg_assists, 1),
            "kd_ratio": round(avg_kd, 2),
            "adr": round(avg_adr, 1) if avg_adr else None,
            "acs": round(avg_acs, 1) if avg_acs else None
        }
    else:
        averages = {
            "kills": 0,
            "deaths": 0,
            "assists": 0,
            "kd_ratio": 0,
            "adr": None,
            "acs": None
        }
    
    # Format recent matches
    recent_matches = []
    for stat, match in player_stats:
        opponent = match.team2 if match.team1 == stat.team else match.team1
        
        recent_matches.append({
            "match_id": match.match_id,
            "match_date": match.match_date.isoformat() if match.match_date else None,
            "tournament": match.tournament,
            "opponent": opponent,
            "won": match.winner == stat.team,
            "kills": stat.kills,
            "deaths": stat.deaths,
            "assists": stat.assists,
            "kd_ratio": stat.kd_ratio,
            "adr": stat.adr,
            "acs": stat.acs,
            "rating": stat.rating,
            "agent": stat.agent,
            "champion": stat.champion,
            "hero": stat.hero
        })
    
    return {
        "player_id": player_info.player_id,
        "player_name": player_info.player_name,
        "team": player_info.team,
        "total_matches": len(player_stats),
        "averages": averages,
        "recent_matches": recent_matches
    }
