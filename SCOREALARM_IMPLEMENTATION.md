# ScorealarmClient Multi-Sport Implementation

This document describes the implementation of the ScorealarmClient system for discovering and analyzing games across 50+ sports using Superbet and Scorealarm APIs.

## Overview

The implementation provides a complete flow for discovering sporting events across multiple sports, with focus on "valuable" sports that are less analyzed and offer better betting opportunities.

## Components

### 1. ScorealarmClient (`scrapers/superbet/scorealarm_client.py`)

An async REST client for the Scorealarm Stats API.

**Base URL**: `https://scorealarm-stats.freetls.fastly.net`

**Main Methods**:

- `get_tournament_details(tournament_id: int)` - Get competition and season IDs for a tournament
- `get_competition_events(season_id: int, competition_id: int)` - Get matches for a competition
- `get_event_detail(match_id: int)` - Get detailed match info including H2H and form

**Usage**:
```python
async with ScorealarmClient() as client:
    details = await client.get_tournament_details(tournament_id=1234)
    season = details.get_latest_season()
    matches = await client.get_competition_events(
        season_id=season.id,
        competition_id=details.competition_id
    )
```

### 2. Updated SuperbetClient (`scrapers/superbet/superbet_client.py`)

Enhanced with new endpoints for the multi-sport discovery flow.

**New Methods**:

- `get_sports()` - Get list of all available sports from `/struct` endpoint
- `get_tournaments_by_sport(sport_id: int)` - Get tournaments for a specific sport

**Usage**:
```python
async with SuperbetClient() as client:
    sports = await client.get_sports()
    tournaments = await client.get_tournaments_by_sport(sport_id=7)  # Bandy
```

### 3. GameDiscoveryService (`scrapers/superbet/game_discovery_service.py`)

High-level service for discovering games across multiple sports.

**Main Methods**:

- `discover_games_by_sport(sport_id: int, limit: Optional[int])` - Discover games for a specific sport
- `discover_all_games(sport_ids: Optional[List[int]], limit_per_sport: Optional[int])` - Discover games across multiple sports
- `get_valuable_sports()` - Get list of "gold" sports with high opportunity
- `get_all_sports()` - Get list of all supported sports

**Usage**:
```python
service = GameDiscoveryService()

# Discover games for Bandy
matches = await service.discover_games_by_sport(sport_id=7, limit=3)

# Discover across all valuable sports
results = await service.discover_all_games(limit_per_sport=2)
```

### 4. Data Models (`scrapers/superbet/scorealarm_models.py`)

All data models use Python dataclasses with `to_dict()` serialization methods, following the existing pattern in the codebase.

**Main Models**:

- `ScorealarmSport` - Sport information
- `ScorealarmTournament` - Tournament/league information
- `ScorealarmTournamentDetails` - Detailed tournament with seasons
- `ScorealarmMatch` - Match/event with scores and teams
- `ScorealarmMatchDetail` - Detailed match with H2H and form
- `ScorealarmTeam`, `ScorealarmScore`, `ScorealarmSeason`, `ScorealarmCompetition`, `ScorealarmCategory` - Supporting models

## API Flow

The complete flow for discovering games:

```
1. Get Sports
   GET /struct
   → Returns list of available sports

2. Get Tournaments for Sport
   GET /sport/{sport_id}/tournaments
   → Returns tournaments/leagues for the sport

3. Get Tournament Details (Scorealarm)
   GET /competition/details/tournaments/brsuperbetsport/pt-BR?tournament_id=ax:tournament:{id}
   → Returns competition_id and seasons

4. Get Competition Events
   GET /competition/events/brsuperbetsport/pt-BR?season_id=br:season:{id}&competition_id=br:competition:{id}
   → Returns matches with scores, teams, dates

5. Get Event Details (optional)
   GET /event/detail/brsuperbetsport/pt-BR?id=br:match:{id}
   → Returns H2H stats, team form, additional stats
```

## Supported Sports

### All Sports (50+)

The system supports all sports available in Superbet. See `SUPERBET_SPORTS` constant in `game_discovery_service.py` for the complete list.

### Valuable Sports ("Gold" Opportunities)

These sports are less analyzed and offer better opportunities:

- **Bandy** (ID: 7) - Ice hockey on a soccer field
- **Floorball** (ID: 9) - Indoor hockey variant
- **Polo aquático** (ID: 15) - Water polo
- **Curling** (ID: 22) - Ice sport
- **Hóquei sobre a grama** (ID: 29) - Field hockey
- **Rink Hockey** (ID: 71) - Roller hockey
- **Lacrosse** (ID: 81) - Team sport

## Examples

See `example_scorealarm_usage.py` for complete usage examples including:

1. Get all sports
2. Get tournaments for a sport
3. Get tournament details
4. Get competition matches
5. Discover games for a sport
6. Discover across all valuable sports
7. Get match details with H2H
8. Complete flow from sport to matches

## Testing

Run the integration tests:

```bash
python test_scorealarm_integration.py
```

Tests include:
- Superbet sports endpoint
- Superbet tournaments endpoint
- Scorealarm tournament details
- Scorealarm events
- Game discovery
- Dataclass serialization

**Note**: API tests may fail in sandboxed environments due to network restrictions, but dataclass and service logic tests will pass.

## Match Data Structure

Example match object:

```python
{
    "id": 60192783,
    "platform_id": "br:match:60192783",
    "offer_id": "ax:match:7875117",
    "match_date": datetime(2026, 2, 13, 10, 0, 0),
    "match_status": 110,
    "match_state": 2,
    "sport_id": 3,
    "team1": {"id": 6278, "name": "Ravensburg Towerstars"},
    "team2": {"id": 5424, "name": "Dresdner Eislowen"},
    "scores": [
        {"team1": 1, "team2": 2, "type": 0},  # Final
        {"team1": 0, "team2": 0, "type": 1},  # 1st period
        {"team1": 0, "team2": 1, "type": 2},  # 2nd period
        {"team1": 1, "team2": 0, "type": 3},  # 3rd period
    ],
    "season": {"id": 120745, "name": "DEL 2 24/25"},
    "competition": {"id": 267, "name": "DEL 2"},
    "category": {"id": 41, "name": "Alemanha", "sport_id": 3}
}
```

## Integration with Existing Code

The implementation maintains backward compatibility:

- Old `SuperbetClient.get_tournaments()` method still works
- New methods use different return types (`ScorealarmTournament` vs `SuperbetTournament`)
- All models follow the existing dataclass pattern with `to_dict()` methods
- Uses the same async context manager pattern as existing clients

## Performance Considerations

- **Caching**: SuperbetClient includes TTL-based caching for tournaments (default: 1 hour)
- **Concurrency**: GameDiscoveryService uses `asyncio.gather()` for parallel API calls
- **Rate Limiting**: Consider adding delays between requests for large-scale discovery
- **Limits**: Use the `limit` parameter in discovery methods to control scope

## Future Enhancements

Possible improvements:

1. Add retry logic for failed API calls
2. Implement more sophisticated caching strategies
3. Add rate limiting/throttling
4. Expand H2H and form analysis
5. Add filtering by date ranges for matches
6. Include betting odds integration
7. Add WebSocket support for live updates

## Error Handling

All methods include comprehensive error handling:

- Network errors are logged and caught
- Invalid data returns `None` or empty lists
- Parsing errors are logged but don't crash the application
- Use try/except blocks when calling API methods

## Dependencies

- `aiohttp` - Async HTTP client
- Python 3.8+ - For dataclasses and type hints
- Existing Superbet infrastructure

## License

Same as parent project.
