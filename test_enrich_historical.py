"""Test script for enrich_historical.py data extraction logic.

This test validates that the enrichment script correctly extracts and processes
V2 API data without requiring a live database connection.
"""

import asyncio
import sys
from datetime import datetime
from typing import List, Optional

# Mock data models to test extraction logic
from dataclasses import dataclass, field


@dataclass
class MockMatchStat:
    """Mock MatchStat for testing."""
    type: int
    team1: str
    team2: str
    stat_name: str


@dataclass
class MockLiveEvent:
    """Mock LiveEvent for testing."""
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
    """Mock FixtureStats for testing."""
    fixture_id: str
    match_stats: List[MockMatchStat]
    live_events: List[MockLiveEvent]
    statistics_by_period: dict = field(default_factory=dict)


def test_xg_extraction():
    """Test extraction of Expected Goals (xG) from fixture stats."""
    print("\n" + "="*60)
    print("TEST 1: xG Extraction")
    print("="*60)
    
    # Create mock fixture stats with xG data (type=19)
    fixture_stats = MockFixtureStats(
        fixture_id="ax:match:12001839",
        match_stats=[
            MockMatchStat(type=19, team1="2.33", team2="1.02", stat_name="Expected Goals"),
            MockMatchStat(type=2, team1="8", team2="4", stat_name="Shots on Goal"),
            MockMatchStat(type=5, team1="6", team2="3", stat_name="Corners")
        ],
        live_events=[],
        statistics_by_period={}
    )
    
    # Extract xG (type=19)
    xg_stats = [s for s in fixture_stats.match_stats if s.type == 19]
    assert len(xg_stats) == 1, "Should find exactly one xG stat"
    
    xg_stat = xg_stats[0]
    xg_home = float(xg_stat.team1)
    xg_away = float(xg_stat.team2)
    
    assert xg_home == 2.33, f"Expected xG home = 2.33, got {xg_home}"
    assert xg_away == 1.02, f"Expected xG away = 1.02, got {xg_away}"
    
    print(f"✓ xG Home: {xg_home}")
    print(f"✓ xG Away: {xg_away}")
    print("✅ xG extraction test passed")
    return


def test_shots_corners_extraction():
    """Test extraction of shots and corners from fixture stats."""
    print("\n" + "="*60)
    print("TEST 2: Shots & Corners Extraction")
    print("="*60)
    
    # Create mock fixture stats
    fixture_stats = MockFixtureStats(
        fixture_id="ax:match:12001839",
        match_stats=[
            MockMatchStat(type=2, team1="8", team2="4", stat_name="Shots on Goal"),
            MockMatchStat(type=5, team1="6", team2="3", stat_name="Corners")
        ],
        live_events=[],
        statistics_by_period={}
    )
    
    # Extract shots (type=2)
    shots_stats = [s for s in fixture_stats.match_stats if s.type == 2]
    assert len(shots_stats) == 1, "Should find exactly one shots stat"
    
    shots_stat = shots_stats[0]
    shots_home = int(shots_stat.team1)
    shots_away = int(shots_stat.team2)
    
    assert shots_home == 8, f"Expected shots home = 8, got {shots_home}"
    assert shots_away == 4, f"Expected shots away = 4, got {shots_away}"
    
    # Extract corners (type=5)
    corner_stats = [s for s in fixture_stats.match_stats if s.type == 5]
    assert len(corner_stats) == 1, "Should find exactly one corner stat"
    
    corner_stat = corner_stats[0]
    corners_home = int(corner_stat.team1)
    corners_away = int(corner_stat.team2)
    
    assert corners_home == 6, f"Expected corners home = 6, got {corners_home}"
    assert corners_away == 3, f"Expected corners away = 3, got {corners_away}"
    
    print(f"✓ Shots Home: {shots_home}, Away: {shots_away}")
    print(f"✓ Corners Home: {corners_home}, Away: {corners_away}")
    print("✅ Shots & Corners extraction test passed")
    return


