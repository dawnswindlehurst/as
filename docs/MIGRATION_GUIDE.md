# Migration Guide: Docker to Oracle Cloud

Guide for migrating from local Docker deployment to Oracle Cloud 24/7 deployment.

## Prerequisites

- Existing Capivara Bet installation
- Oracle Cloud Free Tier account
- SSH access to Oracle Cloud instance

## Migration Steps

### 1. Backup Current Data

If you have existing SQLite database with valuable data:

```bash
# Backup SQLite database
cp capivara_bet.db capivara_bet.db.backup

# Export data if needed
python -c "
from database.db import SessionLocal
from database.models import Match, Bet, TeamRating
import json

db = SessionLocal()

# Export matches
matches = db.query(Match).all()
with open('matches_export.json', 'w') as f:
    json.dump([{
        'team1': m.team1,
        'team2': m.team2,
        'game': m.game,
        # ... add more fields as needed
    } for m in matches], f)

# Export bets
bets = db.query(Bet).all()
# ... similar export

db.close()
"
```

### 2. Set Up Oracle Cloud Instance

Follow the [Oracle Cloud Setup Guide](docs/ORACLE_DEPLOYMENT.md) to:
1. Create compute instance
2. Configure network security
3. Run setup script

### 3. Update Environment Configuration

Copy your local `.env` to the Oracle instance:

```bash
# On your local machine
scp .env ubuntu@<oracle-ip>:~/capivara-bet/.env
```

Or manually configure on Oracle instance:

```bash
# On Oracle instance
cd ~/capivara-bet
cp .env.example .env
nano .env
```

**Important changes for Oracle:**

```env
# Change from SQLite to PostgreSQL
DATABASE_URL=postgresql://capivara:your_password@db:5432/capivara_bet

# Enable Oracle optimizations
ORACLE_DEPLOYMENT=true

# Configure collection
ENABLE_INITIAL_COLLECTION=true  # Set to false if you don't want historical data
COLLECTION_INTERVAL_HOURS=2

# Add Telegram notifications (recommended)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
NOTIFY_ON_COLLECTION_COMPLETE=true
NOTIFY_ON_ERROR=true
```

### 4. Migrate Data (Optional)

If you have valuable data in SQLite, migrate to PostgreSQL:

```bash
# Option A: Manual migration using pgloader (if available)
sudo apt install pgloader
pgloader capivara_bet.db postgresql://capivara:password@localhost:5432/capivara_bet

# Option B: Python migration script
python scripts/migrate_sqlite_to_postgres.py  # You'll need to create this

# Option C: Start fresh with historical data collection
# Just deploy and let the collector populate the database
```

### 5. Deploy on Oracle

```bash
# On Oracle instance
cd ~/capivara-bet
./scripts/deploy.sh
```

### 6. Verify Deployment

```bash
# Check services are running
docker-compose -f docker-compose.oracle.yml ps

# Check API health
curl http://localhost:8000/api/health

# Check metrics
curl http://localhost:8000/api/metrics | jq

# View collector logs
docker-compose -f docker-compose.oracle.yml logs -f collector
```

### 7. Access from Your Computer

Update Oracle Cloud firewall and access the services:

```bash
# Dashboard
http://<oracle-ip>:8501

# API
http://<oracle-ip>:8000/docs

# Health check
curl http://<oracle-ip>:8000/api/health
```

## Differences: Local vs Oracle Deployment

| Feature | Local (Docker Compose) | Oracle (docker-compose.oracle.yml) |
|---------|----------------------|-----------------------------------|
| Database | SQLite or PostgreSQL | PostgreSQL (optimized) |
| Resources | No limits | Memory limits enforced |
| Collection | Manual or cron | Automated service (24/7) |
| Monitoring | Manual | Health checks + Telegram |
| Restart | Manual | Automatic (restart: always) |
| Logging | Standard | Rotated (10MB, 3 files) |
| Pool Size | Default | Optimized for 12GB RAM |

## Post-Migration Checklist

- [ ] All services running (`docker ps`)
- [ ] Database accessible
- [ ] Dashboard loads correctly
- [ ] API responds to health check
- [ ] Collection service is running
- [ ] Telegram notifications working (if configured)
- [ ] Historical data being collected (check logs)
- [ ] Firewall rules configured
- [ ] Monitoring set up

## Rollback Plan

If migration fails, you can:

1. **Keep Oracle deployment** and fix issues
2. **Revert to local**: 
   ```bash
   # On local machine
   docker-compose up -d
   ```
3. **Restore backup**:
   ```bash
   cp capivara_bet.db.backup capivara_bet.db
   ```

## Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
docker exec capivara_db pg_isready

# Check connection from API
docker-compose -f docker-compose.oracle.yml logs api | grep -i database
```

### Collection Not Starting

```bash
# Check collector logs
docker-compose -f docker-compose.oracle.yml logs collector

# Restart collector
docker-compose -f docker-compose.oracle.yml restart collector
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Reduce resource limits in docker-compose.oracle.yml
# Or reduce MAX_WORKERS and BATCH_SIZE in .env
```

### Slow Performance

```bash
# Check system resources
htop
free -h

# Increase collection interval
# Edit .env: COLLECTION_INTERVAL_HOURS=4
docker-compose -f docker-compose.oracle.yml restart collector
```

## Performance Tuning

After migration, monitor and adjust:

### Collection Frequency

```env
# Less frequent = lower resource usage
COLLECTION_INTERVAL_HOURS=4

# More frequent = more current data
COLLECTION_INTERVAL_HOURS=1
```

### Rate Limiting

```env
# If getting rate limited by APIs
TRADITIONAL_SPORTS_RATE_LIMIT=5
HLTV_RATE_LIMIT=3

# If APIs can handle more
SUPERBET_RATE_LIMIT=30
```

### Worker Processes

```env
# Reduce if CPU/memory constrained
MAX_WORKERS=2

# Increase if resources available
MAX_WORKERS=6
```

## Best Practices

1. **Monitor logs regularly**: `docker-compose logs -f`
2. **Set up Telegram**: Get notified of issues immediately
3. **Backup database weekly**: `pg_dump` to backup file
4. **Update regularly**: `git pull && ./scripts/deploy.sh`
5. **Monitor disk space**: `df -h` and clean old logs
6. **Check health endpoints**: Automated monitoring

## Support

For migration issues:
- Check [Oracle Deployment Guide](docs/ORACLE_DEPLOYMENT.md)
- Review Docker logs
- Check GitHub Issues
- Monitor system resources

## Next Steps

After successful migration:
1. Set up automated backups
2. Configure monitoring/alerting
3. Optimize collection based on your needs
4. Consider setting up a reverse proxy (nginx) for HTTPS
5. Set up domain name (optional)
