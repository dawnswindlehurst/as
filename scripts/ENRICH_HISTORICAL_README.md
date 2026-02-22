# Enrich Historical Matches Script

## Overview

The `enrich_historical.py` script enriches existing historical matches in the database with detailed V2 API statistics including:

- **Expected Goals (xG)** for both teams
- **Shots on Goal** statistics
- **Corner Kicks** statistics
- **Goal Events** with player details (scorer, assist provider, minute)

## Prerequisites

1. Matches must already exist in the database (populated via `populate_historical.py`)
2. Matches must have:
   - `is_finished = True`
   - Valid `offer_id` (required for V2 API calls)

## Database Schema Changes

The script requires the following new columns in the `scorealarm_matches` table:

```sql
ALTER TABLE scorealarm_matches ADD COLUMN enriched_at TIMESTAMP;
ALTER TABLE scorealarm_matches ADD COLUMN xg_home FLOAT;
ALTER TABLE scorealarm_matches ADD COLUMN xg_away FLOAT;
ALTER TABLE scorealarm_matches ADD COLUMN shots_on_goal_home INTEGER;
ALTER TABLE scorealarm_matches ADD COLUMN shots_on_goal_away INTEGER;
ALTER TABLE scorealarm_matches ADD COLUMN corners_home INTEGER;
ALTER TABLE scorealarm_matches ADD COLUMN corners_away INTEGER;
ALTER TABLE scorealarm_matches ADD COLUMN goal_events JSON;
```

## Usage

### Basic Usage

Enrich all pending matches:

```bash
python scripts/enrich_historical.py
```

### With Limit

Enrich only the first 500 matches:

```bash
python scripts/enrich_historical.py --limit 500
```

### Force Re-enrichment

Force re-enrichment of already enriched matches:

```bash
python scripts/enrich_historical.py --force
```

### Custom Rate Limiting

Set custom delay between API requests (in milliseconds):

```bash
python scripts/enrich_historical.py --delay 200
```

### Combined Options

```bash
python scripts/enrich_historical.py --limit 1000 --delay 150
```

## How It Works

1. **Fetch Matches**: Queries database for unenriched finished matches with valid `offer_id`
2. **Batch Processing**: Processes matches in batches of 100 for efficient database commits
3. **API Calls**: For each match:
   - Calls `get_fixture_stats(fixture_id)` from V2 API
   - Extracts statistics by type:
     - Type 19: Expected Goals (xG)
     - Type 2: Shots on Goal
     - Type 5: Corner Kicks
   - Extracts goal events (type 4) with player details
4. **Save Data**: Updates match record with extracted data
5. **Mark Enriched**: Sets `enriched_at` timestamp to prevent reprocessing
6. **Error Handling**: Continues processing even if individual matches fail

## Data Format

### Enriched Match Fields

```python
{
    "enriched_at": "2026-02-13T23:00:00Z",
    "xg_home": 2.33,
    "xg_away": 1.02,
    "shots_on_goal_home": 8,
    "shots_on_goal_away": 4,
    "corners_home": 6,
    "corners_away": 3,
    "goal_events": [
        {
            "minute": 33,
            "added_time": null,
            "player_id": "eEoFsBLbpVhqQsMREWEUN",
            "player_name": "Lookman, Ademola",
            "assist_player_id": "524Lwb9169FQbvfEIUGjrl",
            "assist_player_name": "Alvarez, Julian",
            "side": 1,  # 1=home, 2=away
            "score": "1-0"
        }
    ]
}
```

## Rate Limiting

The script uses `GentleRateLimiter` with the following defaults:

- **10 requests per minute** maximum
- **100ms delay** between requests (configurable via `--delay`)
- **Night mode speedup**: Requests run 50% faster between 02:00-06:00 UTC

## Logging

The script provides detailed progress logging:

```
============================================================
🔍 ENRIQUECIMENTO DE PARTIDAS HISTÓRICAS - V2 API
============================================================
📊 4521 partidas para enriquecer
🚀 Iniciando enriquecimento em batches de 100...

📦 Batch 1/46: 100 partidas
  📈 10/100 partidas processadas no batch
  📈 20/100 partidas processadas no batch
  ...
✅ Batch 1/46: 100 partidas processadas
💾 Batch 1 salvo no banco

  ⚠️ Partida 12345: sem dados V2 disponíveis
  ...

============================================================
🎉 ENRIQUECIMENTO CONCLUÍDO
============================================================
📊 Total: 4521 partidas
✅ Enriquecidas: 4500 (99.5%)
⚠️ Sem dados V2: 20 (0.4%)
❌ Erros: 1 (0.0%)
⏭️ Puladas: 0
============================================================
```

## Error Handling

- **No V2 Data**: Matches without V2 data are marked as `enriched_at` to prevent reprocessing
- **Individual Failures**: Script continues processing other matches if one fails
- **Batch Commits**: Database commits happen per batch, minimizing data loss on errors
- **Graceful Degradation**: Missing stats (xG, shots, corners) are set to `NULL` rather than failing

## Performance

- **Batch Size**: 100 matches per batch
- **Expected Duration**: Depends on total matches and delay settings
  - ~10,000 matches with 100ms delay: ~16-20 minutes
  - With night mode speedup: ~10-12 minutes

## Testing

Run the test suite to validate extraction logic:

```bash
python test_enrich_historical.py
```

Tests cover:
- xG extraction and parsing
- Shots and corners extraction
- Goal events with player details
- Missing/invalid data handling

## Related Documentation

- `SCOREALARM_V2_IMPLEMENTATION.md` - V2 API endpoints and data models
- `scrapers/superbet/scorealarm_client.py` - ScorealarmClient with V2 methods
- `jobs/populate_historical.py` - Historical data population script

## Troubleshooting

### No matches to enrich

Check that:
1. Matches exist in database: `SELECT COUNT(*) FROM scorealarm_matches;`
2. Matches are finished: `SELECT COUNT(*) FROM scorealarm_matches WHERE is_finished = true;`
3. Matches have offer_id: `SELECT COUNT(*) FROM scorealarm_matches WHERE offer_id IS NOT NULL;`

### V2 API returns no data

Some matches may not have V2 statistics available in the Scorealarm API. This is normal and the script marks these as enriched to avoid reprocessing.

### Rate limiting errors

If you encounter rate limiting errors, increase the `--delay` parameter:

```bash
python scripts/enrich_historical.py --delay 300  # 300ms delay
```
