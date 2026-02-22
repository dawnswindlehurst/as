.PHONY: help install dev api frontend docker-up docker-down clean

help:
@echo "Capivara Bet - Development Commands"
@echo "===================================="
@echo "make install      - Install all dependencies"
@echo "make dev          - Run both API and frontend in development mode"
@echo "make api          - Run only the FastAPI backend"
@echo "make frontend     - Run only the Next.js frontend"
@echo "make docker-up    - Start all services with Docker Compose"
@echo "make docker-down  - Stop all Docker services"
@echo "make clean        - Clean build artifacts"

install:
@echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
@echo "📦 Installing frontend dependencies..."
cd frontend && npm install
@echo "✅ All dependencies installed!"

dev:
@echo "🚀 Starting development servers..."
./scripts/dev.sh

api:
@echo "📡 Starting FastAPI backend..."
uvicorn api.main:app --reload --port 8000

frontend:
@echo "🎨 Starting Next.js frontend..."
cd frontend && npm run dev

docker-up:
@echo "🐳 Starting Docker services..."
docker-compose up -d
@echo "✅ Services started!"
@echo "   API: http://localhost:8000"
@echo "   Frontend: http://localhost:3000"

docker-down:
@echo "🛑 Stopping Docker services..."
docker-compose down

clean:
@echo "🧹 Cleaning build artifacts..."
rm -rf frontend/.next
rm -rf frontend/node_modules
rm -rf **/__pycache__
rm -rf *.pyc
@echo "✅ Clean complete!"
