#!/bin/bash

# Development script to run both backend and frontend

echo "🚀 Starting Capivara Bet Development Servers..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if running in root directory
if [ ! -d "api" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Start backend API
echo "📡 Starting FastAPI backend on http://localhost:8000..."
cd "$(dirname "$0")/.."
uvicorn api.main:app --reload --port 8000 &
API_PID=$!

# Wait a bit for API to start
sleep 3

# Start frontend
echo "🎨 Starting Next.js frontend on http://localhost:3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development servers started!"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for processes
wait
