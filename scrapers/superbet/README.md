# Superbet API Integration

This module provides integration with the Superbet API for fetching odds and events across multiple sports.

## Supported Sports

### eSports
- **CS2** (Counter-Strike 2) - Sport ID: 55
- **Dota 2** - Sport ID: 54
- **Valorant** - Sport ID: 153
- **League of Legends** - Sport ID: 39

### Traditional Sports
- **Tennis** - Sport ID: 4
- **Football** (Soccer) - Sport ID: 5

## API Structure

### Base URL
```
https://production-superbet-offer-br.freetls.fastly.net/v2/pt-BR
```

### Available Endpoints
- `/sports` - List all available sports
- `/tournaments` - List all tournaments
- `/events/by-date` - Get events by date range
- `/events/{event_id}` - Get specific event details
- `/events/live` - Get currently live events

## Usage Examples

### eSports

```python
import asyncio
from scrapers.superbet import SuperbetEsports

async def fetch_cs2_matches():
    async with SuperbetEsports() as esports:
        matches = await esports.get_cs2_matches(days_ahead=7)
        for match in matches:
            print(f"{match.team1} vs {match.team2}")
            print(f"Tournament: {match.tournament_name}")
            print(f"Start: {match.start_time}")
            print()

asyncio.run(fetch_cs2_matches())
```

### Tennis

```python
import asyncio
from scrapers.superbet import SuperbetTennis

async def fetch_tennis():
    async with SuperbetTennis() as tennis:
        # All tennis matches
        matches = await tennis.get_tennis_matches(days_ahead=7)
        
        # ATP only
        atp_matches = await tennis.get_atp_matches(days_ahead=7)
        
        # WTA only
        wta_matches = await tennis.get_wta_matches(days_ahead=7)

asyncio.run(fetch_tennis())
```

### Football

```python
import asyncio
from scrapers.superbet import SuperbetFootball

async def fetch_football():
    async with SuperbetFootball() as football:
        # All football matches
        matches = await football.get_football_matches(days_ahead=7)
        
        # Brasileirão only
        brasileirao = await football.get_brasileirao_matches(days_ahead=7)
        
        # Champions League only
        ucl = await football.get_champions_league_matches(days_ahead=7)

asyncio.run(fetch_football())
```

### Using the Client Directly

```python
import asyncio
from scrapers.superbet import SuperbetClient

async def fetch_with_client():
    async with SuperbetClient() as client:
        # Get all sports
        sports = await client.get_sports()
        
        # Get tournaments for a sport
        tournaments = await client.get_tournaments(sport_id=55)
        
        # Get events by sport
        events = await client.get_events_by_sport(sport_id=55)
        
        # Get live events
        live = await client.get_live_events()

asyncio.run(fetch_with_client())
```

## Caching

The client includes built-in caching with TTL (Time To Live):

- **Tournament cache**: 1 hour default TTL
- Reduces API calls for frequently accessed data
- Thread-safe implementation
- Automatic cleanup of expired entries

## Data Models

### SuperbetEvent
Represents a sporting event with:
- Event ID and name
- Sport information
- Tournament information
- Teams/participants
- Markets and odds
- Start time
- Live status

### SuperbetMarket
Represents a betting market with:
- Market ID and name
- Market type
- List of odds

### SuperbetOdds
Represents odds for an outcome:
- Outcome ID and name
- Odds value
- Active status

### SuperbetTournament
Represents a tournament:
- Tournament ID and name
- Sport information
- Region and tier

## Error Handling

All methods include error handling and logging:
- Network errors are logged and raised
- Invalid data is logged and skipped
- Async context managers ensure proper cleanup

## Notes

- All API calls are asynchronous using `aiohttp`
- Use async context managers for proper session management
- Live matches are automatically deduplicated
- Dates are in ISO format with timezone support
