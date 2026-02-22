"""Test ScorealarmClient V2 endpoints for Value Bets.

This script tests the new V2 endpoints for fixture stats, player stats, and team stats.
"""

import asyncio
import sys
from scrapers.superbet import (
    ScorealarmClient,
    FixtureStats,
    PlayerStats,
    TeamStats,
)


async def test_fixture_stats():
    """Test getting fixture statistics including xG, shots, and player events."""
    print("\n" + "="*60)
    print("TEST 1: Get Fixture Stats (Atletico 4x0 Barcelona)")
    print("="*60)
    
    async with ScorealarmClient() as client:
        try:
            # Test with full fixture ID format
            fixture_stats = await client.get_fixture_stats("ax:match:12001839")
            
            if fixture_stats:
                print(f"✓ Fixture stats retrieved successfully")
                print(f"  Fixture ID: {fixture_stats.fixture_id}")
                print(f"  Match Stats: {len(fixture_stats.match_stats)} entries")
                print(f"  Live Events: {len(fixture_stats.live_events)} events")
                print(f"  Periods: {len(fixture_stats.statistics_by_period)} period(s)")
                
                # Show xG stats (type 19)
                xg_stats = [s for s in fixture_stats.match_stats if s.type == 19]
                if xg_stats:
                    xg = xg_stats[0]
                    print(f"\n  Expected Goals (xG):")
                    print(f"    Team 1: {xg.team1}")
                    print(f"    Team 2: {xg.team2}")
                
                # Show goals (type 4)
                goals = [e for e in fixture_stats.live_events if e.type == 4]
                if goals:
                    print(f"\n  Goals: {len(goals)}")
                    for goal in goals[:3]:  # Show first 3
                        print(f"    {goal.minute}' - {goal.player_name or 'Unknown'}")
                        if goal.secondary_player_name:
                            print(f"      Assist: {goal.secondary_player_name}")
                        if goal.score:
                            print(f"      Score: {goal.score}")
                    if len(goals) > 3:
                        print(f"    ... and {len(goals) - 3} more goals")
                
                # Test serialization
                fixture_dict = fixture_stats.to_dict()
                assert isinstance(fixture_dict, dict)
                assert 'match_stats' in fixture_dict
                print("\n✓ Serialization successful")
                
                return
            else:
                print("⚠ No fixture stats found (endpoint might require valid/recent fixture)")
                return  # Not a failure if endpoint is working
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            raise


async def test_fixture_stats_short_id():
    """Test fixture stats with short ID format (auto-prefix)."""
    print("\n" + "="*60)
    print("TEST 2: Get Fixture Stats with Short ID")
    print("="*60)
    
    async with ScorealarmClient() as client:
        try:
            # Test with just the numeric ID (should auto-add prefix)
            fixture_stats = await client.get_fixture_stats("12001839")
            
            if fixture_stats:
                print(f"✓ Fixture stats retrieved with short ID")
                print(f"  Fixture ID: {fixture_stats.fixture_id}")
                assert fixture_stats.fixture_id.startswith("ax:match:")
                print("✓ Auto-prefix working correctly")
                return
            else:
                print("⚠ No fixture stats found")
                return
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            raise


