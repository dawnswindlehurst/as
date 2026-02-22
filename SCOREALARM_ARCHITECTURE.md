# ScorealarmClient Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                     ScorealarmClient System Architecture                │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          User Application Layer                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      GameDiscoveryService                               │
│  • discover_games_by_sport(sport_id, limit)                            │
│  • discover_all_games(sport_ids, limit_per_sport)                      │
│  • get_valuable_sports()                                                │
│  • get_all_sports()                                                     │
└─────────────────────────────────────────────────────────────────────────┘
                    │                                  │
                    ▼                                  ▼
    ┌───────────────────────────┐      ┌────────────────────────────┐
    │    SuperbetClient         │      │   ScorealarmClient         │
    │  ───────────────────────  │      │  ────────────────────────  │
    │  • get_sports()           │      │  • get_tournament_details()│
    │  • get_tournaments_by_    │      │  • get_competition_events()│
    │    sport()                │      │  • get_event_detail()      │
    │  • get_tournaments()      │      │                            │
    │    (legacy)               │      │                            │
    └───────────────────────────┘      └────────────────────────────┘
                    │                                  │
                    ▼                                  ▼
    ┌───────────────────────────┐      ┌────────────────────────────┐
    │  Superbet API             │      │  Scorealarm Stats API      │
    │  ─────────────────────    │      │  ──────────────────────    │
    │  production-superbet-     │      │  scorealarm-stats.         │
    │  offer-br.freetls.        │      │  freetls.fastly.net        │
    │  fastly.net               │      │                            │
    │                           │      │  Platform: brsuperbetsport │
    │  • /struct                │      │  • /competition/details/   │
    │  • /sport/{id}/           │      │    tournaments             │
    │    tournaments            │      │  • /competition/events     │
    │  • /events/...            │      │  • /event/detail           │
    └───────────────────────────┘      └────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          Data Models Layer                              │
│  ───────────────────────────────────────────────────────────────────   │
│  Superbet Models              │  Scorealarm Models                      │
│  • SuperbetEvent              │  • ScorealarmSport                      │
│  • SuperbetOdds               │  • ScorealarmTournament                 │
│  • SuperbetMarket             │  • ScorealarmTournamentDetails          │
│  • SuperbetTournament         │  • ScorealarmMatch                      │
│                               │  • ScorealarmMatchDetail                │
│                               │  • ScorealarmTeam, Score, Season, etc.  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          Data Flow Example                              │
└─────────────────────────────────────────────────────────────────────────┘

User requests matches for Bandy (sport_id=7):

1. GameDiscoveryService.discover_games_by_sport(7)
   │
   ├─> SuperbetClient.get_tournaments_by_sport(7)
   │   └─> GET /sport/7/tournaments
   │       └─> Returns: [Tournament{id=1234, name="Swedish Bandy"}, ...]
   │
   └─> For each tournament:
       │
       ├─> ScorealarmClient.get_tournament_details(1234)
       │   └─> GET /competition/details/tournaments?tournament_id=ax:tournament:1234
       │       └─> Returns: {competition_id: 100, seasons: [{id: 500}]}
       │
       └─> ScorealarmClient.get_competition_events(500, 100)
           └─> GET /competition/events?season_id=br:season:500&competition_id=br:competition:100
               └─> Returns: [Match{team1, team2, scores, ...}, ...]

Result: List of ScorealarmMatch objects ready for analysis

┌─────────────────────────────────────────────────────────────────────────┐
│                          Key Features                                   │
└─────────────────────────────────────────────────────────────────────────┘

✓ Async/Await Pattern
  - All API calls use aiohttp for async I/O
  - Context managers for resource management
  - Concurrent processing with asyncio.gather()

✓ Error Handling
  - Comprehensive try/except blocks
  - Graceful degradation (returns [] or None)
  - Detailed logging for debugging

✓ Caching
  - TTL-based caching in SuperbetClient
  - Default 1-hour cache for tournaments
  - Configurable cache TTL

✓ Data Consistency
  - All models use dataclasses
  - All models have to_dict() serialization
  - Type hints throughout

✓ Backward Compatibility
  - Old SuperbetClient methods still work
  - New methods use separate return types
  - No breaking changes to existing code

┌─────────────────────────────────────────────────────────────────────────┐
│                    Supported Sports (53 total)                          │
└─────────────────────────────────────────────────────────────────────────┘

Traditional Sports:
  • Football (5), Basketball (4), Tennis (2), Hockey (3)
  • Volleyball (1), Baseball (20), American Football (12)
  • Rugby (8), Handball (11), Cricket (32), Golf (16)
  • And 25+ more...

Esports:
  • League of Legends (39), Dota 2 (54), CS2 (55)
  • Valorant (153), Rainbow Six (80), Call of Duty (61)
  • Arena of Valor (85), Honor of Kings (88)

"Gold" Sports (High Value):
  💎 Bandy (7), Floorball (9), Water Polo (15)
  💎 Curling (22), Field Hockey (29), Rink Hockey (71)
  💎 Lacrosse (81)

┌─────────────────────────────────────────────────────────────────────────┐
│                          Testing Strategy                               │
└─────────────────────────────────────────────────────────────────────────┘

Unit Tests:
  ✓ Dataclass instantiation and serialization
  ✓ Service logic (valuable sports, etc.)

Integration Tests:
  ✓ API client methods (when network available)
  ✓ End-to-end discovery flow
  ✓ Error handling

Current Status: 5/7 tests passing
  - API tests fail in sandbox (network restrictions)
  - All logic tests pass
