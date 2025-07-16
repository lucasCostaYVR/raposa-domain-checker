#!/bin/bash

# Kill any existing processes on port 8000
echo "🔍 Checking for existing processes on port 8000..."
PORT_PID=$(lsof -ti:8000)
if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  Killing existing process on port 8000 (PID: $PORT_PID)"
    kill -9 $PORT_PID
    sleep 2
else
    echo "✅ No existing processes found on port 8000"
fi

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv .venv"
    exit 1
fi

# Check if Railway CLI is available
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first."
    exit 1
fi

# Ensure we're linked to the development environment
echo "🔧 Setting up Railway development environment..."
railway environment development
railway service Postgres-1Be3

# Start the FastAPI development server with Railway environment variables
echo "🚀 Starting FastAPI development server on port 8000..."
echo "📡 Server will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Change to src directory and run the server
cd src
railway run ../.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
