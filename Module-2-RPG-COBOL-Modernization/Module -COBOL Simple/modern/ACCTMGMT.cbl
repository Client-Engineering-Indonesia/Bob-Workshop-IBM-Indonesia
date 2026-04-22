       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTMGMT.
       AUTHOR. MODERN-DEVELOPER.
      *****************************************************************
      * MODERN ACCOUNT MANAGEMENT PROGRAM                             *
      * WRITTEN IN MODERN COBOL STYLE (COBOL 2014+)                  *
      * DEMONSTRATES BEST PRACTICES AND MODERN PATTERNS               *
      *                                                               *
      * IMPROVEMENTS DEMONSTRATED:                                    *
      * - STRUCTURED PROGRAMMING (NO GOTO)                           *
      * - PROPER MODULARIZATION                                      *
      * - NAMED CONSTANTS                                            *
      * - COMPREHENSIVE ERROR HANDLING                               *
      * - SEPARATION OF CONCERNS                                     *
      * - MEANINGFUL VARIABLE NAMES                                  *
      * - EXTENSIVE DOCUMENTATION                                    *
      * - VALIDATION AND BUSINESS RULES                              *
      * - TRANSACTION MANAGEMENT PATTERN                             *
      *****************************************************************
       
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       REPOSITORY.
           FUNCTION ALL INTRINSIC.
       
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACCOUNT-FILE ASSIGN TO 'ACCOUNT.DAT'
               ORGANIZATION IS INDEXED
               ACCESS MODE IS DYNAMIC
               RECORD KEY IS ACCT-NUMBER
               FILE STATUS IS FILE-STATUS-ACCOUNT.
           
           SELECT TRANSACTION-LOG ASSIGN TO 'TRANSLOG.DAT'
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE IS SEQUENTIAL
               FILE STATUS IS FILE-STATUS-TRANS.
           
           SELECT AUDIT-LOG ASSIGN TO 'AUDIT.DAT'
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE IS SEQUENTIAL
               FILE STATUS IS FILE-STATUS-AUDIT.
       
       DATA DIVISION.
       FILE SECTION.
       FD  ACCOUNT-FILE.
       01  ACCOUNT-RECORD.
           05  ACCT-NUMBER             PIC X(10).
           05  CUSTOMER-NAME           PIC X(50).
           05  ACCOUNT-TYPE            PIC X(01).
               88  SAVINGS-ACCOUNT     VALUE 'S'.
               88  CHECKING-ACCOUNT    VALUE 'C'.
               88  FIXED-DEPOSIT       VALUE 'F'.
           05  ACCOUNT-BALANCE         PIC 9(13)V99.
           05  ACCOUNT-STATUS          PIC X(01).
               88  ACTIVE-ACCOUNT      VALUE 'A'.
               88  INACTIVE-ACCOUNT    VALUE 'I'.
               88  CLOSED-ACCOUNT      VALUE 'C'.
           05  OPENING-DATE            PIC X(10).
           05  LAST-TRANSACTION-DATE   PIC X(10).
           05  INTEREST-RATE           PIC 9(02)V9(4).
           05  CUSTOMER-ID             PIC X(15).
           05  BRANCH-CODE             PIC X(05).
       
       FD  TRANSACTION-LOG.
       01  TRANSACTION-RECORD.
           05  TRANS-ID                PIC X(20).
           05  TRANS-ACCOUNT-NUMBER    PIC X(10).
           05  TRANS-TYPE              PIC X(01).
               88  TRANS-DEPOSIT       VALUE 'D'.
               88  TRANS-WITHDRAWAL    VALUE 'W'.
               88  TRANS-TRANSFER-OUT  VALUE 'T'.
               88  TRANS-TRANSFER-IN   VALUE 'R'.
               88  TRANS-INTEREST      VALUE 'I'.
           05  TRANS-AMOUNT            PIC 9(13)V99.
           05  TRANS-TIMESTAMP         PIC X(26).
           05  TRANS-STATUS            PIC X(01).
               88  TRANS-SUCCESS       VALUE 'S'.
               88  TRANS-FAILED        VALUE 'F'.
               88  TRANS-PENDING       VALUE 'P'.
           05  TRANS-DESCRIPTION       PIC X(100).
       
       FD  AUDIT-LOG.
       01  AUDIT-RECORD.
           05  AUDIT-TIMESTAMP         PIC X(26).
           05  AUDIT-USER-ID           PIC X(10).
           05  AUDIT-ACTION            PIC X(20).
           05  AUDIT-ACCOUNT           PIC X(10).
           05  AUDIT-DETAILS           PIC X(200).
       
       WORKING-STORAGE SECTION.
      *****************************************************************
      * FILE STATUS CODES                                             *
      *****************************************************************
       01  FILE-STATUS-ACCOUNT         PIC XX.
           88  FILE-SUCCESS            VALUE '00'.
           88  FILE-NOT-FOUND          VALUE '23'.
           88  FILE-DUPLICATE          VALUE '22'.
       
       01  FILE-STATUS-TRANS           PIC XX.
       01  FILE-STATUS-AUDIT           PIC XX.
       
      *****************************************************************
      * BUSINESS CONSTANTS - EXTERNALIZED CONFIGURATION              *
      *****************************************************************
       01  BUSINESS-CONSTANTS.
           05  MAX-TRANSFER-AMOUNT     PIC 9(13)V99 VALUE 100000000.00.
           05  MIN-OPENING-BALANCE     PIC 9(13)V99 VALUE 100000.00.
           05  MAX-DAILY-WITHDRAWAL    PIC 9(13)V99 VALUE 50000000.00.
           05  SAVINGS-INTEREST-RATE   PIC 9(02)V9(4) VALUE 05.2500.
           05  CHECKING-INTEREST-RATE  PIC 9(02)V9(4) VALUE 02.0000.
           05  ACCOUNT-NUMBER-LENGTH   PIC 99 VALUE 10.
       
      *****************************************************************
      * ERROR CODES AND MESSAGES                                      *
      *****************************************************************
       01  ERROR-HANDLING.
           05  ERROR-CODE              PIC X(05).
           05  ERROR-MESSAGE           PIC X(100).
           05  ERROR-OCCURRED          PIC X VALUE 'N'.
               88  NO-ERROR            VALUE 'N'.
               88  ERROR-FOUND         VALUE 'Y'.
       
       01  ERROR-CODES.
           05  ERR-ACCOUNT-NOT-FOUND   PIC X(05) VALUE 'E0001'.
           05  ERR-INSUFFICIENT-FUNDS  PIC X(05) VALUE 'E0002'.
           05  ERR-INVALID-AMOUNT      PIC X(05) VALUE 'E0003'.
           05  ERR-ACCOUNT-INACTIVE    PIC X(05) VALUE 'E0004'.
           05  ERR-DUPLICATE-ACCOUNT   PIC X(05) VALUE 'E0005'.
           05  ERR-INVALID-ACCOUNT-NUM PIC X(05) VALUE 'E0006'.
           05  ERR-TRANSFER-LIMIT      PIC X(05) VALUE 'E0007'.
           05  ERR-FILE-ERROR          PIC X(05) VALUE 'E0008'.
       
      *****************************************************************
      * WORKING VARIABLES WITH MEANINGFUL NAMES                       *
      *****************************************************************
       01  WORK-VARIABLES.
           05  CURRENT-DATE-TIME       PIC X(26).
           05  CURRENT-USER-ID         PIC X(10) VALUE 'SYSTEM'.
           05  TRANSACTION-ID          PIC X(20).
           05  MENU-CHOICE             PIC 9.
           05  CONTINUE-FLAG           PIC X VALUE 'Y'.
               88  CONTINUE-PROCESSING VALUE 'Y'.
               88  EXIT-PROCESSING     VALUE 'N'.
       
      *****************************************************************
      * INPUT/OUTPUT VARIABLES                                         *
      *****************************************************************
       01  INPUT-VARIABLES.
           05  INPUT-ACCOUNT-NUMBER    PIC X(10).
           05  INPUT-CUSTOMER-NAME     PIC X(50).
           05  INPUT-ACCOUNT-TYPE      PIC X(01).
           05  INPUT-AMOUNT            PIC 9(13)V99.
           05  INPUT-FROM-ACCOUNT      PIC X(10).
           05  INPUT-TO-ACCOUNT        PIC X(10).
           05  INPUT-CUSTOMER-ID       PIC X(15).
           05  INPUT-BRANCH-CODE       PIC X(05).
       
      *****************************************************************
      * TRANSACTION MANAGEMENT VARIABLES                               *
      *****************************************************************
       01  TRANSACTION-CONTROL.
           05  TRANS-IN-PROGRESS       PIC X VALUE 'N'.
               88  TRANSACTION-ACTIVE  VALUE 'Y'.
               88  NO-TRANSACTION      VALUE 'N'.
           05  ROLLBACK-REQUIRED       PIC X VALUE 'N'.
               88  NEED-ROLLBACK       VALUE 'Y'.
               88  NO-ROLLBACK         VALUE 'N'.
       
       PROCEDURE DIVISION.
      *****************************************************************
      * MAIN PROGRAM LOGIC - STRUCTURED APPROACH                      *
      *****************************************************************
       0000-MAIN-PROGRAM.
           PERFORM 1000-INITIALIZE-PROGRAM
           PERFORM 2000-PROCESS-MENU UNTIL EXIT-PROCESSING
           PERFORM 9000-TERMINATE-PROGRAM
           STOP RUN.
       
      *****************************************************************
      * INITIALIZATION SECTION                                         *
      *****************************************************************
       1000-INITIALIZE-PROGRAM.
           DISPLAY '========================================='
           DISPLAY 'MODERN ACCOUNT MANAGEMENT SYSTEM v2.0'
           DISPLAY 'BANK INDONESIA - CORE BANKING MODULE'
           DISPLAY '========================================='
           
           PERFORM 1100-OPEN-FILES
           PERFORM 1200-INITIALIZE-VARIABLES
           PERFORM 1300-LOG-SYSTEM-START.
       
       1100-OPEN-FILES.
           OPEN I-O ACCOUNT-FILE
           IF NOT FILE-SUCCESS
               MOVE ERR-FILE-ERROR TO ERROR-CODE
               MOVE 'UNABLE TO OPEN ACCOUNT FILE' TO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
               STOP RUN
           END-IF
           
           OPEN EXTEND TRANSACTION-LOG
           OPEN EXTEND AUDIT-LOG.
       
       1200-INITIALIZE-VARIABLES.
           MOVE 'Y' TO CONTINUE-FLAG
           MOVE 'N' TO ERROR-OCCURRED
           MOVE FUNCTION CURRENT-DATE TO CURRENT-DATE-TIME.
       
       1300-LOG-SYSTEM-START.
           MOVE CURRENT-DATE-TIME TO AUDIT-TIMESTAMP
           MOVE CURRENT-USER-ID TO AUDIT-USER-ID
           MOVE 'SYSTEM_START' TO AUDIT-ACTION
           MOVE SPACES TO AUDIT-ACCOUNT
           MOVE 'Account Management System Started' TO AUDIT-DETAILS
           WRITE AUDIT-RECORD.
       
      *****************************************************************
      * MENU PROCESSING - STRUCTURED WITHOUT GOTO                     *
      *****************************************************************
       2000-PROCESS-MENU.
           PERFORM 2100-DISPLAY-MENU
           PERFORM 2200-GET-MENU-CHOICE
           PERFORM 2300-EXECUTE-CHOICE.
       
       2100-DISPLAY-MENU.
           DISPLAY ' '
           DISPLAY '========================================='
           DISPLAY 'MAIN MENU'
           DISPLAY '========================================='
           DISPLAY '1. CREATE NEW ACCOUNT'
           DISPLAY '2. VIEW ACCOUNT BALANCE'
           DISPLAY '3. DEPOSIT MONEY'
           DISPLAY '4. WITHDRAW MONEY'
           DISPLAY '5. TRANSFER MONEY'
           DISPLAY '6. CALCULATE INTEREST'
           DISPLAY '7. VIEW TRANSACTION HISTORY'
           DISPLAY '9. EXIT SYSTEM'
           DISPLAY '========================================='
           DISPLAY 'ENTER YOUR CHOICE (1-7, 9): '.
       
       2200-GET-MENU-CHOICE.
           ACCEPT MENU-CHOICE
           IF MENU-CHOICE < 1 OR MENU-CHOICE > 9 OR MENU-CHOICE = 8
               DISPLAY 'INVALID CHOICE. PLEASE TRY AGAIN.'
               PERFORM 2200-GET-MENU-CHOICE
           END-IF.
       
       2300-EXECUTE-CHOICE.
           EVALUATE MENU-CHOICE
               WHEN 1
                   PERFORM 3000-CREATE-ACCOUNT
               WHEN 2
                   PERFORM 4000-VIEW-BALANCE
               WHEN 3
                   PERFORM 5000-DEPOSIT-MONEY
               WHEN 4
                   PERFORM 6000-WITHDRAW-MONEY
               WHEN 5
                   PERFORM 7000-TRANSFER-MONEY
               WHEN 6
                   PERFORM 8500-CALCULATE-INTEREST
               WHEN 7
                   PERFORM 8600-VIEW-TRANSACTION-HISTORY
               WHEN 9
                   MOVE 'N' TO CONTINUE-FLAG
           END-EVALUATE.
       
      *****************************************************************
      * ACCOUNT CREATION WITH PROPER VALIDATION                       *
      *****************************************************************
       3000-CREATE-ACCOUNT.
           DISPLAY ' '
           DISPLAY '========================================='
           DISPLAY 'CREATE NEW ACCOUNT'
           DISPLAY '========================================='
           
           PERFORM 3100-GET-ACCOUNT-DETAILS
           PERFORM 3200-VALIDATE-ACCOUNT-DATA
           
           IF NO-ERROR
               PERFORM 3300-CREATE-ACCOUNT-RECORD
               PERFORM 3400-LOG-ACCOUNT-CREATION
           END-IF.
       
       3100-GET-ACCOUNT-DETAILS.
           DISPLAY 'ENTER ACCOUNT NUMBER (10 DIGITS): '
           ACCEPT INPUT-ACCOUNT-NUMBER
           
           DISPLAY 'ENTER CUSTOMER NAME: '
           ACCEPT INPUT-CUSTOMER-NAME
           
           DISPLAY 'ENTER CUSTOMER ID: '
           ACCEPT INPUT-CUSTOMER-ID
           
           DISPLAY 'ENTER BRANCH CODE: '
           ACCEPT INPUT-BRANCH-CODE
           
           DISPLAY 'ENTER ACCOUNT TYPE (S=SAVINGS, C=CHECKING): '
           ACCEPT INPUT-ACCOUNT-TYPE
           
           DISPLAY 'ENTER INITIAL DEPOSIT: '
           ACCEPT INPUT-AMOUNT.
       
       3200-VALIDATE-ACCOUNT-DATA.
           PERFORM 3210-VALIDATE-ACCOUNT-NUMBER
           IF NO-ERROR
               PERFORM 3220-VALIDATE-CUSTOMER-DATA
           END-IF
           IF NO-ERROR
               PERFORM 3230-VALIDATE-INITIAL-DEPOSIT
           END-IF
           IF NO-ERROR
               PERFORM 3240-CHECK-ACCOUNT-EXISTS
           END-IF.
       
       3210-VALIDATE-ACCOUNT-NUMBER.
           IF FUNCTION LENGTH(FUNCTION TRIM(INPUT-ACCOUNT-NUMBER))
              NOT = ACCOUNT-NUMBER-LENGTH
               MOVE ERR-INVALID-ACCOUNT-NUM TO ERROR-CODE
               MOVE 'ACCOUNT NUMBER MUST BE 10 DIGITS' TO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF
           
           IF INPUT-ACCOUNT-NUMBER NOT NUMERIC
               MOVE ERR-INVALID-ACCOUNT-NUM TO ERROR-CODE
               MOVE 'ACCOUNT NUMBER MUST BE NUMERIC' TO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF.
       
       3220-VALIDATE-CUSTOMER-DATA.
           IF INPUT-CUSTOMER-NAME = SPACES
               MOVE ERR-INVALID-ACCOUNT-NUM TO ERROR-CODE
               MOVE 'CUSTOMER NAME IS REQUIRED' TO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF
           
           IF INPUT-ACCOUNT-TYPE NOT = 'S' AND NOT = 'C'
               MOVE ERR-INVALID-ACCOUNT-NUM TO ERROR-CODE
               MOVE 'ACCOUNT TYPE MUST BE S OR C' TO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF.
       
       3230-VALIDATE-INITIAL-DEPOSIT.
           IF INPUT-AMOUNT < MIN-OPENING-BALANCE
               MOVE ERR-INVALID-AMOUNT TO ERROR-CODE
               STRING 'MINIMUM OPENING BALANCE IS '
                      MIN-OPENING-BALANCE
                      DELIMITED BY SIZE
                      INTO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF.
       
       3240-CHECK-ACCOUNT-EXISTS.
           MOVE INPUT-ACCOUNT-NUMBER TO ACCT-NUMBER
           READ ACCOUNT-FILE
               INVALID KEY
                   CONTINUE
               NOT INVALID KEY
                   MOVE ERR-DUPLICATE-ACCOUNT TO ERROR-CODE
                   MOVE 'ACCOUNT NUMBER ALREADY EXISTS' TO ERROR-MESSAGE
                   PERFORM 8000-HANDLE-ERROR
           END-READ.
       
       3300-CREATE-ACCOUNT-RECORD.
           MOVE INPUT-ACCOUNT-NUMBER TO ACCT-NUMBER
           MOVE INPUT-CUSTOMER-NAME TO CUSTOMER-NAME
           MOVE INPUT-CUSTOMER-ID TO CUSTOMER-ID
           MOVE INPUT-BRANCH-CODE TO BRANCH-CODE
           MOVE INPUT-ACCOUNT-TYPE TO ACCOUNT-TYPE
           MOVE INPUT-AMOUNT TO ACCOUNT-BALANCE
           MOVE 'A' TO ACCOUNT-STATUS
           MOVE FUNCTION CURRENT-DATE(1:8) TO OPENING-DATE
           MOVE OPENING-DATE TO LAST-TRANSACTION-DATE
           
           IF SAVINGS-ACCOUNT
               MOVE SAVINGS-INTEREST-RATE TO INTEREST-RATE
           ELSE
               MOVE CHECKING-INTEREST-RATE TO INTEREST-RATE
           END-IF
           
           WRITE ACCOUNT-RECORD
           
           IF FILE-SUCCESS
               DISPLAY 'ACCOUNT CREATED SUCCESSFULLY'
               DISPLAY 'ACCOUNT NUMBER: ' ACCT-NUMBER
               DISPLAY 'INITIAL BALANCE: ' ACCOUNT-BALANCE
           ELSE
               MOVE ERR-FILE-ERROR TO ERROR-CODE
               MOVE 'ERROR CREATING ACCOUNT RECORD' TO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF.
       
       3400-LOG-ACCOUNT-CREATION.
           PERFORM 8700-GENERATE-TRANSACTION-ID
           MOVE TRANSACTION-ID TO TRANS-ID
           MOVE ACCT-NUMBER TO TRANS-ACCOUNT-NUMBER
           MOVE 'D' TO TRANS-TYPE
           MOVE ACCOUNT-BALANCE TO TRANS-AMOUNT
           MOVE CURRENT-DATE-TIME TO TRANS-TIMESTAMP
           MOVE 'S' TO TRANS-STATUS
           MOVE 'INITIAL DEPOSIT - ACCOUNT OPENING' TO TRANS-DESCRIPTION
           WRITE TRANSACTION-RECORD.
       
      *****************************************************************
      * VIEW ACCOUNT BALANCE WITH PROPER ERROR HANDLING               *
      *****************************************************************
       4000-VIEW-BALANCE.
           DISPLAY ' '
           DISPLAY '========================================='
           DISPLAY 'VIEW ACCOUNT BALANCE'
           DISPLAY '========================================='
           
           PERFORM 4100-GET-ACCOUNT-NUMBER
           PERFORM 4200-READ-ACCOUNT-RECORD
           
           IF NO-ERROR
               PERFORM 4300-DISPLAY-ACCOUNT-INFO
           END-IF.
       
       4100-GET-ACCOUNT-NUMBER.
           DISPLAY 'ENTER ACCOUNT NUMBER: '
           ACCEPT INPUT-ACCOUNT-NUMBER
           PERFORM 3210-VALIDATE-ACCOUNT-NUMBER.
       
       4200-READ-ACCOUNT-RECORD.
           MOVE INPUT-ACCOUNT-NUMBER TO ACCT-NUMBER
           READ ACCOUNT-FILE
               INVALID KEY
                   MOVE ERR-ACCOUNT-NOT-FOUND TO ERROR-CODE
                   MOVE 'ACCOUNT NOT FOUND' TO ERROR-MESSAGE
                   PERFORM 8000-HANDLE-ERROR
           END-READ
           
           IF NO-ERROR AND NOT ACTIVE-ACCOUNT
               MOVE ERR-ACCOUNT-INACTIVE TO ERROR-CODE
               MOVE 'ACCOUNT IS NOT ACTIVE' TO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF.
       
       4300-DISPLAY-ACCOUNT-INFO.
           DISPLAY ' '
           DISPLAY 'ACCOUNT INFORMATION:'
           DISPLAY '-------------------'
           DISPLAY 'ACCOUNT NUMBER: ' ACCT-NUMBER
           DISPLAY 'CUSTOMER NAME:  ' CUSTOMER-NAME
           DISPLAY 'ACCOUNT TYPE:   ' ACCOUNT-TYPE
           DISPLAY 'CURRENT BALANCE:' ACCOUNT-BALANCE
           DISPLAY 'ACCOUNT STATUS: ' ACCOUNT-STATUS
           DISPLAY 'LAST TRANSACTION:' LAST-TRANSACTION-DATE.
       
      *****************************************************************
      * MONEY TRANSFER WITH TRANSACTION MANAGEMENT                     *
      *****************************************************************
       7000-TRANSFER-MONEY.
           DISPLAY ' '
           DISPLAY '========================================='
           DISPLAY 'TRANSFER MONEY'
           DISPLAY '========================================='
           
           PERFORM 7100-GET-TRANSFER-DETAILS
           PERFORM 7200-VALIDATE-TRANSFER
           
           IF NO-ERROR
               PERFORM 7300-EXECUTE-TRANSFER
           END-IF.
       
       7100-GET-TRANSFER-DETAILS.
           DISPLAY 'ENTER FROM ACCOUNT NUMBER: '
           ACCEPT INPUT-FROM-ACCOUNT
           
           DISPLAY 'ENTER TO ACCOUNT NUMBER: '
           ACCEPT INPUT-TO-ACCOUNT
           
           DISPLAY 'ENTER TRANSFER AMOUNT: '
           ACCEPT INPUT-AMOUNT.
       
       7200-VALIDATE-TRANSFER.
           IF INPUT-AMOUNT <= ZERO
               MOVE ERR-INVALID-AMOUNT TO ERROR-CODE
               MOVE 'TRANSFER AMOUNT MUST BE POSITIVE' TO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF
           
           IF INPUT-AMOUNT > MAX-TRANSFER-AMOUNT
               MOVE ERR-TRANSFER-LIMIT TO ERROR-CODE
               STRING 'TRANSFER AMOUNT EXCEEDS LIMIT OF '
                      MAX-TRANSFER-AMOUNT
                      DELIMITED BY SIZE
                      INTO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF
           
           IF INPUT-FROM-ACCOUNT = INPUT-TO-ACCOUNT
               MOVE ERR-INVALID-ACCOUNT-NUM TO ERROR-CODE
               MOVE 'CANNOT TRANSFER TO SAME ACCOUNT' TO ERROR-MESSAGE
               PERFORM 8000-HANDLE-ERROR
           END-IF.
       
       7300-EXECUTE-TRANSFER.
           MOVE 'Y' TO TRANS-IN-PROGRESS
           
           PERFORM 7310-DEBIT-FROM-ACCOUNT
           IF NO-ERROR
               PERFORM 7320-CREDIT-TO-ACCOUNT
           END-IF
           
           IF ERROR-FOUND
               PERFORM 7330-ROLLBACK-TRANSFER
           ELSE
               PERFORM 7340-COMMIT-TRANSFER
           END-IF
           
           MOVE 'N' TO TRANS-IN-PROGRESS.
       
       7310-DEBIT-FROM-ACCOUNT.
           MOVE INPUT-FROM-ACCOUNT TO ACCT-NUMBER
           READ ACCOUNT-FILE UPDATE
               INVALID KEY
                   MOVE ERR-ACCOUNT-NOT-FOUND TO ERROR-CODE
                   MOVE 'FROM ACCOUNT NOT FOUND' TO ERROR-MESSAGE
                   PERFORM 8000-HANDLE-ERROR
           END-READ
           
           IF NO-ERROR
               IF NOT ACTIVE-ACCOUNT
                   MOVE ERR-ACCOUNT-INACTIVE TO ERROR-CODE
                   MOVE 'FROM ACCOUNT IS NOT ACTIVE' TO ERROR-MESSAGE
                   PERFORM 8000-HANDLE-ERROR
               ELSE
                   IF ACCOUNT-BALANCE < INPUT-AMOUNT
                       MOVE ERR-INSUFFICIENT-FUNDS TO ERROR-CODE
                       MOVE 'INSUFFICIENT FUNDS IN FROM ACCOUNT'
                            TO ERROR-MESSAGE
                       PERFORM 8000-HANDLE-ERROR
                   ELSE
                       SUBTRACT INPUT-AMOUNT FROM ACCOUNT-BALANCE
                       MOVE FUNCTION CURRENT-DATE(1:8)
                            TO LAST-TRANSACTION-DATE
                       REWRITE ACCOUNT-RECORD
                   END-IF
               END-IF
           END-IF.
       
       7320-CREDIT-TO-ACCOUNT.
           MOVE INPUT-TO-ACCOUNT TO ACCT-NUMBER
           READ ACCOUNT-FILE UPDATE
               INVALID KEY
                   MOVE ERR-ACCOUNT-NOT-FOUND TO ERROR-CODE
                   MOVE 'TO ACCOUNT NOT FOUND' TO ERROR-MESSAGE
                   PERFORM 8000-HANDLE-ERROR
           END-READ
           
           IF NO-ERROR
               IF NOT ACTIVE-ACCOUNT
                   MOVE ERR-ACCOUNT-INACTIVE TO ERROR-CODE
                   MOVE 'TO ACCOUNT IS NOT ACTIVE' TO ERROR-MESSAGE
                   PERFORM 8000-HANDLE-ERROR
               ELSE
                   ADD INPUT-AMOUNT TO ACCOUNT-BALANCE
                   MOVE FUNCTION CURRENT-DATE(1:8)
                        TO LAST-TRANSACTION-DATE
                   REWRITE ACCOUNT-RECORD
               END-IF
           END-IF.
       
       7330-ROLLBACK-TRANSFER.
           DISPLAY 'TRANSFER FAILED - ROLLING BACK CHANGES'
           DISPLAY 'ERROR: ' ERROR-MESSAGE
           
           MOVE INPUT-FROM-ACCOUNT TO ACCT-NUMBER
           READ ACCOUNT-FILE UPDATE
           ADD INPUT-AMOUNT TO ACCOUNT-BALANCE
           REWRITE ACCOUNT-RECORD.
       
       7340-COMMIT-TRANSFER.
           DISPLAY 'TRANSFER COMPLETED SUCCESSFULLY'
           DISPLAY 'AMOUNT TRANSFERRED: ' INPUT-AMOUNT
           DISPLAY 'FROM ACCOUNT: ' INPUT-FROM-ACCOUNT
           DISPLAY 'TO ACCOUNT: ' INPUT-TO-ACCOUNT
           
           PERFORM 7350-LOG-TRANSFER-TRANSACTIONS.
       
       7350-LOG-TRANSFER-TRANSACTIONS.
           PERFORM 8700-GENERATE-TRANSACTION-ID
           
           MOVE TRANSACTION-ID TO TRANS-ID
           MOVE INPUT-FROM-ACCOUNT TO TRANS-ACCOUNT-NUMBER
           MOVE 'T' TO TRANS-TYPE
           MOVE INPUT-AMOUNT TO TRANS-AMOUNT
           MOVE CURRENT-DATE-TIME TO TRANS-TIMESTAMP
           MOVE 'S' TO TRANS-STATUS
           STRING 'TRANSFER TO ' INPUT-TO-ACCOUNT
                  DELIMITED BY SIZE
                  INTO TRANS-DESCRIPTION
           WRITE TRANSACTION-RECORD
           
           PERFORM 8700-GENERATE-TRANSACTION-ID
           MOVE TRANSACTION-ID TO TRANS-ID
           MOVE INPUT-TO-ACCOUNT TO TRANS-ACCOUNT-NUMBER
           MOVE 'R' TO TRANS-TYPE
           MOVE INPUT-AMOUNT TO TRANS-AMOUNT
           MOVE CURRENT-DATE-TIME TO TRANS-TIMESTAMP
           MOVE 'S' TO TRANS-STATUS
           STRING 'TRANSFER FROM ' INPUT-FROM-ACCOUNT
                  DELIMITED BY SIZE
                  INTO TRANS-DESCRIPTION
           WRITE TRANSACTION-RECORD.
       
      *****************************************************************
      * UTILITY FUNCTIONS                                              *
      *****************************************************************
       8000-HANDLE-ERROR.
           MOVE 'Y' TO ERROR-OCCURRED
           DISPLAY ' '
           DISPLAY 'ERROR: ' ERROR-CODE
           DISPLAY 'MESSAGE: ' ERROR-MESSAGE
           DISPLAY ' '
           
           PERFORM 8100-LOG-ERROR.
       
       8100-LOG-ERROR.
           MOVE CURRENT-DATE-TIME TO AUDIT-TIMESTAMP
           MOVE CURRENT-USER-ID TO AUDIT-USER-ID
           MOVE 'ERROR' TO AUDIT-ACTION
           MOVE INPUT-ACCOUNT-NUMBER TO AUDIT-ACCOUNT
           STRING ERROR-CODE ' - ' ERROR-MESSAGE
                  DELIMITED BY SIZE
                  INTO AUDIT-DETAILS
           WRITE AUDIT-RECORD.
       
       8700-GENERATE-TRANSACTION-ID.
           STRING 'TXN' FUNCTION CURRENT-DATE(1:8)
                  FUNCTION CURRENT-DATE(9:6)
                  DELIMITED BY SIZE
                  INTO TRANSACTION-ID.
       
      *****************************************************************
      * PROGRAM TERMINATION                                            *
      *****************************************************************
       9000-TERMINATE-PROGRAM.
           PERFORM 9100-CLOSE-FILES
           PERFORM 9200-LOG-SYSTEM-END
           DISPLAY ' '
           DISPLAY 'THANK YOU FOR USING BANK ACCOUNT MANAGEMENT SYSTEM'
           DISPLAY 'SESSION ENDED SUCCESSFULLY'.
       
       9100-CLOSE-FILES.
           CLOSE ACCOUNT-FILE
           CLOSE TRANSACTION-LOG
           CLOSE AUDIT-LOG.
       
       9200-LOG-SYSTEM-END.
           MOVE CURRENT-DATE-TIME TO AUDIT-TIMESTAMP
           MOVE CURRENT-USER-ID TO AUDIT-USER-ID
           MOVE 'SYSTEM_END' TO AUDIT-ACTION
           MOVE SPACES TO AUDIT-ACCOUNT
           MOVE 'Account Management System Ended' TO AUDIT-DETAILS
           WRITE AUDIT-RECORD.
       
      * ADDITIONAL MODULES FOR DEPOSIT, WITHDRAWAL, INTEREST CALCULATION
      * AND TRANSACTION HISTORY WOULD FOLLOW SIMILAR PATTERNS...
       
       5000-DEPOSIT-MONEY.
           DISPLAY 'DEPOSIT FUNCTION - TO BE IMPLEMENTED'.
       
       6000-WITHDRAW-MONEY.
           DISPLAY 'WITHDRAWAL FUNCTION - TO BE IMPLEMENTED'.
       
       8500-CALCULATE-INTEREST.
           DISPLAY 'INTEREST CALCULATION - TO BE IMPLEMENTED'.
       
       8600-VIEW-TRANSACTION-HISTORY.
           DISPLAY 'TRANSACTION HISTORY - TO BE IMPLEMENTED'.

* Made with Bob
