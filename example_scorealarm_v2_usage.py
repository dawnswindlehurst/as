"""Example usage of ScorealarmClient V2 endpoints for Value Bets.

This demonstrates how to use the new V2 endpoints to analyze:
- Match statistics (xG, shots, player events)
- Player performance by competition
- Team form and trends

Use cases:
1. Player Props - Calculate player goal/assist rates per competition
2. Team Markets - Analyze BTTS, clean sheets, corners
3. Match Analysis - Compare xG, possession, shots
"""

import asyncio
from scrapers.superbet import ScorealarmClient


async def example_fixture_stats():
    """Example: Get detailed match statistics including xG and player events."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Fixture Statistics")
    print("="*60)
    
    async with ScorealarmClient() as client:
        # Get fixture stats for Atletico 4x0 Barcelona
        fixture_stats = await client.get_fixture_stats("12001839")
        
        if fixture_stats:
            print(f"\nFixture: {fixture_stats.fixture_id}")
            
            # Find Expected Goals (type 19)
            xg_stats = [s for s in fixture_stats.match_stats if s.type == 19]
            if xg_stats:
                xg = xg_stats[0]
                example_odds = 2.50
                implied_prob = (1 / example_odds) * 100
                print(f"\nExpected Goals (xG):")
                print(f"  Home: {xg.team1}")
                print(f"  Away: {xg.team2}")
                print(f"  Analysis: If home win odds @ {example_odds} ({implied_prob:.0f}% implied),")
                print(f"           and xG suggests 70% → VALUE BET!")
            
            # Find shots on goal (type 2)
            shots_stats = [s for s in fixture_stats.match_stats if s.type == 2]
            if shots_stats:
                shots = shots_stats[0]
                print(f"\nShots on Goal:")
                print(f"  Home: {shots.team1}")
                print(f"  Away: {shots.team2}")
            
            # Show all goals with scorers
            goals = [e for e in fixture_stats.live_events if e.type == 4]
            print(f"\nGoals ({len(goals)}):")
            for goal in goals:
                print(f"  {goal.minute}' - {goal.player_name}")
                if goal.secondary_player_name:
                    print(f"    Assist: {goal.secondary_player_name}")
                if goal.score:
                    print(f"    Score: {goal.score}")
        else:
            print("No fixture stats available")


async def example_player_stats():
    """Example: Calculate player goal rate for player props betting."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Player Stats Analysis")
    print("="*60)
    
    async with ScorealarmClient() as client:
        # Get stats for Julian Alvarez
        player = await client.get_player_stats("524Lwb9169FQbvfEIUGjrl")
        
        if player:
            print(f"\nPlayer: {player.player_name}")
            if player.team_name:
                print(f"Team: {player.team_name}")
            if player.position:
                print(f"Position: {player.position}")
            
            print(f"\nSeasonal Performance:")
            
            for season in player.seasonal_form:
                if season.matches_played > 0:
                    goals_per_game = season.goals / season.matches_played
                    assists_per_game = season.assists / season.matches_played
                    
                    print(f"\n  {season.competition_name} ({season.season_name}):")
                    print(f"    Matches: {season.matches_played}")
                    print(f"    Goals: {season.goals} ({goals_per_game:.2f} per game)")
                    print(f"    Assists: {season.assists} ({assists_per_game:.2f} per game)")
                    if season.rating:
                        print(f"    Rating: {season.rating}")
                    
                    # Value bet example
                    print(f"\n    💡 Value Bet Analysis:")
                    print(f"       If 'Anytime Goalscorer' odds @ 2.50 (40% implied)")
                    print(f"       But goals/game = {goals_per_game:.2f} suggests ~{goals_per_game*100:.0f}%")
                    if goals_per_game > 0.40:
                        print(f"       → VALUE! Real rate > implied odds")
                    else:
                        print(f"       → No value, skip this bet")
        else:
            print("No player stats available")