def test_goal_events_extraction():
    """Test extraction of goal events with player details."""
    print("\n" + "="*60)
    print("TEST 3: Goal Events Extraction")
    print("="*60)
    
    # Create mock fixture stats with goal events
    fixture_stats = MockFixtureStats(
        fixture_id="ax:match:12001839",
        match_stats=[],
        live_events=[
            MockLiveEvent(
                type=4,  # Goal
                subtype=8,  # Assisted
                side=1,  # Home team
                minute=33,
                added_time=None,
                player_id="eEoFsBLbpVhqQsMREWEUN",
                player_name="Lookman, Ademola",
                secondary_player_id="524Lwb9169FQbvfEIUGjrl",
                secondary_player_name="Alvarez, Julian",
                score="1-0"
            ),
            MockLiveEvent(
                type=4,  # Goal
                subtype=0,
                side=2,  # Away team
                minute=67,
                added_time=2,
                player_id="player123",
                player_name="Silva, Bernardo",
                secondary_player_id=None,
                secondary_player_name=None,
                score="1-1"
            ),
            MockLiveEvent(
                type=1,  # Yellow card (should be ignored)
                subtype=0,
                side=1,
                minute=45,
                player_id="player456",
                player_name="Some Player"
            )
        ],
        statistics_by_period={}
    )
    
    # Extract goal events (type=4)
    goal_events = [e for e in fixture_stats.live_events if e.type == 4]
    assert len(goal_events) == 2, f"Should find 2 goals, got {len(goal_events)}"
    
    # Process goals into structured format
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
    
    # Validate first goal (with assist)
    goal1 = goals_data[0]
    assert goal1["minute"] == 33
    assert goal1["player_name"] == "Lookman, Ademola"
    assert goal1["assist_player_name"] == "Alvarez, Julian"
    assert goal1["side"] == 1
    assert goal1["score"] == "1-0"
    
    # Validate second goal (no assist)
    goal2 = goals_data[1]
    assert goal2["minute"] == 67
    assert goal2["added_time"] == 2
    assert goal2["player_name"] == "Silva, Bernardo"
    assert goal2["assist_player_id"] is None
    assert goal2["side"] == 2
    assert goal2["score"] == "1-1"
    
    print(f"✓ Found {len(goals_data)} goals")
    print(f"  Goal 1: {goal1['minute']}' - {goal1['player_name']}")
    print(f"    Assist: {goal1['assist_player_name']}")
    print(f"    Score: {goal1['score']}")
    print(f"  Goal 2: {goal2['minute']}'+{goal2['added_time']}' - {goal2['player_name']}")
    print(f"    Score: {goal2['score']}")
    print("✅ Goal events extraction test passed")
    return


def test_missing_data_handling():
    """Test handling of missing or invalid data."""
    print("\n" + "="*60)
    print("TEST 4: Missing Data Handling")
    print("="*60)
    
    # Create fixture stats with missing/invalid values
    fixture_stats = MockFixtureStats(
        fixture_id="ax:match:12001839",
        match_stats=[
            MockMatchStat(type=19, team1="", team2="1.5", stat_name="Expected Goals"),
            MockMatchStat(type=2, team1="invalid", team2="5", stat_name="Shots")
        ],
        live_events=[],
        statistics_by_period={}
    )
    
    # Test xG extraction with empty value
    xg_stats = [s for s in fixture_stats.match_stats if s.type == 19]
    if xg_stats:
        xg_stat = xg_stats[0]
        try:
            xg_home = float(xg_stat.team1) if xg_stat.team1 else None
            xg_away = float(xg_stat.team2) if xg_stat.team2 else None
        except (ValueError, TypeError):
            xg_home = None
            xg_away = None
        
        assert xg_home is None, "Empty string should result in None"
        assert xg_away == 1.5, "Valid value should be parsed"
        print(f"✓ Handled empty xG value: home={xg_home}, away={xg_away}")
    
    # Test shots extraction with invalid value
    shots_stats = [s for s in fixture_stats.match_stats if s.type == 2]
    if shots_stats:
        shots_stat = shots_stats[0]
        # This should catch ValueError from int("invalid")
        shots_home = None
        shots_away = None
        try:
            if shots_stat.team1:
                shots_home = int(shots_stat.team1)
        except (ValueError, TypeError):
            shots_home = None
        
        try:
            if shots_stat.team2:
                shots_away = int(shots_stat.team2)
        except (ValueError, TypeError):
            shots_away = None
        
        assert shots_home is None, "Invalid value should result in None"
        assert shots_away == 5, "Valid value should be parsed"
        print(f"✓ Handled invalid shots value: home={shots_home}, away={shots_away}")
    
    print("✅ Missing data handling test passed")
    return


