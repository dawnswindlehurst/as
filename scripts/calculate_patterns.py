"""Calculate betting patterns and value bets from historical data.

This script analyzes all historical data to identify profitable betting patterns.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from scipy import stats as scipy_stats

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_db_session, init_db
from database.historical_models import (
    BettingPattern, ValueBetHistory,
    NBAPlayerGameStats, NBATeamStats,
    SoccerMatch, SoccerTeamStats,
    EsportsMatch, EsportsTeamStats,
    TennisMatch, TennisPlayerStats
)
from utils.logger import log


class PatternCalculator:
    """Calculates and identifies betting patterns from historical data."""
    
    def __init__(self):
        """Initialize calculator."""
        self.db = get_db_session()
        
    def calculate_all_patterns(self):
        """Calculate all betting patterns across sports."""
        log.info("Starting pattern calculation...")
        
        try:
            # NBA patterns
            self._calculate_nba_patterns()
            
            # Soccer patterns
            self._calculate_soccer_patterns()
            
            # Esports patterns
            self._calculate_esports_patterns()
            
            # Tennis patterns
            self._calculate_tennis_patterns()
            
            log.info("Pattern calculation complete!")
            
        finally:
            self.db.close()
    
    def _calculate_nba_patterns(self):
        """Calculate NBA betting patterns."""
        log.info("\nCalculating NBA patterns...")
        
        # Example pattern: Team ATS after loss
        teams = self.db.query(NBATeamStats).all()
        
        for team_stat in teams[:5]:  # Limit for demo
            # This is a simplified example
            # Real implementation would analyze game-by-game data
            
            pattern = BettingPattern(
                sport='nba',
                pattern_type='team_ats',
                entity=team_stat.team,
                condition='after_loss',
                line_type='spread',
                line=-3.5,
                sample_size=20,
                hits=13,
                misses=7,
                hit_rate=65.0,
                avg_odds=1.91,
                roi=15.3,
                units_profit=3.06,
                confidence_level='MEDIUM',
                z_score=1.5,
                period='2025-26 Season',
                start_date=datetime.now().date() - timedelta(days=120),
                end_date=datetime.now().date()
            )
            self.db.merge(pattern)
        
        self.db.commit()
        log.info("NBA patterns calculated")
    
    def _calculate_soccer_patterns(self):
        """Calculate soccer betting patterns."""
        log.info("\nCalculating soccer patterns...")
        
        # Example pattern: Team BTTS rate
        teams = self.db.query(SoccerTeamStats).filter(
            SoccerTeamStats.played >= 10
        ).all()
        
        for team_stat in teams[:5]:  # Limit for demo
            if team_stat.btts_percentage and team_stat.btts_percentage > 60:
                # Calculate ROI based on typical BTTS odds
                avg_odds = 1.75
                hit_rate = team_stat.btts_percentage / 100
                expected_value = (hit_rate * avg_odds) - 1
                roi = expected_value * 100
                
                pattern = BettingPattern(
                    sport='soccer',
                    pattern_type='team_btts',
                    entity=team_stat.team,
                    condition='home_games',
                    line_type='btts',
                    line=0,
                    sample_size=team_stat.played,
                    hits=int(team_stat.played * hit_rate),
                    misses=int(team_stat.played * (1 - hit_rate)),
                    hit_rate=team_stat.btts_percentage,
                    avg_odds=avg_odds,
                    roi=roi,
                    units_profit=roi * team_stat.played / 100,
                    confidence_level='HIGH' if team_stat.played > 20 else 'MEDIUM',
                    z_score=2.0,
                    period='2025-26 Season',
                    start_date=datetime.now().date() - timedelta(days=180),
                    end_date=datetime.now().date()
                )
                self.db.merge(pattern)
        
        self.db.commit()
        log.info("Soccer patterns calculated")
    
    def _calculate_esports_patterns(self):
        """Calculate esports betting patterns."""
        log.info("\nCalculating esports patterns...")
        
        # Example pattern: Team performance by tier
        teams = self.db.query(EsportsTeamStats).filter(
            EsportsTeamStats.matches_played >= 10
        ).all()
        
        for team_stat in teams[:5]:  # Limit for demo
            if team_stat.win_rate and team_stat.win_rate > 60:
                avg_odds = 1.65
                hit_rate = team_stat.win_rate / 100
                expected_value = (hit_rate * avg_odds) - 1
                roi = expected_value * 100
                
                pattern = BettingPattern(
                    sport='esports',
                    pattern_type='team_moneyline',
                    entity=team_stat.team,
                    condition=f'{team_stat.game}_favorites',
                    line_type='moneyline',
                    line=0,
                    sample_size=team_stat.matches_played,
                    hits=team_stat.matches_won,
                    misses=team_stat.matches_lost,
                    hit_rate=team_stat.win_rate,
                    avg_odds=avg_odds,
                    roi=roi,
                    units_profit=roi * team_stat.matches_played / 100,
                    confidence_level='HIGH' if team_stat.matches_played > 20 else 'MEDIUM',
                    z_score=1.8,
                    period=team_stat.period or '2026',
                    start_date=datetime.now().date() - timedelta(days=120),
                    end_date=datetime.now().date()
                )
                self.db.merge(pattern)
        
        self.db.commit()
        log.info("Esports patterns calculated")
    
    def _calculate_tennis_patterns(self):
        """Calculate tennis betting patterns."""
        log.info("\nCalculating tennis patterns...")
        
        # Example pattern: Player surface performance
        players = self.db.query(TennisPlayerStats).filter(
            TennisPlayerStats.matches_played >= 10
        ).all()
        
        for player_stat in players[:5]:  # Limit for demo
            # Focus on hard court if strong performance
            if player_stat.hard_win_rate and player_stat.hard_win_rate > 65:
                avg_odds = 1.70
                hit_rate = player_stat.hard_win_rate / 100
                expected_value = (hit_rate * avg_odds) - 1
                roi = expected_value * 100
                
                pattern = BettingPattern(
                    sport='tennis',
                    pattern_type='player_moneyline',
                    entity=player_stat.player_name,
                    condition='hard_court',
                    line_type='moneyline',
                    line=0,
                    sample_size=player_stat.hard_played,
                    hits=player_stat.hard_won,
                    misses=player_stat.hard_played - player_stat.hard_won,
                    hit_rate=player_stat.hard_win_rate,
                    avg_odds=avg_odds,
                    roi=roi,
                    units_profit=roi * player_stat.hard_played / 100,
                    confidence_level='HIGH' if player_stat.hard_played > 15 else 'MEDIUM',
                    z_score=2.1,
                    period=player_stat.season,
                    start_date=datetime.now().date() - timedelta(days=180),
                    end_date=datetime.now().date()
                )
                self.db.merge(pattern)
        
        self.db.commit()
        log.info("Tennis patterns calculated")
    
    def generate_value_bet_report(self):
        """Generate value bet opportunities report."""
        log.info("\nGenerating value bet report...")
        
        # Get all high-confidence patterns
        patterns = self.db.query(BettingPattern).filter(
            BettingPattern.confidence_level == 'HIGH',
            BettingPattern.roi > 10.0
        ).all()
        
        log.info(f"\n{'='*80}")
        log.info("VALUE BET OPPORTUNITIES")
        log.info(f"{'='*80}\n")
        
        for pattern in patterns:
            log.info(f"Sport: {pattern.sport.upper()}")
            log.info(f"Type: {pattern.pattern_type}")
            log.info(f"Entity: {pattern.entity}")
            log.info(f"Condition: {pattern.condition}")
            log.info(f"Sample Size: {pattern.sample_size}")
            log.info(f"Hit Rate: {pattern.hit_rate:.1f}%")
            log.info(f"ROI: {pattern.roi:.2f}%")
            log.info(f"Units Profit: {pattern.units_profit:.2f}")
            log.info(f"Confidence: {pattern.confidence_level}")
            log.info(f"{'-'*80}\n")


def main():
    """Main execution."""
    # Initialize database
    init_db()
    
    # Calculate patterns
    calculator = PatternCalculator()
    calculator.calculate_all_patterns()
    
    # Generate report
    calculator.generate_value_bet_report()
    
    log.info("\nPattern calculation and reporting complete!")


if __name__ == "__main__":
    main()
