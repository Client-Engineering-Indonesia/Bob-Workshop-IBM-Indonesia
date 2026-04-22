#!/bin/bash

# Script to clear Python cache and restart Flask server

echo "Stopping any running Flask servers..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

echo "Clearing Python cache..."
cd "$(dirname "$0")"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "Starting Flask server with fresh cache..."
source venv/bin/activate
python app.py

# Made with Bob
