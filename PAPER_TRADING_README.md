# Paper Trading System Documentation

## Overview

This paper trading system implements automated value bet detection and simulated betting for sports and esports. It uses ELO/Glicko-2 rating systems to estimate team strengths and detect positive expected value (edge) betting opportunities.

## Architecture

The system consists of several key components:

### 1. Rating Systems (`analysis/rating_system.py`)
- **EloRating**: Classic ELO rating system for team strength estimation
- **GlickoRating**: More advanced Glicko-2 system with uncertainty modeling

### 2. Value Bet Detection (`analysis/value_detector.py`)
- Analyzes matches to find positive edge opportunities
- Compares our probability estimates with bookmaker odds
- Filters opportunities by minimum edge threshold (default 3%)

### 3. Match Sync (`jobs/sync_matches.py`)
- Syncs upcoming matches (next 48 hours)
- Updates finished match results (last 2 hours)
- Fetches and stores latest odds

### 4. Paper Trading (`paper_trading/paper_trader.py`)
- Places simulated bets on detected opportunities
- Settles bets when matches finish
- Tracks performance statistics by sport

### 5. Main Job (`jobs/paper_trading_job.py`)
- Orchestrates the complete workflow
- Updates team ratings based on results
- Runs all components in sequence

## Database Models

### ScorealarmTeamRating
Stores team ratings across all sports:
- `elo_rating`: ELO rating (default 1500)
- `glicko_rating`: Glicko-2 rating
- `glicko_rd`: Rating deviation (uncertainty)
- `glicko_vol`: Volatility
- `matches_played`: Total matches
- `last_match_date`: Last match timestamp

### PaperBet
Individual paper bets:
- `match_id`: Match reference
- `bet_on`: Selection (team1/team2/draw)
- `odds`: Odds at time of bet
- `stake`: Bet amount (default R$100)
- `our_probability`: Our estimated probability
- `implied_probability`: Bookmaker's implied probability
- `edge`: Calculated edge
- `status`: pending/won/lost/void
- `profit`: Profit/loss after settlement

### PaperTradingStats
Aggregated statistics by sport:
- `total_bets`: Number of bets placed
- `wins`/`losses`: Win/loss counts
- `total_staked`: Total amount bet
- `total_profit`: Net profit/loss
- `avg_odds`: Average odds
- `avg_edge`: Average edge
- `roi`: Return on Investment

## Usage

### Run Once
Execute a single cycle of the paper trading system:

```bash
python run_paper_trading.py --once
```

### Run Scheduled
Run continuously every N minutes (default 30):

```bash
python run_paper_trading.py
```

Or specify custom interval:

```bash
python run_paper_trading.py --interval 15
```

### Configuration

Environment variables can be set in `.env`:

```bash
# Minimum edge required (default 3%)
MIN_EDGE=0.03

# Paper trading stake per bet (default R$100)
PAPER_TRADING_STAKE=100

# Database URL
DATABASE_URL=sqlite:///capivara_bet.db
```

## Workflow

Each cycle executes the following steps:

1. **Sync Matches**
   - Fetch upcoming matches (next 48h)
   - Update finished matches (last 2h)
   - Update odds for pending matches

2. **Update Team Ratings**
   - Process finished matches
   - Update ELO ratings for both teams
   - Track match counts and timestamps

3. **Settle Bets**
   - Find pending bets with finished matches
   - Determine winners
   - Calculate profit/loss
   - Update statistics

4. **Find Opportunities**
   - Scan upcoming matches
   - Calculate team win probabilities using ELO
   - Compare with bookmaker odds
   - Detect positive edge opportunities

5. **Place Bets**
   - Automatically place paper bets on opportunities
   - Avoid duplicate bets
   - Track all bet details for analysis

6. **Report Stats**
   - Log performance metrics by sport
   - Show win rate, ROI, total profit

## Example Output

```
🔄 Iniciando ciclo Paper Trading...
✅ Sync completo
✅ Ratings atualizados
✅ Apostas liquidadas
✅ Novas apostas registradas
📊 Estatísticas por Esporte:
  Counter-Strike 2: 15 bets | Win: 9/15 (60.0%) | ROI: 12.5% | Profit: R$ 187.50
  Dota 2: 8 bets | Win: 5/8 (62.5%) | ROI: 15.2% | Profit: R$ 121.60
✅ Ciclo Paper Trading completo
```

## Testing

Run the test suite:

```bash
pytest test_paper_trading.py -v
```

Test coverage includes:
- ELO rating calculations
- Glicko-2 rating updates
- Odds to probability conversions
- Edge calculations
- Value bet detection
- Database model operations

## Notes

- This is a **paper trading** system - no real money is used
- Use it to validate your betting strategy before risking real money
- The system requires match data from Scorealarm API
- Team ratings improve over time as more matches are processed
- Minimum edge threshold helps filter out low-quality opportunities
- ROI and statistics track performance across different sports

## Future Enhancements

Potential improvements:
- Machine learning models for probability estimation
- Advanced markets (over/under, handicaps, etc.)
- Bankroll management strategies
- Real-time odds tracking
- CLV (Closing Line Value) analysis
- Multi-bookmaker comparison
- Telegram notifications for opportunities
