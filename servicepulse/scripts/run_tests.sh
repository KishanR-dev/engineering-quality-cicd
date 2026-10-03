#!/bin/bash
# ServicePulse test runner script
# Used by CI/CD (Project 2) and local development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Running ServicePulse test suite..."

# Install dependencies if needed
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install --quiet -r requirements.txt
fi

# Run tests with coverage
pytest \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=xml:coverage.xml \
    -v \
    "$@"

echo "Test suite completed successfully."
