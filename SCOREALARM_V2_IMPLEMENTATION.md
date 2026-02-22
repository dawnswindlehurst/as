# ScorealarmClient V2 API Implementation

## Overview

This implementation adds three new V2 endpoints to the ScorealarmClient for advanced value betting analysis. These endpoints provide detailed statistics for fixtures, players, and teams from the Scorealarm Stats API.

## New Endpoints

### 1. Fixture Statistics - `get_fixture_stats()`

```python
async def get_fixture_stats(self, fixture_id: str) -> Optional[FixtureStats]
```

**Endpoint:** `GET /v2/soccer/fixtures/overview/{platform}/{locale}`

**Parameters:**
- `fixture_id`: Match ID (e.g., "12001839" or "ax:match:12001839")

**Returns:** `FixtureStats` containing:
- `match_stats`: List of match statistics (xG, shots, corners, cards)
- `live_events`: List of live events (goals, assists, cards) with player IDs
- `statistics_by_period`: Stats broken down by period

**Example Usage:**
```python
async with ScorealarmClient() as client:
    stats = await client.get_fixture_stats("12001839")
    
    # Get Expected Goals
    xg = [s for s in stats.match_stats if s.type == 19][0]
    print(f"xG: {xg.team1} - {xg.team2}")
    
    # Get goals with scorers
    goals = [e for e in stats.live_events if e.type == 4]
    for goal in goals:
        print(f"{goal.minute}' - {goal.player_name}")
```

### 2. Player Statistics - `get_player_stats()`

```python
async def get_player_stats(self, player_id: str) -> Optional[PlayerStats]
```

**Endpoint:** `GET /v2/soccer/players/overview/{platform}/{locale}`

**Parameters:**
- `player_id`: Player ID string (e.g., "524Lwb9169FQbvfEIUGjrl")

**Returns:** `PlayerStats` containing:
- `player_name`: Player name
- `position`: Playing position
- `team_name`: Current team
- `seasonal_form`: List of stats by competition (goals, assists, rating)

**Example Usage:**
```python
async with ScorealarmClient() as client:
    player = await client.get_player_stats("524Lwb9169FQbvfEIUGjrl")
    
    for season in player.seasonal_form:
        goals_per_game = season.goals / season.matches_played
        print(f"{season.competition_name}: {goals_per_game:.2f} goals/game")
```

### 3. Team Statistics - `get_team_stats()`

```python
async def get_team_stats(self, team_id: str) -> Optional[TeamStats]
```

**Endpoint:** `GET /v2/soccer/teams/overview/{platform}/{locale}`

**Parameters:**
- `team_id`: Team ID string (e.g., "1FmdLfx4H9O2Ouk5Lbphws")

**Returns:** `TeamStats` containing:
- `team_name`: Team name
- `form_stats`: Form statistics (BTTS, clean sheets, goals/game)
- `standings`: League positions
- `recent_matches`: Recent match history

**Example Usage:**
```python
async with ScorealarmClient() as client:
    team = await client.get_team_stats("1FmdLfx4H9O2Ouk5Lbphws")
    
    print(f"BTTS Rate: {team.form_stats.btts_rate}")
    print(f"Clean Sheets: {team.form_stats.clean_sheet_rate}")
    print(f"Goals/Game: {team.form_stats.goals_scored_per_game}")
```

## Data Models

### MatchStat

Represents a single match statistic (xG, shots, etc).

```python
@dataclass
class MatchStat:
    type: int              # Statistic type (see mapping below)
    team1: str             # Value for team 1
    team2: str             # Value for team 2
    stat_name: str         # Human-readable name
```

**Type Mapping:**
- 1: Ball Possession
- 2: Shots on Goal
- 5: Corner Kicks
- 10: Fouls
- 11: Red Cards
- 12: Yellow Cards
- 18: Total Shots
- 19: Expected Goals (xG)
- 29: Big Chances Scored
- 30: Big Chances Missed

### LiveEvent

Represents a live event (goal, card, shot) with player tracking.

```python
@dataclass
class LiveEvent:
    type: int                          # Event type (4=goal, 1=yellow, etc)
    subtype: int                       # Event subtype (6=own goal, 8=assisted)
    side: int                          # 1=team1, 2=team2
    minute: int                        # Minute of event
    player_id: Optional[str]           # Player ID
    player_name: Optional[str]         # Player name
    secondary_player_id: Optional[str] # Assist provider ID
    secondary_player_name: Optional[str] # Assist provider name
    score: Optional[str]               # Score after event
```

### PlayerSeasonStats

Player statistics for a specific competition/season.

