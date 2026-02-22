"""FastAPI Dashboard for Capivara Bet Paper Trading."""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from database.db import get_db_session
from database.scorealarm_models import ScorealarmSport, ScorealarmMatch
from database.paper_trading_models import PaperBet, PaperTradingStats
from analysis.value_detector import ValueBetDetector
from datetime import datetime, timedelta

app = FastAPI(title="Capivara Bet Dashboard")
templates = Jinja2Templates(directory="dashboard/templates")
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal com overview."""
    db = get_db_session()
    
    # Stats gerais
    total_sports = db.query(ScorealarmSport).count()
    total_matches = db.query(ScorealarmMatch).count()
    pending_matches = db.query(ScorealarmMatch).filter(ScorealarmMatch.is_finished == False).count()
    
    # Paper Trading stats
    total_bets = db.query(PaperBet).count()
    pending_bets = db.query(PaperBet).filter(PaperBet.status == "pending").count()
    won_bets = db.query(PaperBet).filter(PaperBet.status == "won").count()
    lost_bets = db.query(PaperBet).filter(PaperBet.status == "lost").count()
    
    total_profit = db.query(func.sum(PaperBet.profit)).filter(PaperBet.status != "pending").scalar() or 0
    total_staked = db.query(func.sum(PaperBet.stake)).filter(PaperBet.status != "pending").scalar() or 1
    roi = (total_profit / total_staked) * 100
    
    db.close()
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "total_sports": total_sports,
        "total_matches": total_matches,
        "pending_matches": pending_matches,
        "total_bets": total_bets,
        "pending_bets": pending_bets,
        "won_bets": won_bets,
        "lost_bets": lost_bets,
        "win_rate": (won_bets / max(won_bets + lost_bets, 1)) * 100,
        "total_profit": total_profit,
        "roi": roi,
        "now": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    })


@app.get("/opportunities", response_class=HTMLResponse)
async def opportunities(request: Request):
    """Top oportunidades de apostas."""
    db = get_db_session()
    detector = ValueBetDetector(min_edge=0.03)
    
    opps = await detector.scan_all_upcoming(db)
    
    # Enriquecer oportunidades com nomes das partidas
    for opp in opps:
        match = db.query(ScorealarmMatch).filter(ScorealarmMatch.id == opp['match_id']).first()
        if match:
            opp['match_name'] = f"{match.team1_name} vs {match.team2_name}"
        else:
            opp['match_name'] = "Match TBA"
    
    top_opps = opps[:20]  # Top 20
    
    db.close()
    
    return templates.TemplateResponse("opportunities.html", {
        "request": request,
        "opportunities": top_opps,
        "total_found": len(opps),
        "now": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    })


@app.get("/sports", response_class=HTMLResponse)
async def sports(request: Request):
    """Stats por esporte."""
    db = get_db_session()
    
    stats = db.query(PaperTradingStats).all()
    sports_data = []
    
    for s in stats:
        sport = db.query(ScorealarmSport).filter(ScorealarmSport.id == s.sport_id).first()
        if sport:
            sports_data.append({
                "name": sport.name,
                "is_gold": sport.is_gold,
                "total_bets": s.total_bets,
                "wins": s.wins,
                "losses": s.losses,
                "win_rate": (s.wins / max(s.total_bets, 1)) * 100,
                "profit": s.total_profit,
                "roi": s.roi * 100
            })
    
    # Ordenar por ROI
    sports_data.sort(key=lambda x: x["roi"], reverse=True)
    
    db.close()
    
    return templates.TemplateResponse("sports.html", {
        "request": request,
        "sports": sports_data,
        "now": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    })


@app.get("/bets", response_class=HTMLResponse)
async def bets(request: Request, status: str = None):
    """Lista de apostas."""
    db = get_db_session()
    
    query = db.query(PaperBet)
    if status:
        query = query.filter(PaperBet.status == status)
    
    bets_list = query.order_by(PaperBet.placed_at.desc()).limit(100).all()
    
    # Enriquecer com nomes das partidas
    enriched_bets = []
    for bet in bets_list:
        match = db.query(ScorealarmMatch).filter(ScorealarmMatch.id == bet.match_id).first()
        enriched_bets.append({
            "id": bet.id,
            "match_name": f"{match.team1_name} vs {match.team2_name}" if match else "Unknown",
            "bet_on": bet.bet_on,
            "odds": bet.odds,
            "stake": bet.stake,
            "status": bet.status,
            "profit": bet.profit or 0,
            "edge": bet.edge,
            "placed_at": bet.placed_at,
            "settled_at": bet.settled_at
        })
    
    db.close()
    
    return templates.TemplateResponse("bets.html", {
        "request": request,
        "bets": enriched_bets,
        "filter_status": status,
        "now": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    })


@app.get("/api/stats")
async def api_stats():
    """API endpoint para stats (para widgets externos)."""
    db = get_db_session()
    
    stats = db.query(PaperTradingStats).all()
    
    total_profit = sum(s.total_profit for s in stats)
    total_bets = sum(s.total_bets for s in stats)
    total_wins = sum(s.wins for s in stats)
    
    db.close()
    
    return {
        "total_profit": round(total_profit, 2),
        "total_bets": total_bets,
        "win_rate": round((total_wins / max(total_bets, 1)) * 100, 1),
        "updated_at": datetime.utcnow().isoformat()
    }


@app.get("/api/opportunities")
async def api_opportunities():
    """API endpoint para oportunidades."""
    db = get_db_session()
    detector = ValueBetDetector(min_edge=0.05)
    
    opps = await detector.scan_all_upcoming(db)
    
    db.close()
    
    return {
        "count": len(opps),
        "opportunities": opps[:10],
        "updated_at": datetime.utcnow().isoformat()
    }
