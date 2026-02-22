# 📊 Historical Database - Professional Sports Betting Analysis

## Overview

This comprehensive historical database system provides COMPLETE season and tournament data for professional sports betting analysis across NBA, Soccer, Esports, and Tennis.

## Features

✅ **Complete Season Data** - Not just 3 months, but FULL SEASONS and COMPLETE TOURNAMENTS
✅ **Advanced Analytics** - Player props, team stats, BTTS, map analysis, and more
✅ **Pattern Recognition** - Identify profitable betting patterns with statistical significance
✅ **Multi-Sport Support** - NBA, Soccer, Esports (CS2, Valorant, LoL, Dota 2), Tennis
✅ **Comprehensive Splits** - Home/away, rest days, vs opponent quality, after wins/losses, and more
✅ **Value Bet Tracking** - Historical tracking of value bets and their results

## Database Structure

### 📊 NBA (4 tables)

#### `nba_games`
Complete game data with quarter scores, odds, rest days, back-to-back tracking
- 40+ columns of game data
- Quarter-by-quarter scores
- Betting results (total, spread)
- Context (rest days, back-to-back)

#### `nba_player_game_stats`
Every player's stats for every game
- 30+ statistical categories
- Fantasy combos (PRA, stocks, etc.)
- Opponent context
- Rest and fatigue tracking

#### `nba_team_stats`
Aggregated team statistics
- Records (overall, home, away)
- Advanced ratings (offensive, defensive, net)
- Betting performance (ATS, O/U records)
- Streaks and form

#### `nba_player_props_analysis`
Comprehensive player props analysis with ALL splits
- Overall season stats
- Home/Away splits
- After Win/Loss splits
- After Win/Loss Streak (3+) splits
- vs Top 10 / Bottom 10 Defense splits
- Rest days impact (back-to-back, 1 day, 2+ days)
- With/Without key teammate
- Last 5 and Last 10 games
- Trend analysis
- Head-to-head vs specific opponents

### ⚽ Soccer (3 tables)

#### `soccer_matches`
Complete match data for 8+ leagues
- Full match statistics
- Halftime scores
- Betting results (BTTS, Over/Under, etc.)
- Team form and positions

#### `soccer_team_stats`
Team statistics by league
- Record (home, away, overall)
- Goals scored/conceded
- Clean sheets
- BTTS percentages
- Over/Under percentages
- Form and streaks

#### `soccer_player_stats`
Player statistics
- Goals and assists
- Shooting stats
- Passing and defending
- Anytime goalscorer rate
- Home/Away splits

### 🎮 Esports (5 tables)

#### `esports_matches`
Match data for CS2, Valorant, LoL, Dota 2
- Tournament information and tier
- Team rankings
- Best-of format
- Form and context

#### `esports_map_stats`
Map-by-map statistics (CS2, Valorant)
- Half scores
- Side stats (CT/T rounds)
- Overtime tracking
- Over/Under results

#### `esports_player_stats`
Player performance stats
- Common stats (K/D/A)
- Game-specific stats (ADR, KAST, ACS for FPS)
- Economy stats (CS, gold for MOBA)
- Agent/Champion/Hero tracking

#### `esports_team_stats`
Team statistics and rankings
- Match and map records
- World and regional rankings
- Map pool analysis
- Performance vs different tiers

#### `esports_player_props_analysis`
Player props with comprehensive splits
- By map analysis
- vs Team tier splits
- Online vs LAN
- By agent/champion
- Form and trends

### 🎾 Tennis (2 tables)

#### `tennis_matches`
ATP and WTA match data
- Complete set scores
- Match statistics
- Total games Over/Under results
- Surface and tournament category

#### `tennis_player_stats`
Player statistics
- Surface-specific performance
- Tournament category performance
- Serve and return stats
- Tiebreak performance
- vs ranking brackets

### 📈 Analysis (2 tables)

