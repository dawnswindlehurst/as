"""Example usage of ScorealarmClient and GameDiscoveryService.

This demonstrates the complete flow for discovering games across multiple sports.
"""

import asyncio
from scrapers.superbet import (
    SuperbetClient,
    ScorealarmClient,
    GameDiscoveryService,
    VALUABLE_SPORTS,
    SUPERBET_SPORTS,
)


async def example_get_all_sports():
    """Example: Get list of all available sports."""
    print("\n=== Example 1: Get All Sports ===")
    
    async with SuperbetClient() as client:
        sports = await client.get_sports()
        
        print(f"Found {len(sports)} sports:")
        for sport in sports[:10]:  # Show first 10
            print(f"  - {sport.id}: {sport.local_name}")


async def example_get_tournaments_for_sport():
    """Example: Get tournaments for a specific sport (Hockey)."""
    print("\n=== Example 2: Get Tournaments for Hockey ===")
    
    async with SuperbetClient() as client:
        tournaments = await client.get_tournaments_by_sport(sport_id=3)  # Hockey
        
        print(f"Found {len(tournaments)} tournaments for Hockey:")
        for tournament in tournaments[:5]:  # Show first 5
            print(f"  - {tournament.tournament_name} (ID: {tournament.tournament_id})")
            print(f"    Category: {tournament.category_name}")


async def example_get_tournament_details():
    """Example: Get detailed info about a tournament from Scorealarm."""
    print("\n=== Example 3: Get Tournament Details ===")
    
    async with ScorealarmClient() as client:
        # First, get a tournament ID from Superbet
        async with SuperbetClient() as superbet:
            tournaments = await superbet.get_tournaments_by_sport(sport_id=3)
            if not tournaments:
                print("No tournaments found")
                return
            
            tournament_id = tournaments[0].tournament_id
        
        # Get details from Scorealarm
        details = await client.get_tournament_details(tournament_id)
        
        if details:
            print(f"Tournament: {details.tournament_name}")
            print(f"Competition ID: {details.competition_id}")
            print(f"Seasons: {len(details.seasons)}")
            
            latest_season = details.get_latest_season()
            if latest_season:
                print(f"Latest Season: {latest_season.name}")


async def example_get_competition_matches():
    """Example: Get matches for a competition."""
    print("\n=== Example 4: Get Competition Matches ===")
    
    async with ScorealarmClient() as client:
        # These are example IDs - you'd get real ones from the tournament details
        season_id = 12345
        competition_id = 100
        
        matches = await client.get_competition_events(season_id, competition_id)
        
        print(f"Found {len(matches)} matches:")
        for match in matches[:3]:  # Show first 3
            print(f"\n  {match.team1.name} vs {match.team2.name}")
            print(f"  Date: {match.match_date}")
            print(f"  Competition: {match.competition.name}")
            
            # Show final score if available
            final_score = next((s for s in match.scores if s.type == 0), None)
            if final_score:
                print(f"  Score: {final_score.team1} - {final_score.team2}")


async def example_discover_games_for_sport():
    """Example: Discover all games for a specific sport (Bandy)."""
    print("\n=== Example 5: Discover Games for Bandy ===")
    
    service = GameDiscoveryService()
    
    # Discover games for Bandy (sport_id=7)
    # Limit to 3 tournaments for demonstration
    matches = await service.discover_games_by_sport(sport_id=7, limit=3)
    
    print(f"Found {len(matches)} matches for Bandy:")
    for match in matches[:5]:  # Show first 5
        print(f"\n  {match.team1.name} vs {match.team2.name}")
        print(f"  Date: {match.match_date}")
        print(f"  Season: {match.season.name}")
        print(f"  Competition: {match.competition.name}")


async def example_discover_all_valuable_sports():
    """Example: Discover games across all valuable sports."""
    print("\n=== Example 6: Discover Games Across All Valuable Sports ===")
    
    service = GameDiscoveryService()
    
    # Get list of valuable sports first
    valuable_sports = service.get_valuable_sports()
    print(f"Valuable sports: {', '.join(s['name'] for s in valuable_sports)}")
    
    # Discover games for all valuable sports
    # Limit to 1 tournament per sport for demonstration
    results = await service.discover_all_games(limit_per_sport=1)
    
    print(f"\nResults by sport:")
    for sport_name, matches in results.items():
        print(f"  - {sport_name}: {len(matches)} matches")


async def example_get_match_details():
    """Example: Get detailed match information including H2H."""
    print("\n=== Example 7: Get Match Details with H2H ===")
    
    async with ScorealarmClient() as client:
        # Example match ID - you'd get this from discover_games_by_sport
        match_id = 60192783
        
        match_detail = await client.get_event_detail(match_id)
        
        if match_detail:
            match = match_detail.match
            print(f"Match: {match.team1.name} vs {match.team2.name}")
            print(f"Date: {match.match_date}")
            print(f"Competition: {match.competition.name}")
            
            # H2H stats
            if match_detail.h2h_stats:
                print(f"\nH2H Stats available: {len(match_detail.h2h_stats)} keys")
            
            # Team form
            if match_detail.team1_form:
                print(f"Team 1 form: {len(match_detail.team1_form)} recent games")
            if match_detail.team2_form:
                print(f"Team 2 form: {len(match_detail.team2_form)} recent games")


async def example_complete_flow():
    """Example: Complete flow from sport to matches."""
    print("\n=== Example 8: Complete Flow - Sport to Matches ===")
    
    sport_id = 7  # Bandy
    sport_name = SUPERBET_SPORTS[sport_id]
    
    print(f"Discovering matches for {sport_name}...")
    
    async with SuperbetClient() as superbet:
        async with ScorealarmClient() as scorealarm:
            # Step 1: Get tournaments for the sport
            print("\n1. Getting tournaments...")
            tournaments = await superbet.get_tournaments_by_sport(sport_id)
            print(f"   Found {len(tournaments)} tournaments")
            
            if not tournaments:
                print("   No tournaments found")
                return
            
            # Step 2: Get details for first tournament
            print("\n2. Getting tournament details...")
            tournament = tournaments[0]
            details = await scorealarm.get_tournament_details(tournament.tournament_id)
            
            if not details:
                print("   No details found")
                return
            
            print(f"   Tournament: {details.tournament_name}")
            print(f"   Competition: {details.competition_name}")
            
            # Step 3: Get latest season
            print("\n3. Getting latest season...")
            season = details.get_latest_season()
            if not season:
                print("   No season found")
                return
            
            print(f"   Season: {season.name}")
            
            # Step 4: Get matches
            print("\n4. Getting matches...")
            matches = await scorealarm.get_competition_events(
                season_id=season.id,
                competition_id=details.competition_id
            )
            print(f"   Found {len(matches)} matches")
            
            # Step 5: Show sample matches
            if matches:
                print("\n5. Sample matches:")
                for match in matches[:3]:
                    print(f"\n   {match.team1.name} vs {match.team2.name}")
                    print(f"   Date: {match.match_date}")
                    
                    final_score = next((s for s in match.scores if s.type == 0), None)
                    if final_score:
                        print(f"   Score: {final_score.team1} - {final_score.team2}")


async def main():
    """Run all examples."""
    print("="*60)
    print("SCOREALARM CLIENT - USAGE EXAMPLES")
    print("="*60)
    
    examples = [
        example_get_all_sports,
        example_get_tournaments_for_sport,
        example_get_tournament_details,
        example_get_competition_matches,
        example_discover_games_for_sport,
        example_discover_all_valuable_sports,
        example_get_match_details,
        example_complete_flow,
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
