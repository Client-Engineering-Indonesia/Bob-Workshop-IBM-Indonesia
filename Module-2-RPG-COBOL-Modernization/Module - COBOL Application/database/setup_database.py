#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for COBOL Banking System
Connects to PostgreSQL and executes the setup SQL script
"""

import psycopg2
from psycopg2 import sql
import sys

# Database connection parameters
DB_CONFIG = {
    'host': '52.118.151.212',
    'port': 8080,
    'database': 'postgres123',
    'user': 'postgres123',
    'password': 'postgres123'
}

def main():
    print("=" * 60)
    print("COBOL BANKING SYSTEM - DATABASE SETUP")
    print("=" * 60)
    print(f"Connecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Database: {DB_CONFIG['database']}")
    print()
    
    try:
        # Connect to PostgreSQL
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✓ Connected successfully!")
        print()
        
        # Read SQL file
        print("Reading SQL setup script...")
        with open('00_setup_postgres.sql', 'r') as f:
            sql_script = f.read()
        print("✓ SQL script loaded")
        print()
        
        # Execute SQL script
        print("Executing SQL script...")
        print("-" * 60)
        cursor.execute(sql_script)
        print("-" * 60)
        print("✓ SQL script executed successfully!")
        print()
        
        # Verify data
        print("Verifying data insertion...")
        cursor.execute("""
            SELECT 'CUSTOMERS' AS TABLE_NAME, COUNT(*) AS RECORD_COUNT 
            FROM COBOL.CUSTOMER
            UNION ALL
            SELECT 'ACCOUNTS', COUNT(*) FROM COBOL.ACCOUNT
            UNION ALL
            SELECT 'TRANSACTIONS', COUNT(*) FROM COBOL.TRANSACTION
            UNION ALL
            SELECT 'LOANS', COUNT(*) FROM COBOL.LOAN
        """)
        
        results = cursor.fetchall()
        print()
        print("Data Verification:")
        print("-" * 40)
        for table_name, count in results:
            print(f"  {table_name:15} : {count:5} records")
        print("-" * 40)
        print()
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("=" * 60)
        print("DATABASE SETUP COMPLETE!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Verify tables in your PostgreSQL client")
        print("2. Run COBOL programs to test connectivity")
        print("3. Use Bob to analyze the COBOL code")
        print()
        
        return 0
        
    except psycopg2.Error as e:
        print()
        print("=" * 60)
        print("DATABASE ERROR!")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check if PostgreSQL server is running")
        print("2. Verify connection details:")
        print(f"   Host: {DB_CONFIG['host']}")
        print(f"   Port: {DB_CONFIG['port']}")
        print(f"   Database: {DB_CONFIG['database']}")
        print(f"   User: {DB_CONFIG['user']}")
        print("3. Check firewall settings")
        print("4. Verify user permissions")
        print()
        return 1
        
    except FileNotFoundError:
        print()
        print("=" * 60)
        print("FILE NOT FOUND!")
        print("=" * 60)
        print("Error: 00_setup_postgres.sql not found")
        print("Make sure you're running this script from the database/ directory")
        print()
        return 1
        
    except Exception as e:
        print()
        print("=" * 60)
        print("UNEXPECTED ERROR!")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