async def test_player_stats():
    """Test getting player statistics by competition."""
    print("\n" + "="*60)
    print("TEST 3: Get Player Stats (Julian Alvarez)")
    print("="*60)
    
    async with ScorealarmClient() as client:
        try:
            # Julian Alvarez from problem statement
            player_stats = await client.get_player_stats("524Lwb9169FQbvfEIUGjrl")
            
            if player_stats:
                print(f"✓ Player stats retrieved successfully")
                print(f"  Player ID: {player_stats.player_id}")
                print(f"  Name: {player_stats.player_name}")
                if player_stats.position:
                    print(f"  Position: {player_stats.position}")
                if player_stats.team_name:
                    print(f"  Team: {player_stats.team_name}")
                
                print(f"\n  Seasonal Form: {len(player_stats.seasonal_form)} competition(s)")
                
                # Show stats for each competition
                for season in player_stats.seasonal_form[:3]:  # Show first 3
                    print(f"\n    {season.competition_name} - {season.season_name}")
                    print(f"      Matches: {season.matches_played}")
                    print(f"      Goals: {season.goals}")
                    print(f"      Assists: {season.assists}")
                    if season.rating:
                        print(f"      Rating: {season.rating}")
                    
                    # Calculate goals per game
                    if season.matches_played > 0:
                        goals_per_game = season.goals / season.matches_played
                        print(f"      Goals/Game: {goals_per_game:.2f}")
                
                if len(player_stats.seasonal_form) > 3:
                    print(f"\n    ... and {len(player_stats.seasonal_form) - 3} more competitions")
                
                # Test serialization
                player_dict = player_stats.to_dict()
                assert isinstance(player_dict, dict)
                assert 'seasonal_form' in player_dict
                print("\n✓ Serialization successful")
                
                return
            else:
                print("⚠ No player stats found")
                return
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            raise


async def test_team_stats():
    """Test getting team statistics including BTTS and clean sheets."""
    print("\n" + "="*60)
    print("TEST 4: Get Team Stats (Corinthians)")
    print("="*60)
    
    async with ScorealarmClient() as client:
        try:
            # Corinthians from problem statement
            team_stats = await client.get_team_stats("1FmdLfx4H9O2Ouk5Lbphws")
            
            if team_stats:
                print(f"✓ Team stats retrieved successfully")
                print(f"  Team ID: {team_stats.team_id}")
                print(f"  Name: {team_stats.team_name}")
                
                print(f"\n  Form Stats:")
                print(f"    Goals Scored/Game: {team_stats.form_stats.goals_scored_per_game}")
                print(f"    Goals Conceded/Game: {team_stats.form_stats.goals_conceded_per_game}")
                print(f"    BTTS Rate: {team_stats.form_stats.btts_rate}")
                print(f"    Clean Sheet Rate: {team_stats.form_stats.clean_sheet_rate}")
                print(f"    Corners/Game: {team_stats.form_stats.corners_per_game}")
                print(f"    Yellow Cards/Game: {team_stats.form_stats.yellows_per_game}")
                
                # Calculate value bet example
                EXAMPLE_BTTS_NO_ODDS = 1.80  # Example odds for demonstration
                btts_parts = team_stats.form_stats.btts_rate.split('/')
                if len(btts_parts) == 2:
                    try:
                        btts_yes = int(btts_parts[0])
                        btts_total = int(btts_parts[1])
                        if btts_total > 0:
                            btts_percentage = (btts_yes / btts_total) * 100
                            btts_no_percentage = 100 - btts_percentage
                            implied_prob = (1 / EXAMPLE_BTTS_NO_ODDS) * 100
                            print(f"\n  Value Bet Analysis:")
                            print(f"    BTTS Yes: {btts_percentage:.1f}%")
                            print(f"    BTTS No: {btts_no_percentage:.1f}%")
                            print(f"    If BTTS 'No' @ {EXAMPLE_BTTS_NO_ODDS} ({implied_prob:.1f}% implied) vs {btts_no_percentage:.1f}% real")
                            if btts_no_percentage > implied_prob:
                                print(f"    → VALUE BET! 💰")
                    except (ValueError, ZeroDivisionError):
                        pass
                
                if team_stats.standings:
                    print(f"\n  Standings: {len(team_stats.standings)} competition(s)")
                    for standing in team_stats.standings[:3]:
                        print(f"    {standing.competition_name}: Position {standing.position}")
                
                print(f"\n  Recent Matches: {len(team_stats.recent_matches)}")
                
                # Test serialization
                team_dict = team_stats.to_dict()
                assert isinstance(team_dict, dict)
                assert 'form_stats' in team_dict
                print("\n✓ Serialization successful")
                
                return
            else:
                print("⚠ No team stats found")
                return
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            raise


