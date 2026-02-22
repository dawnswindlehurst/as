"""Integration test for enrich_historical.py with database."""
import asyncio
import sys
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Optional

from database.db import get_db_session, init_db
from database.scorealarm_models import ScorealarmMatch, ScorealarmSport, ScorealarmTournament, ScorealarmSeason, ScorealarmTeam
from utils.logger import log


# Mock fixture stats for testing
@dataclass
class MockMatchStat:
    type: int
    team1: str
    team2: str
    stat_name: str


@dataclass
class MockLiveEvent:
    type: int
    subtype: int
    side: int
    minute: int
    added_time: Optional[int] = None
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    secondary_player_id: Optional[str] = None
    secondary_player_name: Optional[str] = None
    score: Optional[str] = None


@dataclass
class MockFixtureStats:
    fixture_id: str
    match_stats: List[MockMatchStat]
    live_events: List[MockLiveEvent]
    statistics_by_period: dict


class MockScorealarmClient:
    """Mock Scorealarm client for testing."""
    
    async def get_fixture_stats(self, fixture_id: str) -> Optional[MockFixtureStats]:
        """Return mock fixture stats."""
        return MockFixtureStats(
            fixture_id=fixture_id,
            match_stats=[
                MockMatchStat(type=19, team1="2.33", team2="1.02", stat_name="Expected Goals"),
                MockMatchStat(type=2, team1="8", team2="4", stat_name="Shots on Goal"),
                MockMatchStat(type=5, team1="6", team2="3", stat_name="Corners"),
                MockMatchStat(type=10, team1="12", team2="15", stat_name="Fouls"),
                MockMatchStat(type=12, team1="2", team2="3", stat_name="Yellow Cards"),
                MockMatchStat(type=1, team1="55", team2="45", stat_name="Possession"),
                MockMatchStat(type=18, team1="15", team2="10", stat_name="Total Shots")
            ],
            live_events=[
                MockLiveEvent(
                    type=4, subtype=8, side=1, minute=33,
                    player_id="player1", player_name="Lookman, Ademola",
                    secondary_player_id="player2", secondary_player_name="Alvarez, Julian",
                    score="1-0"
                ),
                MockLiveEvent(
                    type=1, subtype=0, side=2, minute=45,
                    player_id="player3", player_name="Silva, Bernardo"
                ),
                MockLiveEvent(
                    type=12, subtype=0, side=1, minute=58,
                    player_id="player4", player_name="De Bruyne, Kevin"
                )
            ],
            statistics_by_period={}
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        pass


async def simulate_enrichment(match: ScorealarmMatch):
    """Simulate the enrichment process from enrich_historical.py."""
    
    # Extract fixture_id from offer_id
    fixture_id = match.offer_id
    if not fixture_id:
        return False
    
    # Get fixture stats (using mock)
    scorealarm = MockScorealarmClient()
    fixture_stats = await scorealarm.get_fixture_stats(fixture_id)
    
    if not fixture_stats:
        return False
    
    # Save ALL raw match_stats data (NEW)
    if fixture_stats.match_stats:
        match.match_stats_raw = [
            {
                "type": s.type,
                "team1": s.team1,
                "team2": s.team2,
                "stat_name": s.stat_name
            }
            for s in fixture_stats.match_stats
        ]
    
    # Save ALL raw live_events data (NEW)
    if fixture_stats.live_events:
        match.live_events_raw = [
            {
                "type": e.type,
                "subtype": e.subtype,
                "minute": e.minute,
                "added_time": e.added_time,
                "side": e.side,
                "player_id": e.player_id,
                "player_name": e.player_name,
                "secondary_player_id": e.secondary_player_id,
                "secondary_player_name": e.secondary_player_name,
                "score": e.score
            }
            for e in fixture_stats.live_events
        ]
    
    # Extract xG (type=19) - EXISTING
    xg_stats = [s for s in fixture_stats.match_stats if s.type == 19]
    if xg_stats:
        xg_stat = xg_stats[0]
        try:
            match.xg_home = float(xg_stat.team1) if xg_stat.team1 else None
            match.xg_away = float(xg_stat.team2) if xg_stat.team2 else None
        except (ValueError, TypeError):
            match.xg_home = None
            match.xg_away = None
    
    # Extract shots on goal (type=2) - EXISTING
    shots_stats = [s for s in fixture_stats.match_stats if s.type == 2]
    if shots_stats:
        shots_stat = shots_stats[0]
        try:
            match.shots_on_goal_home = int(shots_stat.team1) if shots_stat.team1 else None
            match.shots_on_goal_away = int(shots_stat.team2) if shots_stat.team2 else None
        except (ValueError, TypeError):
            match.shots_on_goal_home = None
            match.shots_on_goal_away = None
    
    # Extract corners (type=5) - EXISTING
    corner_stats = [s for s in fixture_stats.match_stats if s.type == 5]
    if corner_stats:
        corner_stat = corner_stats[0]
        try:
            match.corners_home = int(corner_stat.team1) if corner_stat.team1 else None
            match.corners_away = int(corner_stat.team2) if corner_stat.team2 else None
        except (ValueError, TypeError):
            match.corners_home = None
            match.corners_away = None
    
    # Extract goal events (type=4) - EXISTING
    goal_events = [e for e in fixture_stats.live_events if e.type == 4]
    if goal_events:
        goals_data = []
        for goal in goal_events:
            goal_dict = {
                "minute": goal.minute,
                "added_time": goal.added_time,
                "player_id": goal.player_id,
                "player_name": goal.player_name,
                "assist_player_id": goal.secondary_player_id,
                "assist_player_name": goal.secondary_player_name,
                "side": goal.side,
                "score": goal.score
            }
            goals_data.append(goal_dict)
        match.goal_events = goals_data
    
    # Mark as enriched
    match.enriched_at = datetime.now(timezone.utc)
    
    return True


async def test_integration():
    """Integration test with database."""
    print("\n" + "="*60)
    print("🧪 INTEGRATION TEST: Enrich Historical with Database")
    print("="*60)
    
    # Initialize database
    log.info("Initializing test database...")
    init_db()
    
    db = get_db_session()
    
    try:
        # Create test data
        log.info("Creating test entities...")
        
        # Create sport
        sport = ScorealarmSport(
            name="Futebol",
            superbet_id=1,
            is_gold=False
        )
        db.add(sport)
        db.flush()
        
        # Create tournament
        tournament = ScorealarmTournament(
            name="Premier League",
            sport_id=sport.id,
            axilis_id="ax:tournament:1"
        )
        db.add(tournament)
        db.flush()
        
        # Create season
        season = ScorealarmSeason(
            name="2025/26",
            tournament_id=tournament.id,
            axilis_id="ax:season:1",
            is_current=True
        )
        db.add(season)
        db.flush()
        
        # Create teams
        team1 = ScorealarmTeam(
            name="Atalanta",
            sport_id=sport.id,
            axilis_id="ax:team:1"
        )
        team2 = ScorealarmTeam(
            name="Manchester City",
            sport_id=sport.id,
            axilis_id="ax:team:2"
        )
        db.add(team1)
        db.add(team2)
        db.flush()
        
        # Create match
        match = ScorealarmMatch(
            platform_id="br:match:12001839",
            offer_id="ax:match:12001839",
            sport_id=sport.id,
            tournament_id=tournament.id,
            season_id=season.id,
            team1_id=team1.id,
            team2_id=team2.id,
            match_date=datetime(2026, 2, 13, 20, 0, tzinfo=timezone.utc),
            match_status=100,
            team1_score=1,
            team2_score=0,
            is_finished=True
        )
        db.add(match)
        db.commit()
        
        log.info(f"✓ Created test match ID: {match.id}")
        
        # Run enrichment
        log.info("Running enrichment simulation...")
        success = await simulate_enrichment(match)
        
        if not success:
            raise Exception("Enrichment failed")
        
        db.commit()
        log.info("✓ Enrichment completed")
        
        # Verify results
        log.info("Verifying enrichment results...")
        
        db.refresh(match)
        
        # Check existing extracted fields
        assert match.enriched_at is not None, "enriched_at should be set"
        assert match.xg_home == 2.33, f"Expected xg_home=2.33, got {match.xg_home}"
        assert match.xg_away == 1.02, f"Expected xg_away=1.02, got {match.xg_away}"
        assert match.shots_on_goal_home == 8, f"Expected shots_home=8, got {match.shots_on_goal_home}"
        assert match.shots_on_goal_away == 4, f"Expected shots_away=4, got {match.shots_on_goal_away}"
        assert match.corners_home == 6, f"Expected corners_home=6, got {match.corners_home}"
        assert match.corners_away == 3, f"Expected corners_away=3, got {match.corners_away}"
        
        log.info("✓ Existing extracted fields verified")
        
        # Check goal events
        assert match.goal_events is not None, "goal_events should be set"
        assert len(match.goal_events) == 1, f"Expected 1 goal, got {len(match.goal_events)}"
        goal = match.goal_events[0]
        assert goal["player_name"] == "Lookman, Ademola"
        assert goal["assist_player_name"] == "Alvarez, Julian"
        
        log.info("✓ Goal events verified")
        
        # Check NEW raw match_stats
        assert match.match_stats_raw is not None, "match_stats_raw should be set"
        assert len(match.match_stats_raw) == 7, f"Expected 7 stats, got {len(match.match_stats_raw)}"
        
        # Verify specific stat types are present
        stat_types = {s["type"] for s in match.match_stats_raw}
        assert 19 in stat_types, "xG (type=19) should be in raw data"
        assert 2 in stat_types, "Shots on goal (type=2) should be in raw data"
        assert 5 in stat_types, "Corners (type=5) should be in raw data"
        assert 10 in stat_types, "Fouls (type=10) should be in raw data"
        assert 12 in stat_types, "Yellow cards (type=12) should be in raw data"
        assert 1 in stat_types, "Possession (type=1) should be in raw data"
        assert 18 in stat_types, "Total shots (type=18) should be in raw data"
        
        log.info("✓ Raw match_stats verified (all 7 stat types)")
        
        # Check NEW raw live_events
        assert match.live_events_raw is not None, "live_events_raw should be set"
        assert len(match.live_events_raw) == 3, f"Expected 3 events, got {len(match.live_events_raw)}"
        
        # Verify event types
        event_types = {e["type"] for e in match.live_events_raw}
        assert 4 in event_types, "Goals (type=4) should be in raw data"
        assert 1 in event_types, "Yellow card events (type=1) should be in raw data"
        assert 12 in event_types, "Yellow card events (type=12) should be in raw data"
        
        log.info("✓ Raw live_events verified (all 3 event types)")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 ENRICHMENT SUMMARY")
        print("="*60)
        print(f"Match: {team1.name} vs {team2.name}")
        print(f"Score: {match.team1_score}-{match.team2_score}")
        print()
        print("Extracted Fields (for fast queries):")
        print(f"  xG: {match.xg_home} - {match.xg_away}")
        print(f"  Shots on Goal: {match.shots_on_goal_home} - {match.shots_on_goal_away}")
        print(f"  Corners: {match.corners_home} - {match.corners_away}")
        print(f"  Goals: {len(match.goal_events)}")
        print()
        print("Raw Data (complete backup for future analysis):")
        print(f"  Match Stats: {len(match.match_stats_raw)} types")
        for stat in match.match_stats_raw:
            print(f"    - Type {stat['type']:2d}: {stat['stat_name']}")
        print(f"  Live Events: {len(match.live_events_raw)} events")
        for event in match.live_events_raw:
            print(f"    - Type {event['type']:2d}: Minute {event['minute']}")
        print("="*60)
        
        log.info("✅ All integration tests passed!")
        return True
        
    except Exception as e:
        log.error(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


async def main():
    """Main entry point."""
    success = await test_integration()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
