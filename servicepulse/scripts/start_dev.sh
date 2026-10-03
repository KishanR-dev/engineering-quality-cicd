#!/bin/bash
# ServicePulse development server startup script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Starting ServicePulse development server..."

# Check for Python
if ! command -v python &> /dev/null; then
    echo "ERROR: Python 3.12+ is required"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "WARNING: .env file not found. Copying .env.example..."
    cp .env.example .env
fi

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    python -m pip install --quiet -r requirements.txt
fi

# Run the server
echo "Starting uvicorn on http://0.0.0.0:8000"
echo "API docs at http://localhost:8000/api/v1/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 "$@"
