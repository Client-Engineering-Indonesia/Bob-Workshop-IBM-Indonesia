       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTMGMT.
       AUTHOR. LEGACY BANKING SYSTEMS.
      ******************************************************************
      * ACCOUNT MANAGEMENT SYSTEM                                      *
      * Description: Handles account creation, updates, and inquiries  *
      * Dependencies: ACCTREC.CPY, CUSTREC.CPY, ERRCODE.CPY           *
      * Files: ACCOUNT-FILE (VSAM KSDS)                               *
      *        CUSTOMER-FILE (VSAM KSDS)                              *
      ******************************************************************
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACCOUNT-FILE
               ASSIGN TO ACCTMAST
               ORGANIZATION IS INDEXED
               ACCESS MODE IS DYNAMIC
               RECORD KEY IS ACCT-NUMBER
               FILE STATUS IS WS-ACCT-FILE-STATUS.
               
           SELECT CUSTOMER-FILE
               ASSIGN TO CUSTMAST
               ORGANIZATION IS INDEXED
               ACCESS MODE IS RANDOM
               RECORD KEY IS CUSTOMER-ID OF CUSTOMER-RECORD
               FILE STATUS IS WS-CUST-FILE-STATUS.
       
       DATA DIVISION.
       FILE SECTION.
       FD  ACCOUNT-FILE.
       COPY ACCTREC.
       
       FD  CUSTOMER-FILE.
       COPY CUSTREC.
       
       WORKING-STORAGE SECTION.
       COPY ERRCODE.
       
       01  WS-FILE-STATUS.
           05  WS-ACCT-FILE-STATUS        PIC XX.
           05  WS-CUST-FILE-STATUS        PIC XX.
       
       01  WS-OPERATION-CODE              PIC X(02).
           88  CREATE-ACCOUNT             VALUE 'CR'.
           88  UPDATE-ACCOUNT             VALUE 'UP'.
           88  INQUIRY-ACCOUNT            VALUE 'IN'.
           88  CLOSE-ACCOUNT              VALUE 'CL'.
           88  FREEZE-ACCOUNT             VALUE 'FR'.
           88  UNFREEZE-ACCOUNT           VALUE 'UF'.
       
       01  WS-WORK-FIELDS.
           05  WS-CURRENT-DATE.
               10  WS-CURR-YEAR           PIC 9(04).
               10  WS-CURR-MONTH          PIC 9(02).
               10  WS-CURR-DAY            PIC 9(02).
           05  WS-CURRENT-TIME.
               10  WS-CURR-HOUR           PIC 9(02).
               10  WS-CURR-MINUTE         PIC 9(02).
               10  WS-CURR-SECOND         PIC 9(02).
           05  WS-FORMATTED-DATE          PIC 9(08).
           05  WS-FORMATTED-TIME          PIC 9(06).
           05  WS-RETURN-CODE             PIC X(04).
           05  WS-ERROR-MESSAGE           PIC X(100).
       
       01  WS-ACCOUNT-WORK-AREA.
           05  WS-NEW-ACCT-NUMBER         PIC 9(12).
           05  WS-SEARCH-CUST-ID          PIC 9(10).
           05  WS-INITIAL-DEPOSIT         PIC S9(13)V99 COMP-3.
           05  WS-REQUESTED-TYPE          PIC X(02).
       
       01  WS-COUNTERS.
           05  WS-ACCOUNTS-PROCESSED      PIC 9(08) VALUE ZERO.
           05  WS-ACCOUNTS-CREATED        PIC 9(08) VALUE ZERO.
           05  WS-ACCOUNTS-UPDATED        PIC 9(08) VALUE ZERO.
           05  WS-ACCOUNTS-CLOSED         PIC 9(08) VALUE ZERO.
           05  WS-ERRORS-ENCOUNTERED      PIC 9(08) VALUE ZERO.
       
       PROCEDURE DIVISION.
       0000-MAIN-PROCESS.
           PERFORM 1000-INITIALIZE
           PERFORM 2000-PROCESS-ACCOUNTS
           PERFORM 3000-FINALIZE
           STOP RUN.
       
       1000-INITIALIZE.
           DISPLAY '========================================='
           DISPLAY 'ACCOUNT MANAGEMENT SYSTEM - STARTING'
           DISPLAY '========================================='
           
           OPEN I-O ACCOUNT-FILE
           IF WS-ACCT-FILE-STATUS NOT = '00'
               DISPLAY 'ERROR OPENING ACCOUNT FILE: ' 
                       WS-ACCT-FILE-STATUS
               MOVE ERR-FILE-OPEN-ERROR TO WS-RETURN-CODE
               PERFORM 9999-ABNORMAL-TERMINATION
           END-IF
           
           OPEN INPUT CUSTOMER-FILE
           IF WS-CUST-FILE-STATUS NOT = '00'
               DISPLAY 'ERROR OPENING CUSTOMER FILE: '
                       WS-CUST-FILE-STATUS
               MOVE ERR-FILE-OPEN-ERROR TO WS-RETURN-CODE
               PERFORM 9999-ABNORMAL-TERMINATION
           END-IF
           
           ACCEPT WS-CURRENT-DATE FROM DATE YYYYMMDD
           ACCEPT WS-CURRENT-TIME FROM TIME
           MOVE FUNCTION CONCATENATE(WS-CURR-YEAR, WS-CURR-MONTH,
                WS-CURR-DAY) TO WS-FORMATTED-DATE
           MOVE FUNCTION CONCATENATE(WS-CURR-HOUR, WS-CURR-MINUTE,
                WS-CURR-SECOND) TO WS-FORMATTED-TIME.
       
       2000-PROCESS-ACCOUNTS.
           DISPLAY 'PROCESSING ACCOUNT OPERATIONS...'
           
      *    THIS SECTION WOULD NORMALLY RECEIVE INPUT FROM:
      *    - ONLINE TERMINAL (CICS/IMS)
      *    - BATCH INPUT FILE
      *    - MESSAGE QUEUE
      *    FOR DEMO PURPOSES, WE'LL SHOW THE LOGIC STRUCTURE
           
           PERFORM 2100-CREATE-NEW-ACCOUNT
           PERFORM 2200-UPDATE-EXISTING-ACCOUNT
           PERFORM 2300-INQUIRY-ACCOUNT
           PERFORM 2400-CLOSE-ACCOUNT-PROCESS.
       
       2100-CREATE-NEW-ACCOUNT.
           DISPLAY 'CREATING NEW ACCOUNT...'
           
      *    VALIDATE CUSTOMER EXISTS
           MOVE 1234567890 TO WS-SEARCH-CUST-ID
           MOVE WS-SEARCH-CUST-ID TO CUSTOMER-ID OF CUSTOMER-RECORD
           
           READ CUSTOMER-FILE
               INVALID KEY
                   DISPLAY 'CUSTOMER NOT FOUND: ' WS-SEARCH-CUST-ID
                   MOVE ERR-CUSTOMER-NOT-FOUND TO WS-RETURN-CODE
                   ADD 1 TO WS-ERRORS-ENCOUNTERED
                   GO TO 2100-EXIT
           END-READ
           
      *    CHECK CUSTOMER STATUS
           IF NOT ACTIVE-CUST
               DISPLAY 'CUSTOMER IS NOT ACTIVE'
               MOVE ERR-CUSTOMER-BLOCKED TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2100-EXIT
           END-IF
           
      *    CHECK KYC STATUS
           IF NOT KYC-COMPLETE
               DISPLAY 'KYC NOT COMPLETE FOR CUSTOMER'
               MOVE ERR-KYC-EXPIRED TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2100-EXIT
           END-IF
           
      *    GENERATE NEW ACCOUNT NUMBER
           PERFORM 2110-GENERATE-ACCOUNT-NUMBER
           
      *    INITIALIZE ACCOUNT RECORD
           INITIALIZE ACCOUNT-RECORD
           MOVE WS-NEW-ACCT-NUMBER TO ACCT-NUMBER
           MOVE 'SA' TO ACCT-TYPE
           SET SAVINGS-ACCT TO TRUE
           MOVE 'A' TO ACCT-STATUS
           SET ACTIVE-ACCT TO TRUE
           MOVE CUSTOMER-ID OF CUSTOMER-RECORD
                TO CUSTOMER-ID OF ACCOUNT-RECORD
           MOVE 1001 TO BRANCH-CODE
           MOVE 'IDR' TO CURRENCY-CODE
           MOVE 1000000.00 TO WS-INITIAL-DEPOSIT
           MOVE WS-INITIAL-DEPOSIT TO ACCT-BALANCE
           MOVE WS-INITIAL-DEPOSIT TO AVAILABLE-BALANCE
           MOVE ZERO TO HOLD-AMOUNT
           MOVE ZERO TO OVERDRAFT-LIMIT
           MOVE 2.5000 TO INTEREST-RATE
           MOVE WS-FORMATTED-DATE TO ACCT-OPEN-DATE
           MOVE WS-FORMATTED-DATE TO LAST-TRAN-DATE
           MOVE WS-FORMATTED-TIME TO LAST-TRAN-TIME
           MOVE 50000.00 TO MINIMUM-BALANCE
           MOVE ZERO TO ACCRUED-INTEREST
           MOVE ZERO TO YTD-INTEREST
           MOVE 10000.00 TO MONTHLY-FEE
           MOVE 'ACCT001' TO ACCT-OFFICER-ID
           MOVE 'A1' TO RISK-RATING
           
      *    WRITE NEW ACCOUNT RECORD
           WRITE ACCOUNT-RECORD
               INVALID KEY
                   DISPLAY 'ERROR CREATING ACCOUNT: ' 
                           WS-ACCT-FILE-STATUS
                   MOVE ERR-FILE-WRITE-ERROR TO WS-RETURN-CODE
                   ADD 1 TO WS-ERRORS-ENCOUNTERED
               NOT INVALID KEY
                   DISPLAY 'ACCOUNT CREATED: ' ACCT-NUMBER
                   ADD 1 TO WS-ACCOUNTS-CREATED
                   ADD 1 TO WS-ACCOUNTS-PROCESSED
           END-WRITE.
           
       2100-EXIT.
           EXIT.
       
       2110-GENERATE-ACCOUNT-NUMBER.
      *    IN PRODUCTION, THIS WOULD USE A SEQUENCE FILE OR DB2 SEQUENCE
      *    FOR DEMO, WE'LL USE A SIMPLE ALGORITHM
           COMPUTE WS-NEW-ACCT-NUMBER = 
               (WS-CURR-YEAR * 100000000) +
               (WS-CURR-MONTH * 1000000) +
               (WS-CURR-DAY * 10000) +
               (WS-CURR-HOUR * 100) +
               WS-CURR-MINUTE.
       
       2200-UPDATE-EXISTING-ACCOUNT.
           DISPLAY 'UPDATING ACCOUNT...'
           
           MOVE WS-NEW-ACCT-NUMBER TO ACCT-NUMBER
           
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY 'ACCOUNT NOT FOUND FOR UPDATE'
                   MOVE ERR-ACCOUNT-NOT-FOUND TO WS-RETURN-CODE
                   ADD 1 TO WS-ERRORS-ENCOUNTERED
                   GO TO 2200-EXIT
           END-READ
           
      *    CHECK ACCOUNT STATUS
           IF CLOSED-ACCT
               DISPLAY 'CANNOT UPDATE CLOSED ACCOUNT'
               MOVE ERR-ACCOUNT-CLOSED TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2200-EXIT
           END-IF
           
      *    UPDATE ACCOUNT DETAILS
           MOVE 3.0000 TO INTEREST-RATE
           MOVE WS-FORMATTED-DATE TO LAST-TRAN-DATE
           MOVE WS-FORMATTED-TIME TO LAST-TRAN-TIME
           
           REWRITE ACCOUNT-RECORD
               INVALID KEY
                   DISPLAY 'ERROR UPDATING ACCOUNT'
                   MOVE ERR-FILE-WRITE-ERROR TO WS-RETURN-CODE
                   ADD 1 TO WS-ERRORS-ENCOUNTERED
               NOT INVALID KEY
                   DISPLAY 'ACCOUNT UPDATED: ' ACCT-NUMBER
                   ADD 1 TO WS-ACCOUNTS-UPDATED
                   ADD 1 TO WS-ACCOUNTS-PROCESSED
           END-REWRITE.
           
       2200-EXIT.
           EXIT.
       
       2300-INQUIRY-ACCOUNT.
           DISPLAY 'ACCOUNT INQUIRY...'
           
           MOVE WS-NEW-ACCT-NUMBER TO ACCT-NUMBER
           
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY 'ACCOUNT NOT FOUND'
                   MOVE ERR-ACCOUNT-NOT-FOUND TO WS-RETURN-CODE
                   ADD 1 TO WS-ERRORS-ENCOUNTERED
                   GO TO 2300-EXIT
           END-READ
           
           DISPLAY 'ACCOUNT NUMBER: ' ACCT-NUMBER
           DISPLAY 'ACCOUNT TYPE: ' ACCT-TYPE
           DISPLAY 'ACCOUNT STATUS: ' ACCT-STATUS
           DISPLAY 'CUSTOMER ID: ' CUSTOMER-ID OF ACCOUNT-RECORD
           DISPLAY 'BALANCE: ' ACCT-BALANCE
           DISPLAY 'AVAILABLE BALANCE: ' AVAILABLE-BALANCE
           DISPLAY 'INTEREST RATE: ' INTEREST-RATE
           ADD 1 TO WS-ACCOUNTS-PROCESSED.
           
       2300-EXIT.
           EXIT.
       
       2400-CLOSE-ACCOUNT-PROCESS.
           DISPLAY 'CLOSING ACCOUNT...'
           
           MOVE WS-NEW-ACCT-NUMBER TO ACCT-NUMBER
           
           READ ACCOUNT-FILE
               INVALID KEY
                   DISPLAY 'ACCOUNT NOT FOUND FOR CLOSURE'
                   MOVE ERR-ACCOUNT-NOT-FOUND TO WS-RETURN-CODE
                   ADD 1 TO WS-ERRORS-ENCOUNTERED
                   GO TO 2400-EXIT
           END-READ
           
      *    VALIDATE ACCOUNT CAN BE CLOSED
           IF ACCT-BALANCE NOT = ZERO
               DISPLAY 'ACCOUNT HAS BALANCE - CANNOT CLOSE'
               MOVE ERR-INVALID-TRANSACTION TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2400-EXIT
           END-IF
           
           IF HOLD-AMOUNT NOT = ZERO
               DISPLAY 'ACCOUNT HAS HOLDS - CANNOT CLOSE'
               MOVE ERR-INVALID-TRANSACTION TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2400-EXIT
           END-IF
           
      *    CLOSE THE ACCOUNT
           MOVE 'C' TO ACCT-STATUS
           SET CLOSED-ACCT TO TRUE
           MOVE WS-FORMATTED-DATE TO ACCT-CLOSE-DATE
           
           REWRITE ACCOUNT-RECORD
               INVALID KEY
                   DISPLAY 'ERROR CLOSING ACCOUNT'
                   MOVE ERR-FILE-WRITE-ERROR TO WS-RETURN-CODE
                   ADD 1 TO WS-ERRORS-ENCOUNTERED
               NOT INVALID KEY
                   DISPLAY 'ACCOUNT CLOSED: ' ACCT-NUMBER
                   ADD 1 TO WS-ACCOUNTS-CLOSED
                   ADD 1 TO WS-ACCOUNTS-PROCESSED
           END-REWRITE.
           
       2400-EXIT.
           EXIT.
       
       3000-FINALIZE.
           DISPLAY '========================================='
           DISPLAY 'ACCOUNT MANAGEMENT SYSTEM - SUMMARY'
           DISPLAY '========================================='
           DISPLAY 'TOTAL ACCOUNTS PROCESSED: ' WS-ACCOUNTS-PROCESSED
           DISPLAY 'ACCOUNTS CREATED: ' WS-ACCOUNTS-CREATED
           DISPLAY 'ACCOUNTS UPDATED: ' WS-ACCOUNTS-UPDATED
           DISPLAY 'ACCOUNTS CLOSED: ' WS-ACCOUNTS-CLOSED
           DISPLAY 'ERRORS ENCOUNTERED: ' WS-ERRORS-ENCOUNTERED
           DISPLAY '========================================='
           
           CLOSE ACCOUNT-FILE
           CLOSE CUSTOMER-FILE.
       
       9999-ABNORMAL-TERMINATION.
           DISPLAY '========================================='
           DISPLAY 'ABNORMAL TERMINATION'
           DISPLAY 'ERROR CODE: ' WS-RETURN-CODE
           DISPLAY '========================================='
           CLOSE ACCOUNT-FILE
           CLOSE CUSTOMER-FILE
           STOP RUN.

