"""Validation routes for paper trading dashboard."""
from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from api.schemas.validation import (
    ValidationMetrics,
    PeriodInfo,
    OverallMetrics,
    SportMetrics,
    MarketMetrics,
    EquityPoint,
    CalibrationMetrics,
    Insight
)

router = APIRouter()


@router.get("/validation/metrics", response_model=ValidationMetrics)
async def get_validation_metrics(
    days: int = Query(7, description="Number of days to analyze")
) -> ValidationMetrics:
    """
    Get validation metrics for paper trading.
    
    Args:
        days: Number of days to analyze (default: 7)
        
    Returns:
        Validation metrics including performance by sport, market, and overall stats
    """
    # Calculate period
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Mock data for demonstration
    # In production, this would query actual betting records from the database
    
    return ValidationMetrics(
        period=PeriodInfo(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            days=days
        ),
        overall=OverallMetrics(
            total_bets=156,
            wins=89,
            losses=67,
            win_rate=57.05,
            roi=8.4,
            profit=84.00,
            total_wagered=1000.00,
            avg_odds=1.95,
            clv_average=2.3,
            sharpe_ratio=1.45,
            max_drawdown=-12.5
        ),
        by_sport=[
            SportMetrics(
                sport="nba",
                name="NBA",
                icon="🏀",
                total_bets=35,
                wins=22,
                win_rate=62.86,
                roi=12.5,
                profit=43.75,
                clv_average=3.1,
                rank=1
            ),
            SportMetrics(
                sport="valorant",
                name="Valorant",
                icon="🎯",
                total_bets=28,
                wins=17,
                win_rate=60.71,
                roi=9.8,
                profit=27.44,
                clv_average=2.8,
                rank=2
            ),
            SportMetrics(
                sport="cs2",
                name="CS2",
                icon="🔫",
                total_bets=25,
                wins=15,
                win_rate=60.00,
                roi=7.2,
                profit=18.00,
                clv_average=2.5,
                rank=3
            ),
            SportMetrics(
                sport="soccer",
                name="Futebol",
                icon="⚽",
                total_bets=22,
                wins=12,
                win_rate=54.55,
                roi=5.1,
                profit=11.22,
                clv_average=2.0,
                rank=4
            ),
            SportMetrics(
                sport="lol",
                name="LoL",
                icon="⚔️",
                total_bets=20,
                wins=11,
                win_rate=55.00,
                roi=3.8,
                profit=7.60,
                clv_average=1.8,
                rank=5
            ),
            SportMetrics(
                sport="tennis",
                name="Tênis",
                icon="🎾",
                total_bets=15,
                wins=8,
                win_rate=53.33,
                roi=2.1,
                profit=3.15,
                clv_average=1.5,
                rank=6
            ),
            SportMetrics(
                sport="dota2",
                name="Dota 2",
                icon="🏆",
                total_bets=11,
                wins=4,
                win_rate=36.36,
                roi=-1.2,
                profit=-1.32,
                clv_average=0.5,
                rank=7
            )
        ],
        by_market=[
            MarketMetrics(
                market="moneyline",
                name="Moneyline",
                total_bets=45,
                wins=28,
                win_rate=62.22,
                roi=11.2,
                rank=1
            ),
            MarketMetrics(
                market="player_props",
                name="Player Props",
                total_bets=30,
                wins=18,
                win_rate=60.00,
                roi=8.5,
                rank=2
            ),
            MarketMetrics(
                market="over_under",
                name="Over/Under",
                total_bets=38,
                wins=21,
                win_rate=55.26,
                roi=6.8,
                rank=3
            ),
            MarketMetrics(
                market="btts",
                name="BTTS",
                total_bets=20,
                wins=11,
                win_rate=55.00,
                roi=5.2,
                rank=4
            ),
            MarketMetrics(
                market="spread",
                name="Spread/Handicap",
                total_bets=23,
                wins=11,
                win_rate=47.83,
                roi=-3.5,
                rank=5
            )
        ],
        equity_curve=[
            EquityPoint(date=(start_date + timedelta(days=0)).strftime("%Y-%m-%d"), bankroll=1000, profit=0),
            EquityPoint(date=(start_date + timedelta(days=1)).strftime("%Y-%m-%d"), bankroll=1025, profit=25),
            EquityPoint(date=(start_date + timedelta(days=2)).strftime("%Y-%m-%d"), bankroll=1010, profit=10),
            EquityPoint(date=(start_date + timedelta(days=3)).strftime("%Y-%m-%d"), bankroll=1045, profit=45),
            EquityPoint(date=(start_date + timedelta(days=4)).strftime("%Y-%m-%d"), bankroll=1032, profit=32),
            EquityPoint(date=(start_date + timedelta(days=5)).strftime("%Y-%m-%d"), bankroll=1068, profit=68),
            EquityPoint(date=(start_date + timedelta(days=6)).strftime("%Y-%m-%d"), bankroll=1055, profit=55),
            EquityPoint(date=(start_date + timedelta(days=7)).strftime("%Y-%m-%d"), bankroll=1084, profit=84)
        ],
        calibration=CalibrationMetrics(
            brier_score=0.21,
            calibration_error=0.03,
            overround_beat_rate=68.5
        ),
        insights=[
            Insight(
                type="success",
                title="NBA está performando bem",
                message="ROI de 12.5% com 35 apostas. Considere aumentar exposição."
            ),
            Insight(
                type="warning",
                title="Spread com ROI negativo",
                message="Mercado de Spread com -3.5% ROI. Revisar modelo ou reduzir stakes."
            ),
            Insight(
                type="info",
                title="CLV positivo consistente",
                message="CLV médio de 2.3% indica edge real. Modelo bem calibrado."
            )
        ]
    )
