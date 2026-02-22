"""Tests for the paper trading system."""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import base first to avoid double registration
from database.models import Base

# Import models directly without going through __init__
import database.scorealarm_models as scorealarm_models
import database.paper_trading_models as paper_trading_models
from analysis.rating_system import EloRating, GlickoRating
from analysis.value_detector import ValueBetDetector

# Get classes from modules
ScorealarmSport = scorealarm_models.ScorealarmSport
ScorealarmMatch = scorealarm_models.ScorealarmMatch
ScorealarmTeam = scorealarm_models.ScorealarmTeam
ScorealarmTeamRating = scorealarm_models.ScorealarmTeamRating
OddsHistory = scorealarm_models.OddsHistory
PaperBet = paper_trading_models.PaperBet
PaperTradingStats = paper_trading_models.PaperTradingStats


# Test database setup
@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_sport(db_session):
    """Create a sample sport."""
    sport = ScorealarmSport(
        id=1,
        name="Counter-Strike 2",
        superbet_id=55,
        is_gold=False
    )
    db_session.add(sport)
    db_session.commit()
    return sport


@pytest.fixture
def sample_teams(db_session, sample_sport):
    """Create sample teams."""
    team1 = ScorealarmTeam(
        id=1,
        name="Team A",
        short_name="TEA",
        sport_id=sample_sport.id
    )
    team2 = ScorealarmTeam(
        id=2,
        name="Team B",
        short_name="TEB",
        sport_id=sample_sport.id
    )
    db_session.add(team1)
    db_session.add(team2)
    db_session.commit()
    return team1, team2


@pytest.fixture
def sample_match(db_session, sample_sport, sample_teams):
    """Create a sample match."""
    team1, team2 = sample_teams
    match = ScorealarmMatch(
        id=1,
        platform_id="test:match:1",
        sport_id=sample_sport.id,
        team1_id=team1.id,
        team2_id=team2.id,
        match_date=datetime.utcnow() + timedelta(hours=24),
        match_status=0,
        is_finished=False
    )
    db_session.add(match)
    db_session.commit()
    return match


class TestEloRating:
    """Test ELO rating system."""
    
    def test_calculate_expected_equal_ratings(self):
        """Test expected probability with equal ratings."""
        elo = EloRating()
        prob = elo.calculate_expected(1500, 1500)
        assert abs(prob - 0.5) < 0.01, "Equal ratings should give ~50% probability"
    
    def test_calculate_expected_higher_rating(self):
        """Test expected probability with higher rating."""
        elo = EloRating()
        prob = elo.calculate_expected(1600, 1400)
        assert prob > 0.5, "Higher rating should have >50% probability"
        assert prob < 1.0, "Probability should be less than 1.0"
    
    def test_update_ratings_win(self):
        """Test rating update after a win."""
        elo = EloRating()
        rating_a, rating_b = elo.update_ratings(1500, 1500, 1.0)
        assert rating_a > 1500, "Winner's rating should increase"
        assert rating_b < 1500, "Loser's rating should decrease"
    
    def test_update_ratings_draw(self):
        """Test rating update after a draw."""
        elo = EloRating()
        rating_a, rating_b = elo.update_ratings(1500, 1500, 0.5)
        assert abs(rating_a - 1500) < 1, "Equal draw should not change ratings much"
        assert abs(rating_b - 1500) < 1, "Equal draw should not change ratings much"


class TestGlickoRating:
    """Test Glicko rating system."""
    
    def test_default_values(self):
        """Test default Glicko values."""
        glicko = GlickoRating()
        assert glicko.default_rating == 1500
        assert glicko.default_rd == 350
        assert glicko.default_vol == 0.06
    
    def test_calculate_expected(self):
        """Test expected probability calculation."""
        glicko = GlickoRating()
        prob = glicko.calculate_expected(1500, 350, 1500, 350)
        assert 0 < prob < 1, "Probability should be between 0 and 1"
        assert abs(prob - 0.5) < 0.1, "Equal ratings should give ~50% probability"
    
    def test_update_rating(self):
        """Test rating update."""
        glicko = GlickoRating()
        new_rating, new_rd, new_vol = glicko.update_rating(
            rating=1500,
            rd=350,
            vol=0.06,
            opponent_rating=1400,
            opponent_rd=350,
            result=1.0
        )
        assert new_rating > 1500, "Winner's rating should increase"
        assert new_rd < 350, "RD should decrease after a match"


