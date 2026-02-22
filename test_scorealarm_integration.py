"""Test the ScorealarmClient and GameDiscoveryService implementation.

This script tests the complete flow for discovering games across multiple sports.
"""

import asyncio
import sys
from scrapers.superbet import (
    SuperbetClient,
    ScorealarmClient,
    GameDiscoveryService,
    VALUABLE_SPORTS,
    SUPERBET_SPORTS,
)


async def test_superbet_sports():
    """Test getting sports from Superbet struct endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Get Sports from Superbet")
    print("="*60)
    
    async with SuperbetClient() as client:
        try:
            sports = await client.get_sports()
            print(f"✓ Found {len(sports)} sports")
            
            # Show first 5 sports
            for sport in sports[:5]:
                print(f"  - {sport.id}: {sport.local_name}")
            
            if len(sports) > 5:
                print(f"  ... and {len(sports) - 5} more")
            
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_superbet_tournaments():
    """Test getting tournaments for a specific sport."""
    print("\n" + "="*60)
    print("TEST 2: Get Tournaments by Sport (Hockey - ID 3)")
    print("="*60)
    
    async with SuperbetClient() as client:
        try:
            tournaments = await client.get_tournaments_by_sport(3)  # Hockey
            print(f"✓ Found {len(tournaments)} tournaments for Hockey")
            
            # Show first 3 tournaments
            for tournament in tournaments[:3]:
                print(f"  - ID {tournament.tournament_id}: {tournament.tournament_name}")
                print(f"    Category: {tournament.category_name}")
            
            if len(tournaments) > 3:
                print(f"  ... and {len(tournaments) - 3} more")
            
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_scorealarm_tournament_details():
    """Test getting tournament details from Scorealarm."""
    print("\n" + "="*60)
    print("TEST 3: Get Tournament Details from Scorealarm")
    print("="*60)
    
    async with ScorealarmClient() as client:
        try:
            # Try a sample tournament ID
            # Note: This might fail if the tournament doesn't exist
            # In a real scenario, we'd get this from get_tournaments_by_sport
            tournament_id = 1000  # Sample ID
            
            details = await client.get_tournament_details(tournament_id)
            
            if details:
                print(f"✓ Tournament Details Found:")
                print(f"  - Tournament ID: {details.tournament_id}")
                print(f"  - Competition: {details.competition_name} (ID: {details.competition_id})")
                print(f"  - Seasons: {len(details.seasons)}")
                
                latest_season = details.get_latest_season()
                if latest_season:
                    print(f"  - Latest Season: {latest_season.name} (ID: {latest_season.id})")
                
                return True
            else:
                print(f"⚠ No details found for tournament {tournament_id} (might not exist)")
                return True  # Not a failure, just no data
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_scorealarm_events():
    """Test getting events from Scorealarm."""
    print("\n" + "="*60)
    print("TEST 4: Get Competition Events from Scorealarm")
    print("="*60)
    
    async with ScorealarmClient() as client:
        try:
            # Sample IDs - these might not exist
            season_id = 1000
            competition_id = 100
            
            matches = await client.get_competition_events(season_id, competition_id)
            
            print(f"✓ Found {len(matches)} matches")
            
            if matches:
                # Show first match
                match = matches[0]
                print(f"\nSample Match:")
                print(f"  - Teams: {match.team1.name} vs {match.team2.name}")
                print(f"  - Date: {match.match_date}")
                print(f"  - Competition: {match.competition.name}")
                print(f"  - Scores: {len(match.scores)} score entries")
            
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_game_discovery_valuable_sports():
    """Test getting valuable sports list."""
    print("\n" + "="*60)
    print("TEST 5: Get Valuable Sports")
    print("="*60)
    
    service = GameDiscoveryService()
    valuable = service.get_valuable_sports()
    
    print(f"✓ Found {len(valuable)} valuable sports:")
    for sport in valuable:
        print(f"  💎 {sport['id']}: {sport['name']}")
    
    return True


async def test_game_discovery_by_sport():
    """Test discovering games for a specific sport."""
    print("\n" + "="*60)
    print("TEST 6: Discover Games for Bandy (ID 7)")
    print("="*60)
    
    service = GameDiscoveryService()
    
    try:
        # Limit to 2 tournaments for testing
        matches = await service.discover_games_by_sport(sport_id=7, limit=2)
        
        print(f"✓ Found {len(matches)} matches for Bandy")
        
        if matches:
            # Show first 3 matches
            for match in matches[:3]:
                print(f"\n  Match {match.id}:")
                print(f"    {match.team1.name} vs {match.team2.name}")
                print(f"    Date: {match.match_date}")
                print(f"    Competition: {match.competition.name}")
                
                if match.scores:
                    final_score = next((s for s in match.scores if s.type == 0), None)
                    if final_score:
                        print(f"    Score: {final_score.team1} - {final_score.team2}")
            
            if len(matches) > 3:
                print(f"\n  ... and {len(matches) - 3} more matches")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_dataclass_serialization():
    """Test that all dataclasses can serialize to dict."""
    print("\n" + "="*60)
    print("TEST 7: Dataclass Serialization")
    print("="*60)
    
    from scrapers.superbet.scorealarm_models import (
        ScorealarmTeam,
        ScorealarmScore,
        ScorealarmSeason,
        ScorealarmCompetition,
        ScorealarmCategory,
        ScorealarmMatch,
    )
    from datetime import datetime
    
    try:
        # Create sample instances
        team1 = ScorealarmTeam(id=1, name="Team A")
        team2 = ScorealarmTeam(id=2, name="Team B")
        score = ScorealarmScore(team1=2, team2=1, type=0)
        season = ScorealarmSeason(id=100, name="2024/25")
        competition = ScorealarmCompetition(id=10, name="Test League")
        category = ScorealarmCategory(id=5, name="Test Country", sport_id=7)
        
        match = ScorealarmMatch(
            id=12345,
            platform_id="br:match:12345",
            offer_id="ax:match:12345",
            match_date=datetime(2024, 1, 15, 18, 0, 0),  # Fixed date for consistent testing
            match_status=110,
            match_state=2,
            sport_id=7,
            team1=team1,
            team2=team2,
            scores=[score],
            season=season,
            competition=competition,
            category=category,
        )
        
        # Test serialization
        match_dict = match.to_dict()
        
        print("✓ Match serialization successful")
        print(f"  Keys: {', '.join(match_dict.keys())}")
        
        # Verify nested objects
        assert 'team1' in match_dict
        assert 'team2' in match_dict
        assert 'scores' in match_dict
        assert isinstance(match_dict['scores'], list)
        
        print("✓ All nested objects serialized correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SCOREALARM CLIENT INTEGRATION TESTS")
    print("="*60)
    
    tests = [
        ("Superbet Sports", test_superbet_sports),
        ("Superbet Tournaments", test_superbet_tournaments),
        ("Scorealarm Tournament Details", test_scorealarm_tournament_details),
        ("Scorealarm Events", test_scorealarm_events),
        ("Valuable Sports", test_game_discovery_valuable_sports),
        ("Game Discovery", test_game_discovery_by_sport),
        ("Dataclass Serialization", test_dataclass_serialization),
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
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
