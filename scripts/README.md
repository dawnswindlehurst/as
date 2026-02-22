# Scripts Directory

This directory contains utility scripts for deploying and managing the Capivara Bet application.

## Deployment Scripts

### `oracle_setup.sh`

**Purpose**: Initial Oracle Cloud instance setup

**Usage**:
```bash
./scripts/oracle_setup.sh
```

**What it does**:
- Checks system requirements (RAM, OS)
- Installs Docker and Docker Compose
- Configures firewall rules for Oracle Cloud
- Creates necessary directories
- Sets up swap space (if needed)
- Installs system dependencies

**When to use**: Run once when setting up a new Oracle Cloud instance

---

### `deploy.sh`

**Purpose**: Deploy or update the application

**Usage**:
```bash
./scripts/deploy.sh
```

**What it does**:
1. Pulls latest code from Git
2. Stops existing containers
3. Builds Docker images
4. Runs database migrations
5. Starts all services
6. Verifies health of services

**When to use**: 
- Initial deployment after setup
- Updating the application
- Redeploying after configuration changes

---

## Development Scripts

### `dev.sh`

**Purpose**: Start development environment

**Usage**:
```bash
./scripts/dev.sh
```

**What it does**:
- Starts the application using the development Docker Compose configuration
- Enables hot-reloading for development

**When to use**: Local development and testing

---

## Data Population Scripts

### `run_populate_historical.py` (project root)

Main entrypoint to populate historical data (NBA, Soccer, Tennis and other supported sports via Scorealarm).

### `populate_esports_tournaments.py`

Populates the database with esports tournament data.

### `enrich_historical.py`

Enriches stored historical matches with additional derived fields/metadata.

### `map_sport_fields.py`

Samples up to 5 finished matches per sport, requests V2 fixture overview data, and saves per-sport field maps under `analysis/sport_field_mapping/`.

**Usage**:
```bash
python scripts/map_sport_fields.py --sports 55 --max-ids-per-sport 100
python scripts/map_sport_fields.py --version
```

By default it stops early when it finds fields for the selected sport. Use `--no-stop-on-first-data` to continue collecting more samples.


---

## Testing Scripts

### `test_historical_db.py`

Tests historical database functionality.

### `calculate_patterns.py`

Analyzes betting patterns and statistics.

---

## Notes

- All shell scripts should be executable: `chmod +x scripts/*.sh`
- For Oracle Cloud deployment, use `oracle_setup.sh` first, then `deploy.sh`
- Python scripts should be run from the project root directory
- Check logs if any script fails: `docker-compose logs -f`

## Environment Variables

Most scripts rely on environment variables defined in `.env`. Make sure to:
1. Copy `.env.example` to `.env`
2. Configure all required variables
3. Never commit `.env` to version control
