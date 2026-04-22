       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTDEMO.
      ******************************************************************
      * PROGRAM: ACCTDEMO - Account Management Demo                   *
      * PURPOSE: Demonstrate working COBOL banking operations         *
      * DESCRIPTION: Creates and displays account information         *
      ******************************************************************
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACCOUNT-FILE
               ASSIGN TO ACCTMAST
               ORGANIZATION IS INDEXED
               ACCESS MODE IS DYNAMIC
               RECORD KEY IS ACCT-NUMBER
               FILE STATUS IS WS-FILE-STATUS.
       
       DATA DIVISION.
       FILE SECTION.
       FD  ACCOUNT-FILE.
       01  ACCOUNT-RECORD.
           05  ACCT-NUMBER            PIC 9(12).
           05  ACCT-TYPE              PIC X(10).
           05  CUSTOMER-NAME          PIC X(50).
           05  ACCT-BALANCE           PIC 9(13)V99.
           05  ACCT-STATUS            PIC X(10).
           05  OPEN-DATE              PIC X(10).
           05  FILLER                 PIC X(393).
       
       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUS             PIC XX.
       01  WS-ACCOUNT-COUNT           PIC 9(04) VALUE ZERO.
       01  WS-TOTAL-BALANCE           PIC 9(15)V99 VALUE ZERO.
       01  WS-FORMATTED-BALANCE       PIC ZZZ,ZZZ,ZZZ,ZZ9.99.
       01  WS-FORMATTED-TOTAL         PIC Z,ZZZ,ZZZ,ZZZ,ZZ9.99.
       
       01  WS-DEMO-ACCOUNTS.
           05  DEMO-ACCT-1.
               10  D1-NUMBER          PIC 9(12) VALUE 100000000001.
               10  D1-TYPE            PIC X(10) VALUE 'SAVINGS   '.
               10  D1-NAME            PIC X(50)
                   VALUE 'BUDI SANTOSO                              '.
               10  D1-BALANCE         PIC 9(13)V99 VALUE 10000000.00.
               10  D1-STATUS          PIC X(10) VALUE 'ACTIVE    '.
               10  D1-DATE            PIC X(10) VALUE '2024-01-15'.
           05  DEMO-ACCT-2.
               10  D2-NUMBER          PIC 9(12) VALUE 100000000002.
               10  D2-TYPE            PIC X(10) VALUE 'CHECKING  '.
               10  D2-NAME            PIC X(50)
                   VALUE 'SITI RAHAYU                               '.
               10  D2-BALANCE         PIC 9(13)V99 VALUE 12500000.00.
               10  D2-STATUS          PIC X(10) VALUE 'ACTIVE    '.
               10  D2-DATE            PIC X(10) VALUE '2024-02-20'.
           05  DEMO-ACCT-3.
               10  D3-NUMBER          PIC 9(12) VALUE 100000000003.
               10  D3-TYPE            PIC X(10) VALUE 'SAVINGS   '.
               10  D3-NAME            PIC X(50)
                   VALUE 'AHMAD WIJAYA                              '.
               10  D3-BALANCE         PIC 9(13)V99 VALUE 25000000.00.
               10  D3-STATUS          PIC X(10) VALUE 'ACTIVE    '.
               10  D3-DATE            PIC X(10) VALUE '2024-03-10'.
           05  DEMO-ACCT-4.
               10  D4-NUMBER          PIC 9(12) VALUE 100000000004.
               10  D4-TYPE            PIC X(10) VALUE 'CHECKING  '.
               10  D4-NAME            PIC X(50)
                   VALUE 'DEWI LESTARI                              '.
               10  D4-BALANCE         PIC 9(13)V99 VALUE 8000000.00.
               10  D4-STATUS          PIC X(10) VALUE 'ACTIVE    '.
               10  D4-DATE            PIC X(10) VALUE '2024-04-15'.
           05  DEMO-ACCT-5.
               10  D5-NUMBER          PIC 9(12) VALUE 100000000006.
               10  D5-TYPE            PIC X(10) VALUE 'SAVINGS   '.
               10  D5-NAME            PIC X(50)
                   VALUE 'FADLY HIDAYAT                             '.
               10  D5-BALANCE         PIC 9(13)V99 VALUE 19000000.00.
               10  D5-STATUS          PIC X(10) VALUE 'ACTIVE    '.
               10  D5-DATE            PIC X(10) VALUE '2024-05-20'.
       
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           DISPLAY "========================================="
           DISPLAY "MANDIRI BANK - ACCOUNT MANAGEMENT SYSTEM"
           DISPLAY "========================================="
           DISPLAY " "
           
           PERFORM INITIALIZE-FILES
           PERFORM CREATE-DEMO-ACCOUNTS
           PERFORM DISPLAY-ALL-ACCOUNTS
           PERFORM CALCULATE-TOTALS
           PERFORM CLEANUP
           
           DISPLAY " "
           DISPLAY "========================================="
           DISPLAY "DEMO COMPLETED SUCCESSFULLY"
           DISPLAY "========================================="
           STOP RUN.
       
       INITIALIZE-FILES.
           DISPLAY "Initializing account file..."
           OPEN OUTPUT ACCOUNT-FILE
           IF WS-FILE-STATUS NOT = "00"
               DISPLAY "Creating new account file..."
           END-IF
           CLOSE ACCOUNT-FILE
           DISPLAY "✓ Account file ready"
           DISPLAY " ".
       
       CREATE-DEMO-ACCOUNTS.
           DISPLAY "Creating demo accounts..."
           OPEN I-O ACCOUNT-FILE
           
      *    CREATE ACCOUNT 1
           MOVE D1-NUMBER TO ACCT-NUMBER
           MOVE D1-TYPE TO ACCT-TYPE
           MOVE D1-NAME TO CUSTOMER-NAME
           MOVE D1-BALANCE TO ACCT-BALANCE
           MOVE D1-STATUS TO ACCT-STATUS
           MOVE D1-DATE TO OPEN-DATE
           WRITE ACCOUNT-RECORD
           DISPLAY "✓ Created account: " ACCT-NUMBER
           
      *    CREATE ACCOUNT 2
           MOVE D2-NUMBER TO ACCT-NUMBER
           MOVE D2-TYPE TO ACCT-TYPE
           MOVE D2-NAME TO CUSTOMER-NAME
           MOVE D2-BALANCE TO ACCT-BALANCE
           MOVE D2-STATUS TO ACCT-STATUS
           MOVE D2-DATE TO OPEN-DATE
           WRITE ACCOUNT-RECORD
           DISPLAY "✓ Created account: " ACCT-NUMBER
           
      *    CREATE ACCOUNT 3
           MOVE D3-NUMBER TO ACCT-NUMBER
           MOVE D3-TYPE TO ACCT-TYPE
           MOVE D3-NAME TO CUSTOMER-NAME
           MOVE D3-BALANCE TO ACCT-BALANCE
           MOVE D3-STATUS TO ACCT-STATUS
           MOVE D3-DATE TO OPEN-DATE
           WRITE ACCOUNT-RECORD
           DISPLAY "✓ Created account: " ACCT-NUMBER
           
           MOVE D4-NUMBER TO ACCT-NUMBER
           MOVE D4-TYPE TO ACCT-TYPE
           MOVE D4-NAME TO CUSTOMER-NAME
           MOVE D4-BALANCE TO ACCT-BALANCE
           MOVE D4-STATUS TO ACCT-STATUS
           MOVE D4-DATE TO OPEN-DATE
           WRITE ACCOUNT-RECORD
           DISPLAY "✓ Created account: " ACCT-NUMBER
           
           MOVE D5-NUMBER TO ACCT-NUMBER
           MOVE D5-TYPE TO ACCT-TYPE
           MOVE D5-NAME TO CUSTOMER-NAME
           MOVE D5-BALANCE TO ACCT-BALANCE
           MOVE D5-STATUS TO ACCT-STATUS
           MOVE D5-DATE TO OPEN-DATE
           WRITE ACCOUNT-RECORD
           DISPLAY "✓ Created account: " ACCT-NUMBER
           
           CLOSE ACCOUNT-FILE
           DISPLAY " ".
       
       DISPLAY-ALL-ACCOUNTS.
           DISPLAY "========================================="
           DISPLAY "ACCOUNT LISTING"
           DISPLAY "========================================="
           DISPLAY " "
           
           OPEN INPUT ACCOUNT-FILE
           
           MOVE D1-NUMBER TO ACCT-NUMBER
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY "Error reading account"
               NOT INVALID KEY
                   PERFORM DISPLAY-ACCOUNT-DETAIL
           END-READ
           
           MOVE D2-NUMBER TO ACCT-NUMBER
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY "Error reading account"
               NOT INVALID KEY
                   PERFORM DISPLAY-ACCOUNT-DETAIL
           END-READ
           
           MOVE D3-NUMBER TO ACCT-NUMBER
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY "Error reading account"
               NOT INVALID KEY
                   PERFORM DISPLAY-ACCOUNT-DETAIL
           END-READ
           
           MOVE D4-NUMBER TO ACCT-NUMBER
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY "Error reading account"
               NOT INVALID KEY
                   PERFORM DISPLAY-ACCOUNT-DETAIL
           END-READ
           
           MOVE D5-NUMBER TO ACCT-NUMBER
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY "Error reading account"
               NOT INVALID KEY
                   PERFORM DISPLAY-ACCOUNT-DETAIL
           END-READ
           
           CLOSE ACCOUNT-FILE.
       
       DISPLAY-ACCOUNT-DETAIL.
           ADD 1 TO WS-ACCOUNT-COUNT
           ADD ACCT-BALANCE TO WS-TOTAL-BALANCE
           
           MOVE ACCT-BALANCE TO WS-FORMATTED-BALANCE
           
           DISPLAY "Account #: " ACCT-NUMBER
           DISPLAY "  Type    : " ACCT-TYPE
           DISPLAY "  Customer: " CUSTOMER-NAME
           DISPLAY "  Balance : Rp " WS-FORMATTED-BALANCE
           DISPLAY "  Status  : " ACCT-STATUS
           DISPLAY "  Opened  : " OPEN-DATE
           DISPLAY " ".
       
       CALCULATE-TOTALS.
           MOVE WS-TOTAL-BALANCE TO WS-FORMATTED-TOTAL
           DISPLAY "========================================="
           DISPLAY "SUMMARY"
           DISPLAY "========================================="
           DISPLAY "Total Accounts: " WS-ACCOUNT-COUNT
           DISPLAY "Total Balance : Rp " WS-FORMATTED-TOTAL
           DISPLAY " ".
       
       CLEANUP.
           DISPLAY "Cleaning up...".