#### `betting_patterns`
Identified profitable betting patterns
- Pattern conditions and details
- Hit rate and ROI
- Statistical significance (Z-score)
- Confidence levels

#### `value_bets_history`
Historical value bet tracking
- Bet details and selection
- Value calculation (edge, probabilities)
- Results and P&L
- Factors used in analysis

## Data Population Scripts

> Note: historical population for traditional sports is now consolidated in `run_populate_historical.py` (legacy per-sport population scripts were removed from `scripts/`).

### NBA Season Populator
```bash
python run_populate_historical.py
```
Collects:
- Complete season games (120+ days)
- All player game stats
- Team statistics
- Calculates player props analysis

### Soccer Leagues Populator
```bash
python run_populate_historical.py
```
Collects data for 8 leagues:
- 🇧🇷 Brasileirão Série A
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
- 🇪🇸 La Liga
- 🇮🇹 Serie A
- 🇩🇪 Bundesliga
- 🇫🇷 Ligue 1
- 🏆 UEFA Champions League
- 🏆 UEFA Europa League

### Esports Tournaments Populator
```bash
python scripts/populate_esports_tournaments.py
```
Collects:
- Valorant (VCT)
- CS2 (HLTV)
- League of Legends (LEC/LCS)
- Dota 2 (OpenDota)

### Tennis Season Populator
```bash
python run_populate_historical.py
```
Collects:
- ATP Tour
- WTA Tour
- All tournament categories

### Pattern Calculator
```bash
python scripts/calculate_patterns.py
```
Analyzes all data to:
- Identify profitable patterns
- Calculate ROI and hit rates
- Determine statistical significance
- Generate value bet reports

## Analytics Usage

### NBA Player Props Analysis

```python
from analytics.betting_analytics import get_analytics

analytics = get_analytics()

# Get comprehensive player prop analysis
props = analytics.get_player_prop_analysis("LeBron James", "points", 25.5)

print(f"Overall: {props['overall']['avg']} avg, {props['overall']['over_rate']}% over rate")
print(f"Home: {props['home']['avg']} avg, {props['home']['over_rate']}% over rate")
print(f"Away: {props['away']['avg']} avg, {props['away']['over_rate']}% over rate")
print(f"Last 5: {props['last_5']['avg']} avg, trend: {props['last_5']['trend']}")

analytics.close()
```

Result:
```python
{
    "overall": {"avg": 27.3, "over_rate": 68.2, "games": 45},
    "home": {"avg": 28.1, "over_rate": 72.0, "games": 22},
    "away": {"avg": 26.5, "over_rate": 64.3, "games": 23},
    "last_5": {"avg": 29.2, "over_rate": 80.0, "trend": "UP"},
    "last_10": {"avg": 28.5, "over_rate": 75.0}
}
```

### Soccer BTTS Analysis

```python
from analytics.betting_analytics import get_analytics

analytics = get_analytics()

# Get team BTTS analysis
btts = analytics.get_team_btts_analysis("Liverpool", "eng.1")

print(f"Overall BTTS Rate: {btts['overall']['rate']}%")
print(f"Home BTTS Rate: {btts['home']['rate']}%")
print(f"Away BTTS Rate: {btts['away']['rate']}%")
print(f"Trend: {btts['trend']}")

analytics.close()
```

Result:
```python
{
    "overall": {"rate": 58.0, "games": 24},
    "home": {"rate": 65.0, "games": 12},
    "away": {"rate": 50.0, "games": 12},
    "trend": "UP"
}
```

### Esports Map Analysis

```python
from analytics.betting_analytics import get_analytics

analytics = get_analytics()

# Get team map statistics
maps = analytics.get_team_map_stats("Sentinels", "valorant")

for map_name, stats in maps.items():
    print(f"{map_name}: {stats['win_rate']}% win rate ({stats['won']}/{stats['played']})")

analytics.close()
```

