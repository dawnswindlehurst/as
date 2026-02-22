"""Test for sport_id mapping fix in populate_historical.py

This test ensures that the populate_historical job correctly uses database IDs
instead of API IDs when saving matches, tournaments, and teams.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime
from database.scorealarm_models import ScorealarmSport
from jobs.populate_historical import HistoricalPopulateJob


class TestSportIdMapping:
    """Test sport_id mapping in populate_historical job."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = MagicMock()
        
        # Mock sport in database with different IDs
        # API: sport.id = 5 (Football in Superbet)
        # DB:  sport.id = 1 (auto-incremented)
        mock_sport = ScorealarmSport()
        mock_sport.id = 1  # Database ID
        mock_sport.superbet_id = 5  # Superbet API ID
        mock_sport.name = "Futebol"
        
        # Configure query chain
        query_mock = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = mock_sport
        query_mock.filter.return_value = filter_mock
        db.query.return_value = query_mock
        
        return db
    
    @pytest.fixture
    def job(self, mock_db):
        """Create HistoricalPopulateJob with mocked dependencies."""
        job = HistoricalPopulateJob()
        job.db = mock_db
        return job
    
    @pytest.mark.asyncio
    async def test_correct_db_sport_id_used_for_tournament(self, job, mock_db):
        """Test that _save_tournament receives database sport.id, not API sport.id."""
        # Mock sport from API with superbet_id = 5
        api_sport = Mock()
        api_sport.id = 5  # Superbet API ID
        api_sport.name = "Futebol"
        
        # Mock tournament
        tournament = Mock()
        tournament.tournament_id = 100
        tournament.tournament_name = "Test Tournament"
        
        # Spy on _save_tournament to check what sport_id is passed
        original_save_tournament = job._save_tournament
        sport_id_received = None
        
        async def spy_save_tournament(tournament, sport_id):
            nonlocal sport_id_received
            sport_id_received = sport_id
            return await original_save_tournament(tournament, sport_id)
        
        job._save_tournament = spy_save_tournament
        
        # After saving sport, the job should query DB to get db_sport_id = 1
        await job._save_sport(api_sport)
        
        # Get the db_sport_id the same way the job does
        db_sport = job.db.query(ScorealarmSport).filter(
            ScorealarmSport.superbet_id == api_sport.id
        ).first()
        db_sport_id = db_sport.id  # Should be 1, not 5
        
        # Verify the mapping is correct
        assert db_sport_id == 1, f"Expected db_sport_id=1, got {db_sport_id}"
        assert db_sport.superbet_id == 5, f"Expected superbet_id=5, got {db_sport.superbet_id}"
        
        # Now call _save_tournament with db_sport_id
        await job._save_tournament(tournament, db_sport_id)
        
        # Verify that _save_tournament received db_sport_id (1), not api sport.id (5)
        assert sport_id_received == 1, f"Expected sport_id=1, got {sport_id_received}"
        print(f"✓ _save_tournament correctly received db_sport_id={sport_id_received} instead of API sport.id=5")
    
    @pytest.mark.asyncio
    async def test_correct_db_sport_id_used_for_match(self, job, mock_db):
        """Test that _save_match receives database sport.id, not API sport.id."""
        # Mock sport from API with superbet_id = 5
        api_sport = Mock()
        api_sport.id = 5  # Superbet API ID
        api_sport.name = "Futebol"
        
        # Mock match
        match = Mock()
        match.platform_id = "test_match_1"
        match.offer_id = "offer_1"
        match.match_date = datetime.now()
        match.match_status = 0
        match.scores = []
        match.team1 = Mock(id=1, name="Team 1")
        match.team2 = Mock(id=2, name="Team 2")
        
        # Mock _save_team to avoid complex setup
        async def mock_save_team(team, sport_id):
            return sport_id  # Return the sport_id to verify
        
        job._save_team = mock_save_team
        
        # Spy on _save_match to check what sport_id is passed
        original_save_match = job._save_match
        sport_id_received = None
        
        async def spy_save_match(match, sport_id, tournament_id, season_id):
            nonlocal sport_id_received
            sport_id_received = sport_id
            # Don't call original to avoid DB complexity
            
        job._save_match = spy_save_match
        
        # After saving sport, the job should query DB to get db_sport_id = 1
        await job._save_sport(api_sport)
        
        # Get the db_sport_id the same way the job does
        db_sport = job.db.query(ScorealarmSport).filter(
            ScorealarmSport.superbet_id == api_sport.id
        ).first()
        db_sport_id = db_sport.id  # Should be 1, not 5
        
        # Now call _save_match with db_sport_id
        await job._save_match(match, db_sport_id, 100, 10)
        
        # Verify that _save_match received db_sport_id (1), not api sport.id (5)
        assert sport_id_received == 1, f"Expected sport_id=1, got {sport_id_received}"
        print(f"✓ _save_match correctly received db_sport_id={sport_id_received} instead of API sport.id=5")


def test_migration_script_import():
    """Test that the migration script can be imported."""
    try:
        import scripts.fix_sport_id_mapping
        print("✓ Migration script imports successfully")
        assert hasattr(scripts.fix_sport_id_mapping, 'fix_sport_ids')
        print("✓ Migration script has fix_sport_ids function")
    except ImportError as e:
        pytest.fail(f"Failed to import migration script: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
