"""Value bets routes."""
from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()


@router.get("/value-bets")
async def get_value_bets(
    sport: Optional[str] = None,
    min_edge: float = 3.0,
    min_confidence: int = 55
):
    """
    Get value bets of the day.
    
    Returns list of bets where model probability exceeds implied probability from odds.
    
    Args:
        sport: Filter by sport (nba, soccer, tennis, valorant, cs2, lol, dota2). If None, returns all sports.
        min_edge: Minimum edge percentage (default 3%)
        min_confidence: Minimum confidence score (default 55%)
    
    Returns:
        Dictionary with value_bets list and summary statistics
    """
    
    # Mock data for demonstration
    # In production, this would query the database for actual predictions and odds
    
    mock_bets = [
        {
            "id": "bet_001",
            "sport": "nba",
            "game": "Los Angeles Lakers vs Boston Celtics",
            "league": "NBA",
            "start_time": (datetime.utcnow() + timedelta(hours=5)).isoformat() + "Z",
            "market": "moneyline",
            "selection": "Lakers",
            "odds": 2.10,
            "bookmaker": "Superbet",
            "model_probability": 0.55,
            "implied_probability": 0.476,
            "edge": 7.4,
            "confidence": 68,
            "expected_value": 0.155,
            "kelly_stake": 0.14,
            "suggested_stake": 14.00,
            "reasoning": "Lakers em casa, Celtics em back-to-back"
        },
        {
            "id": "bet_002",
            "sport": "valorant",
            "game": "LOUD vs NRG",
            "league": "VCT Americas",
            "start_time": (datetime.utcnow() + timedelta(hours=3)).isoformat() + "Z",
            "market": "moneyline",
            "selection": "LOUD",
            "odds": 1.85,
            "bookmaker": "Bet365",
            "model_probability": 0.61,
            "implied_probability": 0.541,
            "edge": 6.9,
            "confidence": 72,
            "expected_value": 0.129,
            "kelly_stake": 0.13,
            "suggested_stake": 13.00,
            "reasoning": "LOUD dominante em casa, NRG sem Marved"
        },
        {
            "id": "bet_003",
            "sport": "soccer",
            "game": "Flamengo vs Palmeiras",
            "league": "Brasileirão",
            "start_time": (datetime.utcnow() + timedelta(hours=7)).isoformat() + "Z",
            "market": "btts",
            "selection": "Both Teams to Score - Yes",
            "odds": 1.72,
            "bookmaker": "Betano",
            "model_probability": 0.65,
            "implied_probability": 0.581,
            "edge": 6.9,
            "confidence": 65,
            "expected_value": 0.118,
            "kelly_stake": 0.12,
            "suggested_stake": 12.00,
            "reasoning": "Ambos times com ataque forte, defesas frágeis"
        },
        {
            "id": "bet_004",
            "sport": "cs2",
            "game": "FaZe Clan vs Natus Vincere",
            "league": "ESL Pro League",
            "start_time": (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z",
            "market": "map_winner",
            "selection": "FaZe on Inferno",
            "odds": 2.25,
            "bookmaker": "Pinnacle",
            "model_probability": 0.52,
            "implied_probability": 0.444,
            "edge": 7.6,
            "confidence": 63,
            "expected_value": 0.170,
            "kelly_stake": 0.15,
            "suggested_stake": 15.00,
            "reasoning": "FaZe 75% winrate no Inferno, NaVi preferindo banir"
        },
        {
            "id": "bet_005",
            "sport": "lol",
            "game": "T1 vs Gen.G",
            "league": "LCK Spring",
            "start_time": (datetime.utcnow() + timedelta(hours=6)).isoformat() + "Z",
            "market": "over_under",
            "selection": "Over 2.5 Maps",
            "odds": 1.95,
            "bookmaker": "Betway",
            "model_probability": 0.58,
            "implied_probability": 0.513,
            "edge": 6.7,
            "confidence": 66,
            "expected_value": 0.131,
            "kelly_stake": 0.13,
            "suggested_stake": 13.00,
            "reasoning": "Histórico de jogos longos entre essas equipes"
        },
        {
            "id": "bet_006",
            "sport": "dota2",
            "game": "Team Spirit vs Team Liquid",
            "league": "DreamLeague",
            "start_time": (datetime.utcnow() + timedelta(hours=4)).isoformat() + "Z",
            "market": "moneyline",
            "selection": "Team Spirit",
            "odds": 1.75,
            "bookmaker": "Superbet",
            "model_probability": 0.63,
            "implied_probability": 0.571,
            "edge": 5.9,
            "confidence": 69,
            "expected_value": 0.103,
            "kelly_stake": 0.10,
            "suggested_stake": 10.00,
            "reasoning": "Spirit forte no patch atual, Liquid em slump"
        },
        {
            "id": "bet_007",
            "sport": "nba",
            "game": "Golden State Warriors vs Phoenix Suns",
            "league": "NBA",
            "start_time": (datetime.utcnow() + timedelta(hours=8)).isoformat() + "Z",
            "market": "spread",
            "selection": "Warriors -3.5",
            "odds": 1.90,
            "bookmaker": "Bet365",
            "model_probability": 0.59,
            "implied_probability": 0.526,
            "edge": 6.4,
            "confidence": 64,
            "expected_value": 0.121,
            "kelly_stake": 0.12,
            "suggested_stake": 12.00,
            "reasoning": "Warriors forte em casa, Suns sem Booker"
        },
        {
            "id": "bet_008",
            "sport": "tennis",
            "game": "Carlos Alcaraz vs Novak Djokovic",
            "league": "Australian Open",
            "start_time": (datetime.utcnow() + timedelta(hours=12)).isoformat() + "Z",
            "market": "moneyline",
            "selection": "Alcaraz",
            "odds": 2.40,
            "bookmaker": "Pinnacle",
            "model_probability": 0.48,
            "implied_probability": 0.417,
            "edge": 6.3,
            "confidence": 61,
            "expected_value": 0.152,
            "kelly_stake": 0.13,
            "suggested_stake": 13.00,
            "reasoning": "Alcaraz em grande forma, Djokovic cansado"
        },
        {
            "id": "bet_009",
            "sport": "valorant",
            "game": "Sentinels vs Cloud9",
            "league": "VCT Americas",
            "start_time": (datetime.utcnow() + timedelta(hours=10)).isoformat() + "Z",
            "market": "over_under",
            "selection": "Over 2.5 Maps",
            "odds": 2.00,
            "bookmaker": "Betway",
            "model_probability": 0.56,
            "implied_probability": 0.500,
            "edge": 6.0,
            "confidence": 62,
            "expected_value": 0.120,
            "kelly_stake": 0.12,
            "suggested_stake": 12.00,
            "reasoning": "Times equilibrados, histórico de jogos longos"
        },
        {
            "id": "bet_010",
            "sport": "soccer",
            "game": "Manchester City vs Arsenal",
            "league": "Premier League",
            "start_time": (datetime.utcnow() + timedelta(hours=9)).isoformat() + "Z",
            "market": "over_under",
            "selection": "Over 2.5 Goals",
            "odds": 1.80,
            "bookmaker": "Betano",
            "model_probability": 0.62,
            "implied_probability": 0.556,
            "edge": 6.4,
            "confidence": 67,
            "expected_value": 0.116,
            "kelly_stake": 0.11,
            "suggested_stake": 11.00,
            "reasoning": "Ambos times com ataque forte, tendência de gols"
        },
        {
            "id": "bet_011",
            "sport": "cs2",
            "game": "Vitality vs G2",
            "league": "IEM Katowice",
            "start_time": (datetime.utcnow() + timedelta(hours=11)).isoformat() + "Z",
            "market": "moneyline",
            "selection": "Vitality",
            "odds": 1.65,
            "bookmaker": "Pinnacle",
            "model_probability": 0.68,
            "implied_probability": 0.606,
            "edge": 7.4,
            "confidence": 71,
            "expected_value": 0.122,
            "kelly_stake": 0.12,
            "suggested_stake": 12.00,
            "reasoning": "Vitality dominante com ZywOo em forma"
        },
        {
            "id": "bet_012",
            "sport": "lol",
            "game": "Cloud9 vs Team Liquid",
            "league": "LCS Spring",
            "start_time": (datetime.utcnow() + timedelta(hours=13)).isoformat() + "Z",
            "market": "moneyline",
            "selection": "Cloud9",
            "odds": 2.15,
            "bookmaker": "Bet365",
            "model_probability": 0.53,
            "implied_probability": 0.465,
            "edge": 6.5,
            "confidence": 60,
            "expected_value": 0.140,
            "kelly_stake": 0.13,
            "suggested_stake": 13.00,
            "reasoning": "C9 com roster novo forte, Liquid inconsistente"
        },
        {
            "id": "bet_013",
            "sport": "nba",
            "game": "Milwaukee Bucks vs Denver Nuggets",
            "league": "NBA",
            "start_time": (datetime.utcnow() + timedelta(hours=14)).isoformat() + "Z",
            "market": "player_prop",
            "selection": "Giannis Over 29.5 Points",
            "odds": 1.88,
            "bookmaker": "Superbet",
            "model_probability": 0.60,
            "implied_probability": 0.532,
            "edge": 6.8,
            "confidence": 65,
            "expected_value": 0.128,
            "kelly_stake": 0.13,
            "suggested_stake": 13.00,
            "reasoning": "Giannis em forma, Nuggets defesa fraca contra PF"
        },
        {
            "id": "bet_014",
            "sport": "dota2",
            "game": "PSG.LGD vs Team Aster",
            "league": "DPC China",
            "start_time": (datetime.utcnow() + timedelta(hours=15)).isoformat() + "Z",
            "market": "over_under",
            "selection": "Over 2.5 Maps",
            "odds": 1.92,
            "bookmaker": "Betway",
            "model_probability": 0.57,
            "implied_probability": 0.521,
            "edge": 4.9,
            "confidence": 59,
            "expected_value": 0.094,
            "kelly_stake": 0.09,
            "suggested_stake": 9.00,
            "reasoning": "Rivais equilibrados, histórico de Bo3 longos"
        },
        {
            "id": "bet_015",
            "sport": "tennis",
            "game": "Jannik Sinner vs Daniil Medvedev",
            "league": "Australian Open",
            "start_time": (datetime.utcnow() + timedelta(hours=16)).isoformat() + "Z",
            "market": "over_under",
            "selection": "Over 3.5 Sets",
            "odds": 1.85,
            "bookmaker": "Pinnacle",
            "model_probability": 0.61,
            "implied_probability": 0.541,
            "edge": 6.9,
            "confidence": 66,
            "expected_value": 0.129,
            "kelly_stake": 0.13,
            "suggested_stake": 13.00,
            "reasoning": "Jogadores equilibrados, finais longas esperadas"
        }
    ]
    
    # Filter by sport
    if sport is not None:
        filtered_bets = [bet for bet in mock_bets if bet["sport"] == sport]
    else:
        filtered_bets = mock_bets
    
    # Filter by min_edge and min_confidence
    filtered_bets = [
        bet for bet in filtered_bets 
        if bet["edge"] >= min_edge and bet["confidence"] >= min_confidence
    ]
    
    # Sort by edge (highest first)
    filtered_bets.sort(key=lambda x: x["edge"], reverse=True)
    
    # Calculate summary
    by_sport = {}
    total_stake = 0.0
    total_edge = 0.0
    
    for bet in filtered_bets:
        sport_name = bet["sport"]
        by_sport[sport_name] = by_sport.get(sport_name, 0) + 1
        total_stake += bet["suggested_stake"]
        total_edge += bet["edge"]
    
    avg_edge = total_edge / len(filtered_bets) if filtered_bets else 0.0
    
    summary = {
        "total_bets": len(filtered_bets),
        "by_sport": by_sport,
        "avg_edge": round(avg_edge, 2),
        "total_suggested_stake": round(total_stake, 2)
    }
    
    return {
        "value_bets": filtered_bets,
        "summary": summary
    }
