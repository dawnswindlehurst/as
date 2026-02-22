# Oracle Cloud Deployment Guide

Complete guide for deploying Capivara Bet Esports on Oracle Cloud Free Tier (Always Free).

## Table of Contents

- [Requirements](#requirements)
- [Oracle Cloud Setup](#oracle-cloud-setup)
- [System Setup](#system-setup)
- [Application Deployment](#application-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Requirements

### Oracle Cloud Free Tier

- **Compute**: ARM Ampere A1 - 2 OCPUs + 12GB RAM
- **Storage**: 100GB Block Storage
- **OS**: Ubuntu 22.04 LTS (recommended) or Oracle Linux 8
- **Network**: Public IP with firewall rules configured

### Software Dependencies

- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl

## Oracle Cloud Setup

### 1. Create Compute Instance

1. Log in to Oracle Cloud Console
2. Navigate to **Compute** → **Instances**
3. Click **Create Instance**
4. Configure:
   - **Name**: capivara-bet-production
   - **Image**: Ubuntu 22.04 (Minimal)
   - **Shape**: VM.Standard.A1.Flex
   - **OCPUs**: 2
   - **Memory**: 12 GB
   - **Boot Volume**: 100 GB
5. Add SSH key for access
6. Click **Create**

### 2. Configure Network Security

1. Go to **Networking** → **Virtual Cloud Networks**
2. Select your VCN → Security Lists
3. Add Ingress Rules:

```
Port 22   (SSH)          - Source: Your IP/32
Port 80   (HTTP)         - Source: 0.0.0.0/0
Port 443  (HTTPS)        - Source: 0.0.0.0/0
Port 8000 (API)          - Source: 0.0.0.0/0
Port 8501 (Dashboard)    - Source: 0.0.0.0/0
```

### 3. Configure OS Firewall

The setup script will configure iptables automatically, but you can verify:

```bash
sudo iptables -L -n | grep -E '8000|8501'
```

## System Setup

### 1. Connect to Instance

```bash
ssh ubuntu@<instance-public-ip>
```

### 2. Run Setup Script

```bash
# Clone repository
git clone https://github.com/dans91364-create/capivara-bet-esports.git ~/capivara-bet
cd ~/capivara-bet

# Run Oracle setup script
./scripts/oracle_setup.sh
```

The setup script will:
- Install Docker and Docker Compose
- Configure firewall rules
- Create application directories
- Set up swap (if needed)
- Install system dependencies

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Required Configuration:**

```env
# Oracle Deployment
ORACLE_DEPLOYMENT=true

# Database
DATABASE_URL=postgresql://capivara:your_secure_password@db:5432/capivara_bet

# Telegram Notifications (optional but recommended)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
NOTIFY_ON_COLLECTION_COMPLETE=true
NOTIFY_ON_ERROR=true

# Collection Settings
COLLECTION_INTERVAL_HOURS=2
INITIAL_COLLECTION_DAYS=180
ENABLE_INITIAL_COLLECTION=true
```

**Optional Optimization:**

```env
# Rate Limiting (adjust based on API responses)
TRADITIONAL_SPORTS_RATE_LIMIT=10
HLTV_RATE_LIMIT=5
VLR_RATE_LIMIT=5
SUPERBET_RATE_LIMIT=20

# Resource Limits
MAX_WORKERS=4
BATCH_SIZE=100
```

## Application Deployment

### Initial Deployment

```bash
cd ~/capivara-bet
./scripts/deploy.sh
```

The deploy script will:
1. Pull latest code changes
2. Stop existing containers
3. Build Docker images
4. Run database migrations
5. Start all services
6. Verify service health

### Services Started

- **PostgreSQL** (db): Port 5432
- **API** (api): Port 8000
- **Dashboard** (dashboard): Port 8501
- **Data Collector** (collector): Background service

### Verify Deployment

```bash
# Check all services are running
docker-compose -f docker-compose.oracle.yml ps

# Check health
curl http://localhost:8000/api/health

# Check metrics
curl http://localhost:8000/api/metrics

# Check collection status
curl http://localhost:8000/api/collection/status
```

## Configuration

### Collection Settings

The data collection system has two modes:

#### 1. Initial Collection (First Run)

- Runs automatically on first startup
- Collects historical data from last 180 days (configurable)
- Sources:
  - Scorealarm: NBA, Football, Tennis
  - HLTV: CS2 matches and rankings
  - VLR.gg: Valorant matches
  - OpenDota: Dota 2 pro matches
  - Superbet: Historical odds

#### 2. Periodic Collection (Continuous)

- Runs every 2 hours (configurable via `COLLECTION_INTERVAL_HOURS`)
- Collects only new data since last collection
- Prioritizes:
  1. Real-time odds (Superbet)
  2. Finished match results
  3. Ranking updates
  4. Player statistics

### Resource Optimization

The Docker Compose configuration is optimized for 12GB RAM:

- **PostgreSQL**: 4GB limit (2GB reserved)
- **API**: 2GB limit (1GB reserved)
- **Dashboard**: 1.5GB limit (512MB reserved)
- **Collector**: 3GB limit (1.5GB reserved)

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ORACLE_DEPLOYMENT` | false | Enable Oracle-specific optimizations |
| `COLLECTION_INTERVAL_HOURS` | 2 | Hours between periodic collections |
| `INITIAL_COLLECTION_DAYS` | 180 | Days of historical data to collect |
| `ENABLE_INITIAL_COLLECTION` | true | Run initial collection on first start |
| `TRADITIONAL_SPORTS_RATE_LIMIT` | 10 | Scorealarm API requests per minute |
| `HLTV_RATE_LIMIT` | 5 | HLTV requests per minute |
| `VLR_RATE_LIMIT` | 5 | VLR.gg requests per minute |
| `SUPERBET_RATE_LIMIT` | 20 | Superbet API requests per minute |
| `MAX_WORKERS` | 4 | Maximum concurrent workers |
| `BATCH_SIZE` | 100 | Database batch insert size |

## Monitoring

### View Logs

```bash
# All services
docker-compose -f docker-compose.oracle.yml logs -f

# Specific service
docker-compose -f docker-compose.oracle.yml logs -f collector
docker-compose -f docker-compose.oracle.yml logs -f api
docker-compose -f docker-compose.oracle.yml logs -f dashboard

# Last 100 lines
docker-compose -f docker-compose.oracle.yml logs --tail=100 collector
```

### Health Checks

```bash
# API health
curl http://localhost:8000/api/health

# System metrics
curl http://localhost:8000/api/metrics | jq

# Collection status
curl http://localhost:8000/api/collection/status | jq
```

### System Resources

```bash
# Check container resource usage
docker stats

# Check disk usage
df -h

# Check memory usage
free -h

# Check database size
docker exec capivara_db psql -U capivara -d capivara_bet -c "
  SELECT pg_size_pretty(pg_database_size('capivara_bet')) as size;
"
```

### Telegram Notifications

If configured, you'll receive notifications for:
- Initial collection complete
- Critical errors during collection
- Daily collection summaries (if enabled)

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
docker-compose -f docker-compose.oracle.yml logs [service_name]

# Check if port is already in use
sudo netstat -tulpn | grep -E '8000|8501|5432'

# Restart specific service
docker-compose -f docker-compose.oracle.yml restart [service_name]
```

### Database Connection Issues

```bash
# Check if database is running
docker exec capivara_db pg_isready -U capivara

# Check database logs
docker-compose -f docker-compose.oracle.yml logs db

# Recreate database
docker-compose -f docker-compose.oracle.yml down -v
docker-compose -f docker-compose.oracle.yml up -d
```

### Collection Not Running

```bash
# Check collector logs
docker-compose -f docker-compose.oracle.yml logs collector

# Check collection status via API
curl http://localhost:8000/api/collection/status

# Restart collector
docker-compose -f docker-compose.oracle.yml restart collector
```

### Out of Memory

```bash
# Check memory usage
free -h
docker stats

# Reduce resource limits in docker-compose.oracle.yml
# Reduce MAX_WORKERS and BATCH_SIZE in .env
```

### High CPU Usage

```bash
# Check which container is using CPU
docker stats

# Reduce collection frequency
# Edit .env: COLLECTION_INTERVAL_HOURS=4

# Reduce concurrent workers
# Edit .env: MAX_WORKERS=2
```

### Firewall Issues

```bash
# Check iptables rules
sudo iptables -L -n

# Re-run setup script to reconfigure
./scripts/oracle_setup.sh

# Or manually add rules
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8501 -j ACCEPT
```

## Maintenance

### Update Application

```bash
cd ~/capivara-bet
git pull origin main
./scripts/deploy.sh
```

### Backup Database

```bash
# Create backup
docker exec capivara_db pg_dump -U capivara capivara_bet > backup_$(date +%Y%m%d).sql

# Restore backup
docker exec -i capivara_db psql -U capivara capivara_bet < backup_20240101.sql
```

### Clean Up Logs

```bash
# Docker logs are automatically rotated (max 10MB, 3 files)
# To manually clean:
docker-compose -f docker-compose.oracle.yml down
rm -rf logs/*
docker-compose -f docker-compose.oracle.yml up -d
```

### Reset Collection Status

If you need to re-run initial collection:

```bash
# Connect to database
docker exec -it capivara_db psql -U capivara capivara_bet

# Delete collection records
DELETE FROM collection_status WHERE collection_type = 'initial';

# Exit
\q

# Restart collector
docker-compose -f docker-compose.oracle.yml restart collector
```

### Update Docker Images

```bash
cd ~/capivara-bet

# Rebuild images
docker-compose -f docker-compose.oracle.yml build --no-cache

# Restart services
docker-compose -f docker-compose.oracle.yml up -d
```

### Monitor Disk Space

```bash
# Check disk usage
df -h

# Clean Docker system
docker system prune -a --volumes

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

## Performance Tuning

### Database Optimization

The PostgreSQL configuration is already optimized for 12GB RAM. If you need to adjust:

Edit `docker-compose.oracle.yml` and modify PostgreSQL command parameters:

```yaml
command: >
  postgres
  -c shared_buffers=1GB          # 25% of RAM for DB
  -c effective_cache_size=3GB    # 75% of RAM for DB
  -c work_mem=16MB               # Per query memory
  -c maintenance_work_mem=256MB  # For maintenance ops
```

### Collection Tuning

Adjust based on your needs:

```env
# Less frequent collection (lower load)
COLLECTION_INTERVAL_HOURS=4

# More aggressive collection (higher load)
COLLECTION_INTERVAL_HOURS=1

# Reduce rate limits if APIs are rate-limiting
TRADITIONAL_SPORTS_RATE_LIMIT=5
HLTV_RATE_LIMIT=3

# Increase for faster collection (if APIs allow)
SUPERBET_RATE_LIMIT=30
```

## Security Best Practices

1. **Use strong database password** in `.env`
2. **Enable firewall** for non-essential ports
3. **Keep system updated**: `sudo apt update && sudo apt upgrade`
4. **Regular backups** of database
5. **Monitor logs** for suspicious activity
6. **Use SSH key authentication** (disable password auth)
7. **Limit SSH access** to known IPs

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review this documentation
- Check GitHub Issues
- Monitor system resources: `htop`, `docker stats`

## Additional Resources

- [Oracle Cloud Documentation](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