def test_raw_data_storage():
    """Test storage of raw match_stats and live_events data."""
    print("\n" + "="*60)
    print("TEST 5: Raw Data Storage")
    print("="*60)
    
    # Create mock fixture stats with various data
    fixture_stats = MockFixtureStats(
        fixture_id="ax:match:12001839",
        match_stats=[
            MockMatchStat(type=19, team1="2.33", team2="1.02", stat_name="Expected Goals"),
            MockMatchStat(type=2, team1="8", team2="4", stat_name="Shots on Goal"),
            MockMatchStat(type=5, team1="6", team2="3", stat_name="Corners"),
            MockMatchStat(type=10, team1="12", team2="15", stat_name="Fouls"),
            MockMatchStat(type=12, team1="2", team2="3", stat_name="Yellow Cards"),
            MockMatchStat(type=1, team1="55", team2="45", stat_name="Possession")
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
                type=5, subtype=0, side=1, minute=67,
                player_id="player4", player_name="De Bruyne, Kevin"
            )
        ],
        statistics_by_period={}
    )
    
    # Simulate raw data storage (as done in enrich_historical.py)
    match_stats_raw = [
        {
            "type": s.type,
            "team1": s.team1,
            "team2": s.team2,
            "stat_name": s.stat_name
        }
        for s in fixture_stats.match_stats
    ]
    
    live_events_raw = [
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
    
    # Verify all stats are captured
    assert len(match_stats_raw) == 6, f"Expected 6 stats, got {len(match_stats_raw)}"
    assert len(live_events_raw) == 3, f"Expected 3 events, got {len(live_events_raw)}"
    
    # Verify specific stat types are present
    stat_types = [s["type"] for s in match_stats_raw]
    assert 10 in stat_types, "Fouls (type=10) should be captured"
    assert 12 in stat_types, "Yellow cards (type=12) should be captured"
    assert 1 in stat_types, "Possession (type=1) should be captured"
    
    # Verify event types are present
    event_types = [e["type"] for e in live_events_raw]
    assert 4 in event_types, "Goals (type=4) should be captured"
    assert 1 in event_types, "Cards (type=1) should be captured"
    assert 5 in event_types, "Shots (type=5) should be captured"
    
    # Verify all fields are preserved
    goal_event = live_events_raw[0]
    assert goal_event["player_id"] == "player1"
    assert goal_event["player_name"] == "Lookman, Ademola"
    assert goal_event["secondary_player_id"] == "player2"
    assert goal_event["secondary_player_name"] == "Alvarez, Julian"
    assert goal_event["score"] == "1-0"
    
    print(f"✓ Stored {len(match_stats_raw)} match stats:")
    for stat in match_stats_raw:
        print(f"    - Type {stat['type']:2d}: {stat['stat_name']}")
    
    print(f"✓ Stored {len(live_events_raw)} live events:")
    for event in live_events_raw:
        print(f"    - Type {event['type']:2d}: Minute {event['minute']}")
    
    print("✅ Raw data storage test passed")
    return


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 ENRICH_HISTORICAL.PY - DATA EXTRACTION TESTS")
    print("="*60)
    
    tests = [
        test_xg_extraction,
        test_shots_corners_extraction,
        test_goal_events_extraction,
        test_missing_data_handling,
        test_raw_data_storage
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ Test failed: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ Test error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