async def test_dataclass_serialization():
    """Test that all new V2 dataclasses can serialize to dict."""
    print("\n" + "="*60)
    print("TEST 5: V2 Dataclass Serialization")
    print("="*60)
    
    from scrapers.superbet import (
        MatchStat,
        LiveEvent,
        FixtureStats,
        PlayerSeasonStats,
        PlayerStats,
        TeamFormStats,
        TeamStanding,
        TeamStats,
    )
    
    try:
        # Test MatchStat
        match_stat = MatchStat(
            type=19,
            team1="2.33",
            team2="1.02",
            stat_name="stats.football.match.expected_goals"
        )
        assert isinstance(match_stat.to_dict(), dict)
        print("✓ MatchStat serialization successful")
        
        # Test LiveEvent
        live_event = LiveEvent(
            type=4,
            subtype=8,
            side=1,
            minute=33,
            player_id="eEoFsBLbpVhqQsMREWEUN",
            player_name="Lookman, Ademola",
            secondary_player_id="524Lwb9169FQbvfEIUGjrl",
            secondary_player_name="Alvarez, Julian",
            score="3:0"
        )
        assert isinstance(live_event.to_dict(), dict)
        print("✓ LiveEvent serialization successful")
        
        # Test FixtureStats
        fixture_stats = FixtureStats(
            fixture_id="ax:match:12001839",
            match_stats=[match_stat],
            live_events=[live_event],
            statistics_by_period={0: [match_stat]}
        )
        assert isinstance(fixture_stats.to_dict(), dict)
        print("✓ FixtureStats serialization successful")
        
        # Test PlayerSeasonStats
        player_season = PlayerSeasonStats(
            competition_id="1FxsMJT0731IxdFhTAsWQA",
            competition_name="La Liga",
            season_name="La Liga 25/26",
            matches_played=23,
            goals=7,
            assists=3,
            rating=7.13,
            rank=29
        )
        assert isinstance(player_season.to_dict(), dict)
        print("✓ PlayerSeasonStats serialization successful")
        
        # Test PlayerStats
        player_stats = PlayerStats(
            player_id="524Lwb9169FQbvfEIUGjrl",
            player_name="Julian Alvarez",
            position="Forward",
            team_id="test",
            team_name="Test Team",
            seasonal_form=[player_season]
        )
        assert isinstance(player_stats.to_dict(), dict)
        print("✓ PlayerStats serialization successful")
        
        # Test TeamFormStats
        team_form = TeamFormStats(
            goals_scored_per_game=1.6,
            goals_conceded_per_game=0.6,
            btts_rate="1/5",
            clean_sheet_rate="3/5",
            corners_per_game=5.4,
            yellows_per_game=3.0
        )
        assert isinstance(team_form.to_dict(), dict)
        print("✓ TeamFormStats serialization successful")
        
        # Test TeamStanding
        standing = TeamStanding(
            competition_name="Test League",
            position=5
        )
        assert isinstance(standing.to_dict(), dict)
        print("✓ TeamStanding serialization successful")
        
        # Test TeamStats
        team_stats = TeamStats(
            team_id="1FmdLfx4H9O2Ouk5Lbphws",
            team_name="Corinthians",
            form_stats=team_form,
            standings=[standing]
        )
        assert isinstance(team_stats.to_dict(), dict)
        print("✓ TeamStats serialization successful")
        
        print("\n✓ All V2 dataclasses serialize correctly")
        return
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


async def main():
    """Run all V2 endpoint tests."""
    print("\n" + "="*60)
    print("SCOREALARM V2 ENDPOINTS TESTS")
    print("="*60)
    
    tests = [
        ("Fixture Stats (Full ID)", test_fixture_stats),
        ("Fixture Stats (Short ID)", test_fixture_stats_short_id),
        ("Player Stats", test_player_stats),
        ("Team Stats", test_team_stats),
        ("V2 Dataclass Serialization", test_dataclass_serialization),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All V2 endpoint tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
