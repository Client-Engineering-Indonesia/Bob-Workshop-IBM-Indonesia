       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTMGMT.
       AUTHOR. LEGACY-DEVELOPER.
      *****************************************************************
      * LEGACY ACCOUNT MANAGEMENT PROGRAM                             *
      * WRITTEN IN COBOL-85 STYLE                                     *
      * DEMONSTRATES COMMON LEGACY PATTERNS AND ANTI-PATTERNS         *
      *                                                               *
      * ISSUES DEMONSTRATED:                                          *
      * - GOTO STATEMENTS (SPAGHETTI CODE)                           *
      * - HARDCODED VALUES                                           *
      * - POOR ERROR HANDLING                                        *
      * - NO MODULARIZATION                                          *
      * - MIXED BUSINESS LOGIC AND I/O                               *
      * - CRYPTIC VARIABLE NAMES                                     *
      * - LACK OF DOCUMENTATION                                      *
      *****************************************************************
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACCOUNT-FILE ASSIGN TO 'ACCOUNT.DAT'
               ORGANIZATION IS INDEXED
               ACCESS MODE IS RANDOM
               RECORD KEY IS ACCT-NO
               FILE STATUS IS WS-FILE-STATUS.
           
           SELECT TRANS-FILE ASSIGN TO 'TRANS.DAT'
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE IS SEQUENTIAL
               FILE STATUS IS WS-TRANS-STATUS.
       
       DATA DIVISION.
       FILE SECTION.
       FD  ACCOUNT-FILE.
       01  ACCOUNT-RECORD.
           05  ACCT-NO                 PIC X(10).
           05  CUST-NAME               PIC X(30).
           05  ACCT-TYPE               PIC X(01).
           05  ACCT-BAL                PIC 9(13)V99.
           05  ACCT-STATUS             PIC X(01).
           05  OPEN-DATE               PIC X(08).
           05  LAST-TRANS-DATE         PIC X(08).
           05  INT-RATE                PIC 9(02)V99.
       
       FD  TRANS-FILE.
       01  TRANS-RECORD.
           05  TRANS-ACCT-NO           PIC X(10).
           05  TRANS-TYPE              PIC X(01).
           05  TRANS-AMT               PIC 9(13)V99.
           05  TRANS-DATE              PIC X(08).
       
       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUS              PIC XX.
       01  WS-TRANS-STATUS             PIC XX.
       01  WS-EOF                      PIC X VALUE 'N'.
       
      * HARDCODED VALUES - SHOULD BE IN CONFIGURATION
       01  WS-MAX-TRANSFER             PIC 9(13)V99 VALUE 100000000.00.
       01  WS-MIN-BALANCE              PIC 9(13)V99 VALUE 100000.00.
       01  WS-INTEREST-RATE            PIC 9(02)V99 VALUE 05.00.
       
      * CRYPTIC VARIABLE NAMES
       01  WS-A                        PIC 9(13)V99.
       01  WS-B                        PIC 9(13)V99.
       01  WS-C                        PIC 9(13)V99.
       01  WS-D                        PIC X(10).
       01  WS-E                        PIC X(10).
       01  WS-F                        PIC X(01).
       
      * NO PROPER ERROR CODES
       01  WS-ERROR                    PIC X VALUE 'N'.
       01  WS-MSG                      PIC X(50).
       
      * MIXED CONCERNS - UI AND BUSINESS LOGIC
       01  WS-MENU-CHOICE              PIC 9.
       
       PROCEDURE DIVISION.
       MAIN-PARA.
           OPEN I-O ACCOUNT-FILE.
           IF WS-FILE-STATUS NOT = '00'
               DISPLAY 'ERROR OPENING FILE'
               STOP RUN.
           
      * POOR MENU STRUCTURE WITH GOTO
       MENU-LOOP.
           DISPLAY '================================'.
           DISPLAY 'ACCOUNT MANAGEMENT SYSTEM'.
           DISPLAY '================================'.
           DISPLAY '1. CREATE ACCOUNT'.
           DISPLAY '2. VIEW BALANCE'.
           DISPLAY '3. DEPOSIT'.
           DISPLAY '4. WITHDRAW'.
           DISPLAY '5. TRANSFER'.
           DISPLAY '6. CALCULATE INTEREST'.
           DISPLAY '9. EXIT'.
           DISPLAY 'ENTER CHOICE: '.
           ACCEPT WS-MENU-CHOICE.
           
           IF WS-MENU-CHOICE = 1
               GO TO CREATE-ACCOUNT
           ELSE IF WS-MENU-CHOICE = 2
               GO TO VIEW-BALANCE
           ELSE IF WS-MENU-CHOICE = 3
               GO TO DEPOSIT-MONEY
           ELSE IF WS-MENU-CHOICE = 4
               GO TO WITHDRAW-MONEY
           ELSE IF WS-MENU-CHOICE = 5
               GO TO TRANSFER-MONEY
           ELSE IF WS-MENU-CHOICE = 6
               GO TO CALC-INTEREST
           ELSE IF WS-MENU-CHOICE = 9
               GO TO EXIT-PROGRAM
           ELSE
               DISPLAY 'INVALID CHOICE'
               GO TO MENU-LOOP.
       
      * SPAGHETTI CODE WITH GOTO STATEMENTS
       CREATE-ACCOUNT.
           DISPLAY 'ENTER ACCOUNT NUMBER: '.
           ACCEPT ACCT-NO.
           
      * NO INPUT VALIDATION
           DISPLAY 'ENTER CUSTOMER NAME: '.
           ACCEPT CUST-NAME.
           
           DISPLAY 'ENTER ACCOUNT TYPE (S/C): '.
           ACCEPT ACCT-TYPE.
           
           DISPLAY 'ENTER INITIAL DEPOSIT: '.
           ACCEPT ACCT-BAL.
           
      * HARDCODED BUSINESS RULE
           IF ACCT-BAL < WS-MIN-BALANCE
               DISPLAY 'MINIMUM BALANCE REQUIRED: 100000'
               GO TO MENU-LOOP.
           
           MOVE 'A' TO ACCT-STATUS.
           ACCEPT OPEN-DATE FROM DATE.
           MOVE OPEN-DATE TO LAST-TRANS-DATE.
           
      * HARDCODED INTEREST RATE
           IF ACCT-TYPE = 'S'
               MOVE 05.00 TO INT-RATE
           ELSE
               MOVE 02.00 TO INT-RATE.
           
           WRITE ACCOUNT-RECORD.
           
           IF WS-FILE-STATUS = '00'
               DISPLAY 'ACCOUNT CREATED SUCCESSFULLY'
           ELSE
               DISPLAY 'ERROR CREATING ACCOUNT: ' WS-FILE-STATUS.
           
           GO TO MENU-LOOP.
       
       VIEW-BALANCE.
           DISPLAY 'ENTER ACCOUNT NUMBER: '.
           ACCEPT WS-D.
           MOVE WS-D TO ACCT-NO.
           
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY 'ACCOUNT NOT FOUND'
                   GO TO MENU-LOOP.
           
      * POOR OUTPUT FORMATTING
           DISPLAY 'ACCOUNT: ' ACCT-NO.
           DISPLAY 'NAME: ' CUST-NAME.
           DISPLAY 'BALANCE: ' ACCT-BAL.
           
           GO TO MENU-LOOP.
       
       DEPOSIT-MONEY.
           DISPLAY 'ENTER ACCOUNT NUMBER: '.
           ACCEPT WS-D.
           MOVE WS-D TO ACCT-NO.
           
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY 'ACCOUNT NOT FOUND'
                   GO TO MENU-LOOP.
           
           DISPLAY 'ENTER DEPOSIT AMOUNT: '.
           ACCEPT WS-A.
           
      * NO VALIDATION OF AMOUNT
           ADD WS-A TO ACCT-BAL.
           ACCEPT LAST-TRANS-DATE FROM DATE.
           
           REWRITE ACCOUNT-RECORD.
           
           IF WS-FILE-STATUS = '00'
               DISPLAY 'DEPOSIT SUCCESSFUL'
               DISPLAY 'NEW BALANCE: ' ACCT-BAL
           ELSE
               DISPLAY 'ERROR: ' WS-FILE-STATUS.
           
           GO TO MENU-LOOP.
       
       WITHDRAW-MONEY.
           DISPLAY 'ENTER ACCOUNT NUMBER: '.
           ACCEPT WS-D.
           MOVE WS-D TO ACCT-NO.
           
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY 'ACCOUNT NOT FOUND'
                   GO TO MENU-LOOP.
           
           DISPLAY 'ENTER WITHDRAWAL AMOUNT: '.
           ACCEPT WS-A.
           
      * INSUFFICIENT FUNDS CHECK
           IF WS-A > ACCT-BAL
               DISPLAY 'INSUFFICIENT FUNDS'
               GO TO MENU-LOOP.
           
           SUBTRACT WS-A FROM ACCT-BAL.
           ACCEPT LAST-TRANS-DATE FROM DATE.
           
           REWRITE ACCOUNT-RECORD.
           
           IF WS-FILE-STATUS = '00'
               DISPLAY 'WITHDRAWAL SUCCESSFUL'
               DISPLAY 'NEW BALANCE: ' ACCT-BAL
           ELSE
               DISPLAY 'ERROR: ' WS-FILE-STATUS.
           
           GO TO MENU-LOOP.
       
      * NO TRANSACTION MANAGEMENT - MONEY CAN BE LOST!
       TRANSFER-MONEY.
           DISPLAY 'ENTER FROM ACCOUNT: '.
           ACCEPT WS-D.
           MOVE WS-D TO ACCT-NO.
           
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY 'FROM ACCOUNT NOT FOUND'
                   GO TO MENU-LOOP.
           
           MOVE ACCT-BAL TO WS-B.
           
           DISPLAY 'ENTER TO ACCOUNT: '.
           ACCEPT WS-E.
           
           DISPLAY 'ENTER TRANSFER AMOUNT: '.
           ACCEPT WS-A.
           
      * MAGIC NUMBER
           IF WS-A > 100000000
               DISPLAY 'AMOUNT EXCEEDS LIMIT'
               GO TO MENU-LOOP.
           
           IF WS-A > WS-B
               DISPLAY 'INSUFFICIENT FUNDS'
               GO TO MENU-LOOP.
           
      * DEBIT FROM SOURCE - NO ROLLBACK IF NEXT STEP FAILS!
           SUBTRACT WS-A FROM ACCT-BAL.
           ACCEPT LAST-TRANS-DATE FROM DATE.
           REWRITE ACCOUNT-RECORD.
           
           IF WS-FILE-STATUS NOT = '00'
               DISPLAY 'ERROR DEBITING ACCOUNT'
               GO TO MENU-LOOP.
           
      * CREDIT TO DESTINATION - IF THIS FAILS, MONEY IS LOST!
           MOVE WS-E TO ACCT-NO.
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY 'TO ACCOUNT NOT FOUND'
                   DISPLAY 'MONEY LOST IN TRANSFER!'
                   GO TO MENU-LOOP.
           
           ADD WS-A TO ACCT-BAL.
           ACCEPT LAST-TRANS-DATE FROM DATE.
           REWRITE ACCOUNT-RECORD.
           
           IF WS-FILE-STATUS = '00'
               DISPLAY 'TRANSFER SUCCESSFUL'
           ELSE
               DISPLAY 'ERROR CREDITING ACCOUNT'
               DISPLAY 'MONEY LOST IN TRANSFER!'.
           
           GO TO MENU-LOOP.
       
      * BUSINESS LOGIC MIXED WITH FILE I/O
       CALC-INTEREST.
           DISPLAY 'CALCULATING INTEREST FOR ALL ACCOUNTS...'.
           
           OPEN INPUT ACCOUNT-FILE.
           
           PERFORM UNTIL WS-EOF = 'Y'
               READ ACCOUNT-FILE NEXT RECORD
                   AT END
                       MOVE 'Y' TO WS-EOF
                   NOT AT END
                       IF ACCT-TYPE = 'S' AND ACCT-STATUS = 'A'
      * HARDCODED CALCULATION
                           COMPUTE WS-C = ACCT-BAL * 0.05 / 12
                           ADD WS-C TO ACCT-BAL
                           REWRITE ACCOUNT-RECORD
                           DISPLAY 'INTEREST ADDED TO: ' ACCT-NO
                       END-IF
               END-READ
           END-PERFORM.
           
           CLOSE ACCOUNT-FILE.
           DISPLAY 'INTEREST CALCULATION COMPLETE'.
           
           GO TO MENU-LOOP.
       
       EXIT-PROGRAM.
           CLOSE ACCOUNT-FILE.
           DISPLAY 'THANK YOU FOR USING THE SYSTEM'.
           STOP RUN.

* Made with Bob
