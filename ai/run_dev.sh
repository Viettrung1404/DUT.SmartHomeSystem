#!/bin/bash
# Development server startup script

echo "🚀 Starting Vietnamese NLP Intent Classification Server (Development Mode)..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Run the server with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
