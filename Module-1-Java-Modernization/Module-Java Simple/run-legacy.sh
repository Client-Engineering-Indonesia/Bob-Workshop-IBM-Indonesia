#!/bin/bash

echo "=========================================="
echo "Running Legacy Banking Service Demo"
echo "=========================================="
echo ""
echo "Note: This will fail to connect to database (expected)"
echo "The purpose is to demonstrate the legacy code structure"
echo ""

cd legacy

# Compile
echo "Compiling legacy code..."
javac BankingService.java

# Run (will fail on DB connection, but shows the code execution)
echo ""
echo "Running legacy code..."
echo ""
java BankingService

cd ..

# Made with Bob
