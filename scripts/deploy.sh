#!/bin/bash
set -e

echo "=========================================="
echo "Capivara Bet - Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.oracle.yml"
ENV_FILE=".env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create a .env file from .env.example"
    exit 1
fi

echo -e "${GREEN}[1/6] Pulling latest changes...${NC}"
if [ -d .git ]; then
    git pull origin main || echo -e "${YELLOW}Warning: Could not pull latest changes${NC}"
else
    echo "Not a git repository, skipping..."
fi

echo -e "${GREEN}[2/6] Stopping existing containers...${NC}"
docker-compose -f $COMPOSE_FILE down || true

echo -e "${GREEN}[3/6] Building Docker images...${NC}"
docker-compose -f $COMPOSE_FILE build --no-cache

echo -e "${GREEN}[4/6] Running database migrations...${NC}"
# Create tables if they don't exist
docker-compose -f $COMPOSE_FILE run --rm api python -c "
from database.db import engine, Base
Base.metadata.create_all(bind=engine)
print('Database tables created/updated')
" || echo -e "${YELLOW}Warning: Migration may have failed${NC}"

echo -e "${GREEN}[5/6] Starting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

echo -e "${GREEN}[6/6] Verifying service health...${NC}"
sleep 10

# Check if services are running
services=("db" "api" "dashboard" "collector")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose -f $COMPOSE_FILE ps | grep -q "${service}.*Up"; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is not running${NC}"
        all_healthy=false
    fi
done

echo ""
if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}=========================================="
    echo "Deployment Successful!"
    echo "==========================================${NC}"
    echo ""
    echo "Services are running:"
    echo "  - API: http://localhost:8000"
    echo "  - Dashboard: http://localhost:8501"
    echo "  - Database: localhost:5432"
    echo ""
    echo "To view logs:"
    echo "  docker-compose -f $COMPOSE_FILE logs -f [service_name]"
    echo ""
    echo "To check health:"
    echo "  curl http://localhost:8000/api/health"
    echo "  curl http://localhost:8000/api/metrics"
else
    echo -e "${RED}=========================================="
    echo "Deployment completed with warnings"
    echo "==========================================${NC}"
    echo ""
    echo "Some services failed to start. Check logs with:"
    echo "  docker-compose -f $COMPOSE_FILE logs"
fi