Result:
```python
{
    "ascent": {"played": 15, "won": 12, "win_rate": 80.0},
    "bind": {"played": 10, "won": 7, "win_rate": 70.0},
    "haven": {"played": 8, "won": 3, "win_rate": 37.5}
}
```

### Value Bets Query

```python
from analytics.betting_analytics import get_analytics

analytics = get_analytics()

# Get current value bets
value_bets = analytics.get_value_bets("nba", min_edge=5.0)

for bet in value_bets:
    print(f"Match: {bet['match']}")
    print(f"Selection: {bet['selection']}")
    print(f"Edge: {bet['edge']:.1f}%")
    print(f"Confidence: {bet['confidence']:.2f}")
    print("-" * 50)

analytics.close()
```

## Database Initialization

```python
from database.db import init_db

# Initialize all tables (including historical models)
init_db()
```

This creates all tables in the configured database (default: SQLite).

## Configuration

The system uses the existing database configuration from `config/settings.py`:

```python
DATABASE_URL = "sqlite:///./capivara_bet.db"
# or
DATABASE_URL = "postgresql://user:pass@localhost/dbname"
```

## Data Flow

1. **Population Scripts** → Collect raw data from APIs/scrapers
2. **Database Storage** → Store in normalized historical tables
3. **Pattern Calculator** → Analyze data to find profitable patterns
4. **Analytics Module** → Provide query functions for analysis
5. **Dashboard/Application** → Display insights and value bets

## Performance Considerations

- **Indexing**: Key columns are indexed (game_id, match_id, player_id, etc.)
- **Pagination**: Use pagination for large queries
- **Caching**: Analytics results can be cached for performance
- **Batch Processing**: Population scripts use batch commits

## Advanced Features

### Statistical Significance

Pattern calculator includes Z-score calculation for statistical significance:
- **HIGH confidence**: Z-score > 2.0, sample size > 20
- **MEDIUM confidence**: Z-score > 1.5, sample size > 10
- **LOW confidence**: Below thresholds

### ROI Calculation

Patterns track ROI based on actual hit rates and average odds:
```python
roi = ((hit_rate * avg_odds) - 1) * 100
```

### Trend Detection

Player props analysis includes trend detection:
- **UP**: Last 5 avg > Season avg
- **DOWN**: Last 5 avg < Season avg
- **STABLE**: Within 5% of season avg

## Extending the System

### Adding New Sports

1. Create models in `database/historical_models.py`
2. Create population script in `scripts/`
3. Add analytics functions in `analytics/betting_analytics.py`
4. Update pattern calculator

### Adding New Splits

1. Add columns to relevant model
2. Update population script to calculate split
3. Add analysis function for the split

## Integration with Existing System

The historical database integrates with the existing Capivara Bet system:

- **Scrapers**: Reuses Scorealarm, VLR, HLTV, and other scrapers
- **Database**: Extends existing database with new tables
- **Dashboard**: Can be visualized in Streamlit dashboard
- **Models**: Can feed into existing predictive models

## Example: Complete Workflow

```python
# 1. Initialize database
from database.db import init_db
init_db()

# 2. Populate data
from run_populate_historical import main as populate_historical

populate_historical()

# 3. Calculate patterns
from scripts.calculate_patterns import main as calc_patterns
calc_patterns()

# 4. Analyze and find value
from analytics.betting_analytics import get_analytics

analytics = get_analytics()
props = analytics.get_player_prop_analysis("LeBron James", "points", 25.5)
btts = analytics.get_team_btts_analysis("Liverpool", "eng.1")
value_bets = analytics.get_value_bets("nba", min_edge=5.0)

print("LeBron Props:", props)
print("Liverpool BTTS:", btts)
print("Value Bets:", value_bets)

analytics.close()
```

## License

Same as main Capivara Bet project - Educational and research purposes only.

## Support

For questions and issues, refer to the main project README or open an issue on GitHub.
