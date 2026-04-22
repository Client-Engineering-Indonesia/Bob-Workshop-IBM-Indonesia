#!/bin/bash
# Complete working COBOL demo for Mandiri Bank presentation

echo "========================================="
echo "MANDIRI BANK - COBOL DEMO"
echo "========================================="
echo ""
echo "This demo shows a working COBOL banking system"
echo ""

# Step 1: Compile the demo program
echo "Step 1: Compiling COBOL program..."
cobc -x ACCTDEMO.CBL -o ACCTDEMO
if [ $? -ne 0 ]; then
    echo "✗ Compilation failed"
    exit 1
fi
echo "✓ ACCTDEMO compiled successfully"
echo ""

# Step 2: Set environment variable
echo "Step 2: Setting up environment..."
export ACCTMAST=../data/DEMO_ACCT.dat
echo "✓ Environment configured"
echo ""

# Step 3: Run the demo
echo "Step 3: Running COBOL Banking System..."
echo ""
./ACCTDEMO

echo ""
echo "========================================="
echo "DEMO EXPLANATION:"
echo "========================================="
echo "What you just saw:"
echo "1. COBOL program created 3 bank accounts"
echo "2. Stored them in an indexed file"
echo "3. Retrieved and displayed account details"
echo "4. Calculated total balances"
echo ""
echo "This demonstrates:"
echo "- Legacy COBOL file handling"
echo "- Banking business logic"
echo "- Data processing capabilities"
echo ""
echo "Next: Use Bob AI to analyze and modernize this code!"
echo "========================================="

