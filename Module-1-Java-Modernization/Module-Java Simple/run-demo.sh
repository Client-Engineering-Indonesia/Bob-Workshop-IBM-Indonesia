#!/bin/bash

echo "=========================================="
echo "Java Modernization Demo"
echo "Legacy vs Modern Banking Service"
echo "=========================================="
echo ""

# Create proper directory structure for compilation
echo "Setting up compilation environment..."
mkdir -p build/legacy
mkdir -p build/modern

# Compile Legacy Code
echo ""
echo "1. Compiling LEGACY code (Java 6/7 style)..."
echo "   Location: legacy/BankingService.java"
cd legacy
javac -d ../build/legacy BankingService.java 2>&1
cd ..

if [ $? -eq 0 ]; then
    echo "   ✓ Legacy code compiled successfully"
    echo "   ⚠ Warnings about unsafe operations (expected for legacy code)"
else
    echo "   ✗ Legacy code compilation failed"
fi

# Try to run legacy code
echo ""
echo "2. Running LEGACY code..."
echo "   Note: Will fail on database connection (no DB configured)"
echo ""
cd build/legacy
java com.bsn.banking.legacy.BankingService 2>&1 | head -20
cd ../..

echo ""
echo "=========================================="
echo "Key Issues in Legacy Code:"
echo "=========================================="
echo "✗ Hardcoded database credentials (security risk)"
echo "✗ SQL injection vulnerabilities"
echo "✗ No transaction management"
echo "✗ Poor error handling (printStackTrace)"
echo "✗ No dependency injection"
echo "✗ Using obsolete APIs (Vector, Class.forName)"
echo "✗ Magic numbers and hardcoded values"
echo "✗ No separation of concerns"
echo "✗ Impossible to unit test"
echo ""

echo "=========================================="
echo "Modern Code Improvements:"
echo "=========================================="
echo "✓ Spring Boot 3 + Java 17"
echo "✓ Dependency injection"
echo "✓ Proper exception handling"
echo "✓ Transaction management (@Transactional)"
echo "✓ Input validation (Bean Validation)"
echo "✓ Modern Java features (Records, Sealed classes)"
echo "✓ Structured logging (SLF4J)"
echo "✓ DTOs for data transfer"
echo "✓ Repository pattern"
echo "✓ Testable code"
echo ""

echo "Note: Modern code requires Spring Boot runtime to execute"
echo "See DEMO-GUIDE.md for detailed comparison"
echo ""

# Made with Bob
