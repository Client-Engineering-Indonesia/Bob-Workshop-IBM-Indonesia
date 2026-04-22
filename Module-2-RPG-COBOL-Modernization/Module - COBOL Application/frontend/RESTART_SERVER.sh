#!/bin/bash

# Script to restart the Flask server

echo "Stopping any running Flask servers..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

echo "Starting Flask server..."
cd "$(dirname "$0")"
source venv/bin/activate
python app.py

# Made with Bob
