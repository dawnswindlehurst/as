"""Validation schemas for paper trading dashboard."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class PeriodInfo(BaseModel):
    """Period information."""
    start: str
    end: str
    days: int


class OverallMetrics(BaseModel):
    """Overall metrics for validation."""
    total_bets: int
    wins: int
    losses: int
    win_rate: float
    roi: float
    profit: float
    total_wagered: float
    avg_odds: float
    clv_average: float
    sharpe_ratio: float
    max_drawdown: float


class SportMetrics(BaseModel):
    """Metrics by sport."""
    sport: str
    name: str
    icon: str
    total_bets: int
    wins: int
    win_rate: float
    roi: float
    profit: float
    clv_average: float
    rank: int


class MarketMetrics(BaseModel):
    """Metrics by market."""
    market: str
    name: str
    total_bets: int
    wins: int
    win_rate: float
    roi: float
    rank: int


class EquityPoint(BaseModel):
    """Equity curve data point."""
    date: str
    bankroll: float
    profit: float


class CalibrationMetrics(BaseModel):
    """Calibration metrics."""
    brier_score: float
    calibration_error: float
    overround_beat_rate: float


class Insight(BaseModel):
    """Insight message."""
    type: str  # success, warning, info, danger
    title: str
    message: str


class ValidationMetrics(BaseModel):
    """Complete validation metrics response."""
    period: PeriodInfo
    overall: OverallMetrics
    by_sport: List[SportMetrics]
    by_market: List[MarketMetrics]
    equity_curve: List[EquityPoint]
    calibration: CalibrationMetrics
    insights: List[Insight]
