from flask import Flask, render_template, request, jsonify
import subprocess
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': '52.118.151.212',
    'port': 8080,
    'database': 'postgres123',
    'user': 'postgres123',
    'password': 'postgres123'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def try_run_cobol_program(program_name, operation, params):
    """
    Attempt to run actual COBOL program
    Returns: (success, output, error)
    """
    try:
        # Set environment variables for COBOL file access
        env = os.environ.copy()
        env['ACCTMAST'] = '../data/ACCTMAST.dat'
        env['CUSTMAST'] = '../data/CUSTMAST.dat'
        
        # Try to execute the compiled COBOL program
        cobol_path = f'../programs/{program_name}'
        
        if not os.path.exists(cobol_path):
            return False, None, f"COBOL program {program_name} not compiled"
        
        # Run the COBOL program
        result = subprocess.run(
            [cobol_path],
            env=env,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return True, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return False, None, "COBOL program timeout"
    except Exception as e:
        return False, None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.account_number, a.customer_id, a.account_type,
                   a.account_balance, a.account_status, a.account_open_date,
                   c.full_name
            FROM COBOL.ACCOUNT a
            LEFT JOIN COBOL.CUSTOMER c ON a.customer_id = c.customer_id
            ORDER BY a.account_number
        """)
        
        accounts = []
        for row in cursor.fetchall():
            accounts.append({
                'account_number': row[0],
                'customer_id': row[1],
                'account_type': row[2],
                'balance': float(row[3]),
                'status': row[4],
                'open_date': row[5].strftime('%Y-%m-%d') if row[5] else None,
                'customer_name': row[6] if row[6] else 'Unknown'
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': accounts,
            'source': 'PostgreSQL Database'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/customer/create', methods=['POST'])
def create_customer():
    """Create new customer"""
    data = request.json
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate customer ID (10-digit number)
        cursor.execute("SELECT MAX(customer_id) FROM COBOL.CUSTOMER")
        result = cursor.fetchone()
        
        if result is None or result[0] is None:
            new_customer_id = 1234567890
        else:
            new_customer_id = result[0] + 1
        
        # Insert customer
        cursor.execute("""
            INSERT INTO COBOL.CUSTOMER
            (customer_id, title, first_name, last_name, full_name,
             date_of_birth, gender, nationality, id_type, id_number,
             mobile_phone, email, customer_since, customer_status,
             customer_segment, kyc_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            new_customer_id,
            data.get('title', 'Mr.'),
            data['first_name'],
            data['last_name'],
            f"{data['first_name']} {data['last_name']}",
            data.get('date_of_birth'),
            data.get('gender', 'M'),
            'IDN',
            'KTP',
            data.get('id_number', ''),
            data.get('mobile_phone', ''),
            data.get('email', ''),
            datetime.now().date(),
            'A',
            'RET',
            'C'
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'customer_id': new_customer_id,
            'full_name': f"{data['first_name']} {data['last_name']}",
            'message': 'Customer created successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/create', methods=['POST'])
def create_account():
    """Create new account - tries COBOL first, falls back to Python"""
    data = request.json
    
    # Try to run actual COBOL program
    cobol_success, cobol_output, cobol_error = try_run_cobol_program(
        'ACCTMGMT', 'CREATE', data
    )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate account number (numeric, not string)
        cursor.execute("SELECT MAX(account_number) FROM COBOL.ACCOUNT")
        result = cursor.fetchone()
        
        # Handle the result properly
        if result is None or result[0] is None:
            # No accounts exist yet, start with 1000000001
            new_acct_number = 1000000001
        else:
            # Increment the max account number
            max_acct = result[0]
            new_acct_number = max_acct + 1
        
        # Convert customer_id to integer if it's a string
        customer_id = data['customer_id']
        if isinstance(customer_id, str):
            # Remove any non-numeric characters and convert to int
            customer_id = int(''.join(filter(str.isdigit, customer_id)))
        
        # Insert account
        cursor.execute("""
            INSERT INTO COBOL.ACCOUNT
            (account_number, customer_id, account_type, account_balance,
             account_status, account_open_date, currency_code, branch_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            new_acct_number,
            customer_id,
            data['account_type'],
            data.get('initial_balance', 0),
            'A',
            datetime.now().date(),
            'IDR',
            1001
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'account_number': new_acct_number,
            'cobol_attempted': cobol_success,
            'cobol_output': cobol_output if cobol_success else None,
            'cobol_error': cobol_error if not cobol_success else None,
            'implementation': 'Python (COBOL business logic)',
            'message': 'Account created successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transaction/deposit', methods=['POST'])
def deposit():
    """Process deposit transaction"""
    data = request.json
    
    # Try COBOL first
    cobol_success, cobol_output, cobol_error = try_run_cobol_program(
        'TRANPROC', 'DEPOSIT', data
    )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current balance
        cursor.execute("""
            SELECT account_balance FROM COBOL.ACCOUNT
            WHERE account_number = %s
        """, (data['account_number'],))
        
        result = cursor.fetchone()
        if not result:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        old_balance = result[0]
        new_balance = old_balance + data['amount']
        
        # Generate transaction ID
        trans_id = f"TRX{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Insert transaction
        cursor.execute("""
            INSERT INTO COBOL.TRANSACTION 
            (transaction_id, account_number, transaction_type, 
             amount, transaction_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (trans_id, data['account_number'], 'DEPOSIT',
              data['amount'], datetime.now(), 'COMPLETED'))
        
        # Update balance
        cursor.execute("""
            UPDATE COBOL.ACCOUNT
            SET account_balance = %s, last_transaction_date = %s
            WHERE account_number = %s
        """, (new_balance, datetime.now(), data['account_number']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'transaction_id': trans_id,
            'old_balance': float(old_balance),
            'new_balance': float(new_balance),
            'cobol_attempted': cobol_success,
            'implementation': 'Python (COBOL business logic)',
            'message': 'Deposit successful'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transaction/withdraw', methods=['POST'])
def withdraw():
    """Process withdrawal transaction"""
    data = request.json
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current balance
        cursor.execute("""
            SELECT account_balance FROM COBOL.ACCOUNT
            WHERE account_number = %s
        """, (data['account_number'],))
        
        result = cursor.fetchone()
        if not result:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        old_balance = result[0]
        
        if old_balance < data['amount']:
            return jsonify({
                'success': False, 
                'error': 'Insufficient funds'
            }), 400
        
        new_balance = old_balance - data['amount']
        
        # Generate transaction ID
        trans_id = f"TRX{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Insert transaction
        cursor.execute("""
            INSERT INTO COBOL.TRANSACTION 
            (transaction_id, account_number, transaction_type, 
             amount, transaction_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (trans_id, data['account_number'], 'WITHDRAWAL',
              data['amount'], datetime.now(), 'COMPLETED'))
        
        # Update balance
        cursor.execute("""
            UPDATE COBOL.ACCOUNT
            SET account_balance = %s, last_transaction_date = %s
            WHERE account_number = %s
        """, (new_balance, datetime.now(), data['account_number']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'transaction_id': trans_id,
            'old_balance': float(old_balance),
            'new_balance': float(new_balance),
            'implementation': 'Python (COBOL business logic)',
            'message': 'Withdrawal successful'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get all customers"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT customer_id, full_name, id_number,
                   mobile_phone, email, kyc_status
            FROM COBOL.CUSTOMER
            ORDER BY customer_id
        """)
        
        customers = []
        for row in cursor.fetchall():
            customers.append({
                'customer_id': row[0],
                'customer_name': row[1],
                'id_number': row[2],
                'phone_number': row[3],
                'email': row[4],
                'kyc_status': row[5]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': customers})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cobol/status', methods=['GET'])
def cobol_status():
    """Check COBOL programs compilation status"""
    programs = ['ACCTMGMT', 'TRANPROC', 'CUSTINFO', 'LOANPROC', 'ACCTDEMO']
    status = {}
    
    for prog in programs:
        path = f'../programs/{prog}'
        status[prog] = {
            'compiled': os.path.exists(path),
            'path': path
        }
    
    return jsonify({
        'success': True,
        'programs': status,
        'note': 'COBOL programs with EXEC SQL require ECPG precompiler'
    })

if __name__ == '__main__':
    app.run(debug=True, port=8443)

# Made with Bob