```python
@dataclass
class PlayerSeasonStats:
    competition_id: str
    competition_name: str
    season_name: str
    matches_played: int
    goals: int
    assists: int
    rating: Optional[float]
    rank: Optional[int]
```

### TeamFormStats

Team form statistics for betting analysis.

```python
@dataclass
class TeamFormStats:
    goals_scored_per_game: float
    goals_conceded_per_game: float
    btts_rate: str              # Format: "1/5"
    clean_sheet_rate: str       # Format: "3/5"
    corners_per_game: float
    yellows_per_game: float
```

## Value Betting Use Cases

### 1. Player Props - Anytime Goalscorer

```python
async with ScorealarmClient() as client:
    player = await client.get_player_stats(player_id)
    
    # Find current competition stats
    current = player.seasonal_form[0]
    goals_per_game = current.goals / current.matches_played
    
    # Compare with odds
    odds = 2.50
    implied_prob = (1 / odds) * 100  # 40%
    actual_prob = goals_per_game * 100
    
    if actual_prob > implied_prob:
        edge = actual_prob - implied_prob
        print(f"VALUE BET! Edge: +{edge:.1f}%")
```

### 2. Team Markets - Both Teams to Score

```python
async with ScorealarmClient() as client:
    team = await client.get_team_stats(team_id)
    
    # Parse BTTS rate
    btts_yes, btts_total = map(int, team.form_stats.btts_rate.split('/'))
    btts_no_pct = (1 - btts_yes/btts_total) * 100
    
    # Compare with odds
    odds = 1.80
    implied_prob = (1 / odds) * 100  # 55.6%
    
    if btts_no_pct > implied_prob:
        print("VALUE on BTTS No!")
```

### 3. Match Analysis - Expected Goals

```python
async with ScorealarmClient() as client:
    stats = await client.get_fixture_stats(fixture_id)
    
    # Get xG stats
    xg = [s for s in stats.match_stats if s.type == 19][0]
    home_xg = float(xg.team1)
    away_xg = float(xg.team2)
    
    # If home team xG is significantly higher than odds suggest,
    # there may be value in backing the home team
```

## Stat Type Mappings

### Match Stats Types
- 1: Ball Possession (%)
- 2: Shots on Goal
- 5: Corner Kicks
- 10: Fouls
- 11: Red Cards
- 12: Yellow Cards
- 18: Total Shots
- 19: Expected Goals (xG)

### Live Event Types
- 1: Yellow Card
- 4: Goal (subtype: 6=own goal, 8=assisted)
- 5: Shot on Goal
- 8: Blocked Shot
- 9: Shot Off Target

### Player Stats Types
- 1: Goals
- 2: Assists
- 3: Yellow Cards
- 5: Minutes Played
- 6: Shots on Target
- 7: Passes
- 8: Starting 11
- 14: Matches Played

### Team Stats Types
- 0: Corners per game
- 1: Yellow cards per game
- 2: Clean sheets
- 3: Goals scored per game
- 4: Goals conceded per game
- 5: Both teams to score (BTTS)

## Testing

Run the test suite:
```bash
python test_scorealarm_v2.py
```

See example usage:
```bash
python example_scorealarm_v2_usage.py
```

## Implementation Details

### Error Handling
- All methods return `Optional[T]` (can return None on errors)
- Network errors are logged but don't raise exceptions
- Invalid data is handled gracefully

### Auto-Prefixing
The `get_fixture_stats()` method automatically adds the "ax:match:" prefix if not provided:
```python
# Both work the same
stats = await client.get_fixture_stats("12001839")
stats = await client.get_fixture_stats("ax:match:12001839")
```

### Serialization
All dataclasses include `to_dict()` methods for JSON serialization:
```python
stats = await client.get_player_stats(player_id)
json_data = stats.to_dict()
```

## Files Modified

1. `scrapers/superbet/scorealarm_models.py` (+180 lines)
   - Added 8 new dataclasses for V2 API

2. `scrapers/superbet/scorealarm_client.py` (+382 lines)
   - Added 3 new async methods for V2 endpoints

3. `scrapers/superbet/__init__.py` (+16 lines)
   - Exported new models

4. `test_scorealarm_v2.py` (+396 lines)
   - Comprehensive test suite

5. `example_scorealarm_v2_usage.py` (+273 lines)
   - Detailed usage examples

**Total: 1,247 lines added**

## Security

- CodeQL scan: 0 alerts
- No hardcoded credentials
- Proper error handling
- Safe data parsing

## Performance

- Async/await throughout
- Reuses aiohttp session
- 30-second default timeout
- Minimal memory footprint

## Future Enhancements

Potential additions:
- Caching for frequently accessed data
- Rate limiting
- Batch operations
- Real-time WebSocket feeds
- Historical data aggregation