class TestValueBetDetector:
    """Test value bet detection."""
    
    def test_odds_to_probability(self):
        """Test odds to probability conversion."""
        detector = ValueBetDetector()
        
        # Odds of 2.0 should give 50% probability
        prob = detector.odds_to_probability(2.0)
        assert abs(prob - 0.5) < 0.01
        
        # Odds of 1.5 should give ~66.7% probability
        prob = detector.odds_to_probability(1.5)
        assert abs(prob - 0.667) < 0.01
    
    def test_calculate_edge(self):
        """Test edge calculation."""
        detector = ValueBetDetector()
        
        # Our probability is 60%, bookmaker odds imply 50%
        edge = detector.calculate_edge(0.6, 2.0)
        assert abs(edge - 0.1) < 0.01, "Edge should be 10%"
        
        # Our probability is 50%, bookmaker odds imply 50%
        edge = detector.calculate_edge(0.5, 2.0)
        assert abs(edge) < 0.01, "Edge should be ~0%"
    
    def test_analyze_match_with_edge(self, db_session, sample_match):
        """Test match analysis with positive edge."""
        detector = ValueBetDetector(min_edge=0.03)
        
        # Create odds that give edge
        odds = OddsHistory(
            match_id=sample_match.id,
            market_type="moneyline",
            team1_odds=2.5,  # Implies 40% probability
            team2_odds=1.6,  # Implies 62.5% probability
            bookmaker="superbet"
        )
        db_session.add(odds)
        db_session.commit()
        
        # Team ratings give team1 50% chance to win
        opportunities = detector.analyze_match(sample_match, 1500, 1500, odds)
        
        # Should find opportunity on team1 (50% our prob vs 40% implied)
        assert len(opportunities) >= 1
        assert any(opp["bet_on"] == "team1" for opp in opportunities)
    
    def test_analyze_match_no_edge(self, db_session, sample_match):
        """Test match analysis with no edge."""
        detector = ValueBetDetector(min_edge=0.03)
        
        # Create odds with no edge
        odds = OddsHistory(
            match_id=sample_match.id,
            market_type="moneyline",
            team1_odds=2.0,  # Implies 50% probability
            team2_odds=2.0,  # Implies 50% probability
            bookmaker="superbet"
        )
        db_session.add(odds)
        db_session.commit()
        
        # Team ratings also give 50/50
        opportunities = detector.analyze_match(sample_match, 1500, 1500, odds)
        
        # Should find no opportunities
        assert len(opportunities) == 0


class TestPaperBetModel:
    """Test PaperBet database model."""
    
    def test_create_paper_bet(self, db_session, sample_match):
        """Test creating a paper bet."""
        bet = PaperBet(
            match_id=sample_match.id,
            bet_on="team1",
            odds=2.0,
            stake=100.0,
            our_probability=0.6,
            implied_probability=0.5,
            edge=0.1,
            status="pending"
        )
        db_session.add(bet)
        db_session.commit()
        
        assert bet.id is not None
        assert bet.status == "pending"
        assert bet.profit is None
    
    def test_settle_winning_bet(self, db_session, sample_match):
        """Test settling a winning bet."""
        bet = PaperBet(
            match_id=sample_match.id,
            bet_on="team1",
            odds=2.0,
            stake=100.0,
            our_probability=0.6,
            implied_probability=0.5,
            edge=0.1,
            status="pending"
        )
        db_session.add(bet)
        db_session.commit()
        
        # Settle as won
        bet.status = "won"
        bet.profit = (bet.odds - 1) * bet.stake
        bet.settled_at = datetime.utcnow()
        db_session.commit()
        
        assert bet.status == "won"
        assert bet.profit == 100.0
        assert bet.settled_at is not None


class TestPaperTradingStats:
    """Test PaperTradingStats model."""
    
    def test_create_stats(self, db_session, sample_sport):
        """Test creating trading stats."""
        stats = PaperTradingStats(
            sport_id=sample_sport.id,
            total_bets=10,
            wins=6,
            losses=4,
            total_staked=1000.0,
            total_profit=200.0,
            avg_odds=2.0,
            avg_edge=0.05,
            roi=0.2
        )
        db_session.add(stats)
        db_session.commit()
        
        assert stats.id is not None
        assert stats.roi == 0.2
        assert stats.wins == 6
    
    def test_update_roi(self, db_session, sample_sport):
        """Test ROI calculation."""
        stats = PaperTradingStats(
            sport_id=sample_sport.id,
            total_bets=5,
            total_staked=500.0,
            total_profit=100.0
        )
        
        stats.roi = stats.total_profit / stats.total_staked
        db_session.add(stats)
        db_session.commit()
        
        assert abs(stats.roi - 0.2) < 0.01


class TestScorealarmTeamRating:
    """Test ScorealarmTeamRating model."""
    
    def test_create_team_rating(self, db_session, sample_teams):
        """Test creating team rating."""
        team1, _ = sample_teams
        
        rating = ScorealarmTeamRating(
            team_id=team1.id,
            elo_rating=1500.0,
            glicko_rating=1500.0,
            glicko_rd=350.0,
            glicko_vol=0.06,
            matches_played=0
        )
        db_session.add(rating)
        db_session.commit()
        
        assert rating.id is not None
        assert rating.elo_rating == 1500.0
        assert rating.matches_played == 0
    
    def test_update_after_match(self, db_session, sample_teams):
        """Test updating rating after match."""
        team1, _ = sample_teams
        
        rating = ScorealarmTeamRating(
            team_id=team1.id,
            elo_rating=1500.0,
            matches_played=0
        )
        db_session.add(rating)
        db_session.commit()
        
        # Update after match
        elo = EloRating()
        new_rating, _ = elo.update_ratings(1500, 1400, 1.0)
        rating.elo_rating = new_rating
        rating.matches_played += 1
        db_session.commit()
        
        assert rating.elo_rating > 1500
        assert rating.matches_played == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