async def example_team_stats():
    """Example: Analyze team form for BTTS and clean sheet bets."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Team Stats for Market Analysis")
    print("="*60)
    
    async with ScorealarmClient() as client:
        # Get stats for Corinthians
        team = await client.get_team_stats("1FmdLfx4H9O2Ouk5Lbphws")
        
        if team:
            print(f"\nTeam: {team.team_name}")
            
            form = team.form_stats
            
            print(f"\nForm Statistics:")
            print(f"  Goals Scored/Game: {form.goals_scored_per_game}")
            print(f"  Goals Conceded/Game: {form.goals_conceded_per_game}")
            print(f"  BTTS Rate: {form.btts_rate}")
            print(f"  Clean Sheet Rate: {form.clean_sheet_rate}")
            print(f"  Corners/Game: {form.corners_per_game}")
            print(f"  Yellow Cards/Game: {form.yellows_per_game}")
            
            # Calculate BTTS value
            btts_parts = form.btts_rate.split('/')
            if len(btts_parts) == 2:
                try:
                    btts_yes_count = int(btts_parts[0])
                    btts_total = int(btts_parts[1])
                    
                    if btts_total > 0:
                        btts_yes_pct = (btts_yes_count / btts_total) * 100
                        btts_no_pct = 100 - btts_yes_pct
                        
                        btts_no_odds = 1.80
                        btts_no_implied = (1 / btts_no_odds) * 100
                        
                        print(f"\n💡 BTTS Market Analysis:")
                        print(f"   Historical BTTS Yes: {btts_yes_pct:.1f}%")
                        print(f"   Historical BTTS No: {btts_no_pct:.1f}%")
                        print(f"\n   If BTTS 'No' @ {btts_no_odds} → Implied prob: {btts_no_implied:.1f}%")
                        print(f"   Real rate: {btts_no_pct:.1f}%")
                        
                        if btts_no_pct > btts_no_implied:
                            edge = btts_no_pct - btts_no_implied
                            print(f"   → VALUE BET! Edge: +{edge:.1f}% 💰")
                        else:
                            print(f"   → No value")
                except (ValueError, ZeroDivisionError):
                    pass
            
            # Calculate clean sheet value
            cs_parts = form.clean_sheet_rate.split('/')
            if len(cs_parts) == 2:
                try:
                    cs_count = int(cs_parts[0])
                    cs_total = int(cs_parts[1])
                    
                    if cs_total > 0:
                        cs_pct = (cs_count / cs_total) * 100
                        
                        cs_odds = 3.00
                        cs_implied = (1 / cs_odds) * 100
                        
                        print(f"\n💡 Clean Sheet Market Analysis:")
                        print(f"   Historical Clean Sheet Rate: {cs_pct:.1f}%")
                        print(f"\n   If 'Team to Keep Clean Sheet' @ {cs_odds} → Implied: {cs_implied:.1f}%")
                        print(f"   Real rate: {cs_pct:.1f}%")
                        
                        if cs_pct > cs_implied:
                            edge = cs_pct - cs_implied
                            print(f"   → VALUE BET! Edge: +{edge:.1f}% 💰")
                        else:
                            print(f"   → No value")
                except (ValueError, ZeroDivisionError):
                    pass
            
            # Standings
            if team.standings:
                print(f"\nStandings:")
                for standing in team.standings:
                    print(f"  {standing.competition_name}: #{standing.position}")
            
            # Recent form
            if team.recent_matches:
                print(f"\nRecent matches: {len(team.recent_matches)} games tracked")
        else:
            print("No team stats available")


async def example_combined_analysis():
    """Example: Combine multiple data sources for comprehensive analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Combined Analysis")
    print("="*60)
    
    async with ScorealarmClient() as client:
        print("\nScenario: Player Props bet on 'Alvarez to score'")
        print("Combining player stats + team stats + recent fixtures\n")
        
        # Get player stats
        player = await client.get_player_stats("524Lwb9169FQbvfEIUGjrl")
        
        if player and player.seasonal_form:
            # Find current competition
            current_season = player.seasonal_form[0] if player.seasonal_form else None
            
            if current_season and current_season.matches_played > 0:
                goals_per_game = current_season.goals / current_season.matches_played
                
                print(f"Player: {player.player_name}")
                print(f"Competition: {current_season.competition_name}")
                print(f"Goals/Game: {goals_per_game:.2f}")
                
                # Calculate probability
                # Cap scoring probability at 99% since no bet is 100% certain
                MAX_SCORING_PROBABILITY = 0.99
                scoring_prob = min(goals_per_game, MAX_SCORING_PROBABILITY)
                
                print(f"\nEstimated scoring probability: {scoring_prob*100:.1f}%")
                
                # Compare with odds
                example_odds = 2.50
                implied_prob = 1 / example_odds * 100
                
                print(f"\nOdds Analysis:")
                print(f"  Odds: {example_odds}")
                print(f"  Implied Probability: {implied_prob:.1f}%")
                print(f"  Model Probability: {scoring_prob*100:.1f}%")
                
                if scoring_prob * 100 > implied_prob:
                    edge = (scoring_prob * 100) - implied_prob
                    print(f"\n  ✅ VALUE BET! Edge: +{edge:.1f}%")
                    
                    # Calculate expected value
                    ev = (scoring_prob * (example_odds - 1)) - ((1 - scoring_prob) * 1)
                    print(f"  Expected Value: {ev*100:+.1f}% ROI")
                else:
                    print(f"\n  ❌ No value - skip this bet")
        else:
            print("Insufficient data for analysis")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("SCOREALARM V2 ENDPOINTS - VALUE BETS EXAMPLES")
    print("="*60)
    
    await example_fixture_stats()
    await example_player_stats()
    await example_team_stats()
    await example_combined_analysis()
    
    print("\n" + "="*60)
    print("EXAMPLES COMPLETE")
    print("="*60)
    print("\nKey Takeaways:")
    print("1. Use get_fixture_stats() for xG and in-game analysis")
    print("2. Use get_player_stats() for player props (goals, assists)")
    print("3. Use get_team_stats() for BTTS, clean sheets, corners")
    print("4. Combine data sources for comprehensive edge detection")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
