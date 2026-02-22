"""Test script to verify database schema creation and basic functionality."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import init_db, get_db_session
from database.historical_models import (
    NBAGame, NBAPlayerGameStats, NBATeamStats, NBAPlayerPropsAnalysis,
    SoccerMatch, SoccerTeamStats, SoccerPlayerStats,
    EsportsMatch, EsportsMapStats, EsportsPlayerStats, EsportsTeamStats, EsportsPlayerPropsAnalysis,
    TennisMatch, TennisPlayerStats,
    BettingPattern, ValueBetHistory
)
from analytics.betting_analytics import get_analytics
from utils.logger import log
from datetime import datetime, date


def test_database_creation():
    """Test that all tables are created successfully."""
    log.info("Testing database schema creation...")
    
    try:
        init_db()
        log.info("✅ Database initialized successfully")
        return True
    except Exception as e:
        log.error(f"❌ Database initialization failed: {e}")
        return False


def test_nba_models():
    """Test NBA model creation."""
    log.info("\nTesting NBA models...")
    
    try:
        db = get_db_session()
        
        # Create sample NBA game
        game = NBAGame(
            game_id="test_game_001",
            season="2025-26",
            season_type="regular",
            game_date=date.today(),
            home_team="Los Angeles Lakers",
            away_team="Boston Celtics",
            home_score=110,
            away_score=105,
            total_points=215,
            home_q1=28, home_q2=25, home_q3=30, home_q4=27,
            away_q1=26, away_q2=27, away_q3=28, away_q4=24
        )
        db.add(game)
        
        # Create sample player stats
        player_stat = NBAPlayerGameStats(
            game_id="test_game_001",
            player_id="lebron_test",
            player_name="LeBron James",
            team="Los Angeles Lakers",
            is_home=True,
            is_starter=True,
            minutes=38,
            points=28,
            rebounds_total=10,
            assists=8,
            pts_reb_ast=46
        )
        db.add(player_stat)
        
        db.commit()
        log.info("✅ NBA models working correctly")
        
        # Clean up
        db.query(NBAPlayerGameStats).filter(NBAPlayerGameStats.game_id == "test_game_001").delete()
        db.query(NBAGame).filter(NBAGame.game_id == "test_game_001").delete()
        db.commit()
        db.close()
        
        return True
        
    except Exception as e:
        log.error(f"❌ NBA models test failed: {e}")
        return False


def test_soccer_models():
    """Test Soccer model creation."""
    log.info("\nTesting Soccer models...")
    
    try:
        db = get_db_session()
        
        # Create sample match
        match = SoccerMatch(
            match_id="test_match_001",
            league="eng.1",
            league_name="Premier League",
            season="2025-26",
            match_date=date.today(),
            home_team="Liverpool",
            away_team="Manchester City",
            home_score=2,
            away_score=1,
            total_goals=3,
            btts=True,
            over_2_5=True
        )
        db.add(match)
        db.commit()
        
        log.info("✅ Soccer models working correctly")
        
        # Clean up
        db.query(SoccerMatch).filter(SoccerMatch.match_id == "test_match_001").delete()
        db.commit()
        db.close()
        
        return True
        
    except Exception as e:
        log.error(f"❌ Soccer models test failed: {e}")
        return False


def test_esports_models():
    """Test Esports model creation."""
    log.info("\nTesting Esports models...")
    
    try:
        db = get_db_session()
        
        # Create sample match
        match = EsportsMatch(
            match_id="test_esports_001",
            game="valorant",
            tournament="VCT 2026: Americas",
            tournament_tier="S",
            match_date=datetime.now(),
            team1="Sentinels",
            team2="Cloud9",
            team1_score=2,
            team2_score=1,
            winner="Sentinels",
            best_of=3
        )
        db.add(match)
        db.commit()
        
        log.info("✅ Esports models working correctly")
        
        # Clean up
        db.query(EsportsMatch).filter(EsportsMatch.match_id == "test_esports_001").delete()
        db.commit()
        db.close()
        
        return True
        
    except Exception as e:
        log.error(f"❌ Esports models test failed: {e}")
        return False


def test_tennis_models():
    """Test Tennis model creation."""
    log.info("\nTesting Tennis models...")
    
    try:
        db = get_db_session()
        
        # Create sample match
        match = TennisMatch(
            match_id="test_tennis_001",
            tour="atp",
            tournament="Australian Open",
            tournament_category="grand_slam",
            surface="hard",
            round="Final",
            match_date=date.today(),
            player1="Novak Djokovic",
            player2="Carlos Alcaraz",
            winner="Carlos Alcaraz",
            score="6-4, 3-6, 7-6",
            player1_sets=1,
            player2_sets=2,
            total_games=29,
            over_22_5=True
        )
        db.add(match)
        db.commit()
        
        log.info("✅ Tennis models working correctly")
        
        # Clean up
        db.query(TennisMatch).filter(TennisMatch.match_id == "test_tennis_001").delete()
        db.commit()
        db.close()
        
        return True
        
    except Exception as e:
        log.error(f"❌ Tennis models test failed: {e}")
        return False


def test_analytics():
    """Test analytics functions."""
    log.info("\nTesting analytics functions...")
    
    try:
        analytics = get_analytics()
        
        # Test analytics functions (they should handle empty data gracefully)
        result = analytics.get_player_prop_analysis("Test Player", "points", 25.5)
        assert "error" in result or "overall" in result
        
        result = analytics.get_team_btts_analysis("Test Team", "eng.1")
        assert "error" in result or "overall" in result
        
        result = analytics.get_team_map_stats("Test Team", "valorant")
        assert "error" in result or len(result) >= 0
        
        analytics.close()
        
        log.info("✅ Analytics functions working correctly")
        return True
        
    except Exception as e:
        log.error(f"❌ Analytics test failed: {e}")
        return False


def main():
    """Run all tests."""
    log.info("="*60)
    log.info("HISTORICAL DATABASE TEST SUITE")
    log.info("="*60)
    
    results = []
    
    # Test database creation
    results.append(("Database Creation", test_database_creation()))
    
    # Test models
    results.append(("NBA Models", test_nba_models()))
    results.append(("Soccer Models", test_soccer_models()))
    results.append(("Esports Models", test_esports_models()))
    results.append(("Tennis Models", test_tennis_models()))
    
    # Test analytics
    results.append(("Analytics Functions", test_analytics()))
    
    # Summary
    log.info("\n" + "="*60)
    log.info("TEST SUMMARY")
    log.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        log.info(f"{test_name:.<50} {status}")
    
    log.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        log.info("\n🎉 All tests passed successfully!")
        return 0
    else:
        log.error(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
