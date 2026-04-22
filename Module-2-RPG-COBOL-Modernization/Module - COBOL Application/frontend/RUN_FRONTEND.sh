#!/bin/bash
# Run the banking system frontend

echo "========================================="
echo "MANDIRI BANK - COBOL BANKING FRONTEND"
echo "========================================="
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    echo ""
fi

echo "Starting Flask web server..."
echo ""
echo "The frontend will be available at:"
echo "  http://localhost:5000"
echo ""
echo "Features:"
echo "  ✓ View all accounts from PostgreSQL"
echo "  ✓ Create new accounts (COBOL business logic)"
echo "  ✓ Process deposits (COBOL business logic)"
echo "  ✓ Process withdrawals (COBOL business logic)"
echo "  ✓ Attempts to run actual COBOL programs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

python3 app.py

# Made with Bob
