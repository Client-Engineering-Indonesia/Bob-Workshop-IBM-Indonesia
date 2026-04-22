       IDENTIFICATION DIVISION.
       PROGRAM-ID. LOANPROC.
       AUTHOR. LEGACY BANKING SYSTEMS.
      ******************************************************************
      * LOAN PROCESSING SYSTEM                                         *
      * Description: Handles loan applications, disbursements,         *
      *              and payment processing                            *
      * Dependencies: LOANREC.CPY, ACCTREC.CPY, CUSTREC.CPY,          *
      *               ERRCODE.CPY                                      *
      * Database: PostgreSQL via EXEC SQL                             *
      ******************************************************************
       
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-370.
       OBJECT-COMPUTER. IBM-370.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       COPY LOANREC.
       COPY ACCTREC.
       COPY CUSTREC.
       COPY ERRCODE.
       
       EXEC SQL INCLUDE SQLCA END-EXEC.
       
       01  WS-OPERATION-CODE              PIC X(02).
           88  APPLY-LOAN                 VALUE 'AP'.
           88  APPROVE-LOAN               VALUE 'AV'.
           88  DISBURSE-LOAN              VALUE 'DB'.
           88  PROCESS-PAYMENT            VALUE 'PY'.
           88  INQUIRY-LOAN               VALUE 'IN'.
       
       01  WS-WORK-FIELDS.
           05  WS-CURRENT-DATE.
               10  WS-CURR-YEAR           PIC 9(04).
               10  WS-CURR-MONTH          PIC 9(02).
               10  WS-CURR-DAY            PIC 9(02).
           05  WS-FORMATTED-DATE          PIC 9(08).
           05  WS-RETURN-CODE             PIC X(04).
           05  WS-ERROR-MESSAGE           PIC X(100).
           05  WS-SQL-CODE                PIC S9(9) COMP.
       
       01  WS-LOAN-WORK-AREA.
           05  WS-NEW-LOAN-NUMBER         PIC 9(12).
           05  WS-SEARCH-LOAN-NUMBER      PIC 9(12).
           05  WS-CUSTOMER-ID-WORK        PIC 9(10).
           05  WS-LOAN-AMOUNT-WORK        PIC S9(13)V99 COMP-3.
           05  WS-PAYMENT-AMOUNT-WORK     PIC S9(11)V99 COMP-3.
           05  WS-INTEREST-AMOUNT         PIC S9(11)V99 COMP-3.
           05  WS-PRINCIPAL-AMOUNT        PIC S9(11)V99 COMP-3.
           05  WS-MONTHLY-RATE            PIC 9(02)V9(06) COMP-3.
           05  WS-TEMP-CALC               PIC S9(15)V99 COMP-3.
       
       01  WS-COUNTERS.
           05  WS-LOANS-PROCESSED         PIC 9(08) VALUE ZERO.
           05  WS-LOANS-APPLIED           PIC 9(08) VALUE ZERO.
           05  WS-LOANS-APPROVED          PIC 9(08) VALUE ZERO.
           05  WS-LOANS-DISBURSED         PIC 9(08) VALUE ZERO.
           05  WS-PAYMENTS-PROCESSED      PIC 9(08) VALUE ZERO.
           05  WS-ERRORS-ENCOUNTERED      PIC 9(08) VALUE ZERO.
       
       01  WS-SQL-VARIABLES.
           05  SQL-LOAN-NUMBER            PIC 9(12).
           05  SQL-LOAN-TYPE              PIC X(03).
           05  SQL-CUSTOMER-ID            PIC 9(10).
           05  SQL-LOAN-ACCOUNT           PIC 9(12).
           05  SQL-DISB-ACCOUNT           PIC 9(12).
           05  SQL-LOAN-STATUS            PIC X(01).
           05  SQL-ORIGINAL-AMOUNT        PIC S9(13)V99 COMP-3.
           05  SQL-OUTSTANDING-PRINCIPAL  PIC S9(13)V99 COMP-3.
           05  SQL-OUTSTANDING-INTEREST   PIC S9(13)V99 COMP-3.
           05  SQL-INTEREST-RATE          PIC 9(02)V9(04) COMP-3.
           05  SQL-LOAN-TERM              PIC 9(04).
           05  SQL-INSTALLMENT-AMOUNT     PIC S9(11)V99 COMP-3.
           05  SQL-CUSTOMER-STATUS        PIC X(01).
           05  SQL-CREDIT-SCORE           PIC 9(04).
           05  SQL-ACCOUNT-BALANCE        PIC S9(13)V99 COMP-3.
       
       PROCEDURE DIVISION.
       0000-MAIN-PROCESS.
           PERFORM 1000-INITIALIZE
           PERFORM 2000-PROCESS-LOANS
           PERFORM 3000-FINALIZE
           STOP RUN.
       
       1000-INITIALIZE.
           DISPLAY '========================================='
           DISPLAY 'LOAN PROCESSING SYSTEM - STARTING'
           DISPLAY '========================================='
           
           EXEC SQL
               CONNECT TO 'banking_db'
               USER 'db_user'
               USING 'db_password'
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'ERROR CONNECTING TO DATABASE: ' SQLCODE
               MOVE ERR-FILE-OPEN-ERROR TO WS-RETURN-CODE
               PERFORM 9999-ABNORMAL-TERMINATION
           END-IF
           
           ACCEPT WS-CURRENT-DATE FROM DATE YYYYMMDD
           MOVE FUNCTION CONCATENATE(WS-CURR-YEAR, WS-CURR-MONTH,
                WS-CURR-DAY) TO WS-FORMATTED-DATE.
       
       2000-PROCESS-LOANS.
           DISPLAY 'PROCESSING LOAN OPERATIONS...'
           
      *    DEMONSTRATE VARIOUS LOAN OPERATIONS
      *    IN PRODUCTION, INPUT WOULD COME FROM:
      *    - LOAN ORIGINATION SYSTEM
      *    - BRANCH TERMINALS
      *    - ONLINE APPLICATIONS
           
           PERFORM 2100-APPLY-FOR-LOAN
           PERFORM 2200-APPROVE-LOAN-APPLICATION
           PERFORM 2300-DISBURSE-LOAN
           PERFORM 2400-PROCESS-LOAN-PAYMENT
           PERFORM 2500-CALCULATE-INTEREST.
       
       2100-APPLY-FOR-LOAN.
           DISPLAY 'PROCESSING LOAN APPLICATION...'
           
      *    GENERATE LOAN NUMBER
           PERFORM 2110-GENERATE-LOAN-NUMBER
           
      *    SET LOAN APPLICATION DATA
           MOVE 1234567890 TO WS-CUSTOMER-ID-WORK
           MOVE 200000000.00 TO WS-LOAN-AMOUNT-WORK
           
      *    VALIDATE CUSTOMER EXISTS AND IS ELIGIBLE
           MOVE WS-CUSTOMER-ID-WORK TO SQL-CUSTOMER-ID
           
           EXEC SQL
               SELECT CUSTOMER_STATUS, CREDIT_SCORE
               INTO :SQL-CUSTOMER-STATUS, :SQL-CREDIT-SCORE
               FROM COBOL.CUSTOMER
               WHERE CUSTOMER_ID = :SQL-CUSTOMER-ID
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'CUSTOMER NOT FOUND'
               MOVE ERR-CUSTOMER-NOT-FOUND TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2100-EXIT
           END-IF
           
      *    CHECK CUSTOMER STATUS
           IF SQL-CUSTOMER-STATUS NOT = 'A'
               DISPLAY 'CUSTOMER IS NOT ACTIVE'
               MOVE ERR-CUSTOMER-BLOCKED TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2100-EXIT
           END-IF
           
      *    CHECK CREDIT SCORE
           IF SQL-CREDIT-SCORE < 550
               DISPLAY 'CREDIT SCORE TOO LOW: ' SQL-CREDIT-SCORE
               MOVE ERR-LOAN-LIMIT-EXCEEDED TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2100-EXIT
           END-IF
           
      *    CALCULATE INTEREST RATE BASED ON CREDIT SCORE
           IF SQL-CREDIT-SCORE >= 750
               MOVE 8.5000 TO SQL-INTEREST-RATE
           ELSE IF SQL-CREDIT-SCORE >= 650
               MOVE 10.5000 TO SQL-INTEREST-RATE
           ELSE
               MOVE 12.5000 TO SQL-INTEREST-RATE
           END-IF
           
      *    SET LOAN TERM (60 MONTHS = 5 YEARS)
           MOVE 60 TO SQL-LOAN-TERM
           
      *    CALCULATE MONTHLY INSTALLMENT
           PERFORM 2120-CALCULATE-INSTALLMENT
           
      *    INSERT LOAN APPLICATION
           MOVE WS-NEW-LOAN-NUMBER TO SQL-LOAN-NUMBER
           MOVE 'PER' TO SQL-LOAN-TYPE
           MOVE WS-CUSTOMER-ID-WORK TO SQL-CUSTOMER-ID
           MOVE WS-LOAN-AMOUNT-WORK TO SQL-ORIGINAL-AMOUNT
           MOVE 'P' TO SQL-LOAN-STATUS
           
           EXEC SQL
               INSERT INTO COBOL.LOAN (
                   LOAN_NUMBER, LOAN_TYPE, CUSTOMER_ID,
                   LOAN_STATUS, LOAN_CURRENCY, ORIGINAL_AMOUNT,
                   INTEREST_RATE, INTEREST_TYPE, LOAN_TERM_MONTHS,
                   PAYMENT_FREQUENCY, INSTALLMENT_AMOUNT,
                   APPLICATION_DATE, PAYMENTS_REMAINING,
                   DELINQUENCY_STATUS
               ) VALUES (
                   :SQL-LOAN-NUMBER, :SQL-LOAN-TYPE, :SQL-CUSTOMER-ID,
                   'P', 'IDR', :SQL-ORIGINAL-AMOUNT,
                   :SQL-INTEREST-RATE, 'F', :SQL-LOAN-TERM,
                   'M', :SQL-INSTALLMENT-AMOUNT,
                   CURRENT_DATE, :SQL-LOAN-TERM, 'C'
               )
           END-EXEC
           
           IF SQLCODE = 0
               EXEC SQL COMMIT END-EXEC
               DISPLAY 'LOAN APPLICATION CREATED: ' SQL-LOAN-NUMBER
               DISPLAY 'AMOUNT: ' SQL-ORIGINAL-AMOUNT
               DISPLAY 'INTEREST RATE: ' SQL-INTEREST-RATE '%'
               DISPLAY 'MONTHLY INSTALLMENT: ' SQL-INSTALLMENT-AMOUNT
               ADD 1 TO WS-LOANS-APPLIED
               ADD 1 TO WS-LOANS-PROCESSED
           ELSE
               EXEC SQL ROLLBACK END-EXEC
               DISPLAY 'ERROR CREATING LOAN APPLICATION: ' SQLCODE
               MOVE ERR-FILE-WRITE-ERROR TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
           END-IF.
           
       2100-EXIT.
           EXIT.
       
       2110-GENERATE-LOAN-NUMBER.
      *    GENERATE UNIQUE LOAN NUMBER
      *    FORMAT: 3YYYYMMDDXXXX
           COMPUTE WS-NEW-LOAN-NUMBER =
               (3 * 100000000000) +
               (WS-CURR-YEAR * 10000000) +
               (WS-CURR-MONTH * 100000) +
               (WS-CURR-DAY * 1000) +
               FUNCTION RANDOM(1000).
       
       2120-CALCULATE-INSTALLMENT.
      *    CALCULATE MONTHLY INSTALLMENT USING AMORTIZATION FORMULA
      *    PMT = P * [r(1+r)^n] / [(1+r)^n - 1]
      *    WHERE: P = PRINCIPAL, r = MONTHLY RATE, n = MONTHS
           
      *    CONVERT ANNUAL RATE TO MONTHLY RATE
           COMPUTE WS-MONTHLY-RATE = SQL-INTEREST-RATE / 100 / 12
           
      *    SIMPLIFIED CALCULATION FOR DEMO
      *    IN PRODUCTION, USE PROPER AMORTIZATION FORMULA
           COMPUTE SQL-INSTALLMENT-AMOUNT =
               (SQL-ORIGINAL-AMOUNT * WS-MONTHLY-RATE * 1.5) /
               (1 - (1 / (1 + WS-MONTHLY-RATE) ** SQL-LOAN-TERM)).
       
       2200-APPROVE-LOAN-APPLICATION.
           DISPLAY 'APPROVING LOAN APPLICATION...'
           
           MOVE WS-NEW-LOAN-NUMBER TO SQL-LOAN-NUMBER
           
      *    CHECK LOAN EXISTS AND IS PENDING
           EXEC SQL
               SELECT LOAN_STATUS, ORIGINAL_AMOUNT
               INTO :SQL-LOAN-STATUS, :SQL-ORIGINAL-AMOUNT
               FROM COBOL.LOAN
               WHERE LOAN_NUMBER = :SQL-LOAN-NUMBER
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'LOAN NOT FOUND'
               MOVE ERR-LOAN-NOT-FOUND TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2200-EXIT
           END-IF
           
           IF SQL-LOAN-STATUS NOT = 'P'
               DISPLAY 'LOAN IS NOT PENDING APPROVAL'
               MOVE ERR-INVALID-LOAN-TYPE TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2200-EXIT
           END-IF
           
      *    APPROVE LOAN
           EXEC SQL
               UPDATE COBOL.LOAN
               SET LOAN_STATUS = 'A',
                   APPROVAL_DATE = CURRENT_DATE,
                   APPROVER_ID = 'MGR001',
                   UPDATED_DATE = CURRENT_TIMESTAMP
               WHERE LOAN_NUMBER = :SQL-LOAN-NUMBER
           END-EXEC
           
           IF SQLCODE = 0
               EXEC SQL COMMIT END-EXEC
               DISPLAY 'LOAN APPROVED: ' SQL-LOAN-NUMBER
               ADD 1 TO WS-LOANS-APPROVED
               ADD 1 TO WS-LOANS-PROCESSED
           ELSE
               EXEC SQL ROLLBACK END-EXEC
               DISPLAY 'ERROR APPROVING LOAN: ' SQLCODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
           END-IF.
           
       2200-EXIT.
           EXIT.
       
       2300-DISBURSE-LOAN.
           DISPLAY 'DISBURSING LOAN...'
           
           MOVE WS-NEW-LOAN-NUMBER TO SQL-LOAN-NUMBER
           
      *    GET LOAN DETAILS
           EXEC SQL
               SELECT LOAN_STATUS, ORIGINAL_AMOUNT, CUSTOMER_ID
               INTO :SQL-LOAN-STATUS, :SQL-ORIGINAL-AMOUNT,
                    :SQL-CUSTOMER-ID
               FROM COBOL.LOAN
               WHERE LOAN_NUMBER = :SQL-LOAN-NUMBER
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'LOAN NOT FOUND'
               MOVE ERR-LOAN-NOT-FOUND TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2300-EXIT
           END-IF
           
           IF SQL-LOAN-STATUS NOT = 'A'
               DISPLAY 'LOAN IS NOT APPROVED'
               MOVE ERR-INVALID-LOAN-TYPE TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2300-EXIT
           END-IF
           
      *    GET CUSTOMER'S ACCOUNT FOR DISBURSEMENT
           EXEC SQL
               SELECT ACCOUNT_NUMBER
               INTO :SQL-DISB-ACCOUNT
               FROM COBOL.ACCOUNT
               WHERE CUSTOMER_ID = :SQL-CUSTOMER-ID
                 AND ACCOUNT_TYPE = 'SA'
                 AND ACCOUNT_STATUS = 'A'
               FETCH FIRST 1 ROW ONLY
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'NO ACTIVE ACCOUNT FOUND FOR DISBURSEMENT'
               MOVE ERR-ACCOUNT-NOT-FOUND TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2300-EXIT
           END-IF
           
      *    UPDATE ACCOUNT BALANCE (CREDIT LOAN AMOUNT)
           EXEC SQL
               UPDATE COBOL.ACCOUNT
               SET ACCOUNT_BALANCE = ACCOUNT_BALANCE + 
                                     :SQL-ORIGINAL-AMOUNT,
                   AVAILABLE_BALANCE = AVAILABLE_BALANCE + 
                                       :SQL-ORIGINAL-AMOUNT,
                   LAST_TRANSACTION_DATE = CURRENT_DATE,
                   UPDATED_DATE = CURRENT_TIMESTAMP
               WHERE ACCOUNT_NUMBER = :SQL-DISB-ACCOUNT
           END-EXEC
           
           IF SQLCODE NOT = 0
               EXEC SQL ROLLBACK END-EXEC
               DISPLAY 'ERROR UPDATING ACCOUNT: ' SQLCODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2300-EXIT
           END-IF
           
      *    UPDATE LOAN STATUS TO ACTIVE
           EXEC SQL
               UPDATE COBOL.LOAN
               SET LOAN_STATUS = 'A',
                   DISBURSED_AMOUNT = :SQL-ORIGINAL-AMOUNT,
                   OUTSTANDING_PRINCIPAL = :SQL-ORIGINAL-AMOUNT,
                   TOTAL_OUTSTANDING = :SQL-ORIGINAL-AMOUNT,
                   DISBURSEMENT_DATE = CURRENT_DATE,
                   FIRST_PAYMENT_DATE = CURRENT_DATE + 30,
                   NEXT_PAYMENT_DATE = CURRENT_DATE + 30,
                   DISBURSEMENT_ACCOUNT = :SQL-DISB-ACCOUNT,
                   UPDATED_DATE = CURRENT_TIMESTAMP
               WHERE LOAN_NUMBER = :SQL-LOAN-NUMBER
           END-EXEC
           
           IF SQLCODE = 0
               EXEC SQL COMMIT END-EXEC
               DISPLAY 'LOAN DISBURSED: ' SQL-LOAN-NUMBER
               DISPLAY 'AMOUNT: ' SQL-ORIGINAL-AMOUNT
               DISPLAY 'TO ACCOUNT: ' SQL-DISB-ACCOUNT
               ADD 1 TO WS-LOANS-DISBURSED
               ADD 1 TO WS-LOANS-PROCESSED
           ELSE
               EXEC SQL ROLLBACK END-EXEC
               DISPLAY 'ERROR DISBURSING LOAN: ' SQLCODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
           END-IF.
           
       2300-EXIT.
           EXIT.
       
       2400-PROCESS-LOAN-PAYMENT.
           DISPLAY 'PROCESSING LOAN PAYMENT...'
           
           MOVE WS-NEW-LOAN-NUMBER TO SQL-LOAN-NUMBER
           MOVE 5000000.00 TO WS-PAYMENT-AMOUNT-WORK
           
      *    GET LOAN DETAILS
           EXEC SQL
               SELECT OUTSTANDING_PRINCIPAL, OUTSTANDING_INTEREST,
                      INSTALLMENT_AMOUNT, LOAN_STATUS
               INTO :SQL-OUTSTANDING-PRINCIPAL,
                    :SQL-OUTSTANDING-INTEREST,
                    :SQL-INSTALLMENT-AMOUNT,
                    :SQL-LOAN-STATUS
               FROM COBOL.LOAN
               WHERE LOAN_NUMBER = :SQL-LOAN-NUMBER
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'LOAN NOT FOUND'
               MOVE ERR-LOAN-NOT-FOUND TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2400-EXIT
           END-IF
           
           IF SQL-LOAN-STATUS NOT = 'A'
               DISPLAY 'LOAN IS NOT ACTIVE'
               MOVE ERR-LOAN-DEFAULTED TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2400-EXIT
           END-IF
           
      *    ALLOCATE PAYMENT TO INTEREST FIRST, THEN PRINCIPAL
           IF WS-PAYMENT-AMOUNT-WORK >= SQL-OUTSTANDING-INTEREST
               MOVE SQL-OUTSTANDING-INTEREST TO WS-INTEREST-AMOUNT
               COMPUTE WS-PRINCIPAL-AMOUNT = 
                   WS-PAYMENT-AMOUNT-WORK - WS-INTEREST-AMOUNT
           ELSE
               MOVE WS-PAYMENT-AMOUNT-WORK TO WS-INTEREST-AMOUNT
               MOVE ZERO TO WS-PRINCIPAL-AMOUNT
           END-IF
           
      *    UPDATE LOAN BALANCES
           EXEC SQL
               UPDATE COBOL.LOAN
               SET OUTSTANDING_PRINCIPAL = OUTSTANDING_PRINCIPAL - 
                                           :WS-PRINCIPAL-AMOUNT,
                   OUTSTANDING_INTEREST = OUTSTANDING_INTEREST - 
                                          :WS-INTEREST-AMOUNT,
                   TOTAL_OUTSTANDING = TOTAL_OUTSTANDING - 
                                       :WS-PAYMENT-AMOUNT-WORK,
                   TOTAL_PAID_PRINCIPAL = TOTAL_PAID_PRINCIPAL + 
                                          :WS-PRINCIPAL-AMOUNT,
                   TOTAL_PAID_INTEREST = TOTAL_PAID_INTEREST + 
                                         :WS-INTEREST-AMOUNT,
                   TOTAL_PAYMENTS_MADE = TOTAL_PAYMENTS_MADE + 1,
                   PAYMENTS_REMAINING = PAYMENTS_REMAINING - 1,
                   LAST_PAYMENT_DATE = CURRENT_DATE,
                   LAST_PAYMENT_AMOUNT = :WS-PAYMENT-AMOUNT-WORK,
                   NEXT_PAYMENT_DATE = CURRENT_DATE + 30,
                   UPDATED_DATE = CURRENT_TIMESTAMP
               WHERE LOAN_NUMBER = :SQL-LOAN-NUMBER
           END-EXEC
           
           IF SQLCODE = 0
               EXEC SQL COMMIT END-EXEC
               DISPLAY 'PAYMENT PROCESSED: ' SQL-LOAN-NUMBER
               DISPLAY 'PAYMENT AMOUNT: ' WS-PAYMENT-AMOUNT-WORK
               DISPLAY 'PRINCIPAL PAID: ' WS-PRINCIPAL-AMOUNT
               DISPLAY 'INTEREST PAID: ' WS-INTEREST-AMOUNT
               ADD 1 TO WS-PAYMENTS-PROCESSED
               ADD 1 TO WS-LOANS-PROCESSED
           ELSE
               EXEC SQL ROLLBACK END-EXEC
               DISPLAY 'ERROR PROCESSING PAYMENT: ' SQLCODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
           END-IF.
           
       2400-EXIT.
           EXIT.
       
       2500-CALCULATE-INTEREST.
           DISPLAY 'CALCULATING ACCRUED INTEREST...'
           
           MOVE WS-NEW-LOAN-NUMBER TO SQL-LOAN-NUMBER
           
      *    GET LOAN DETAILS
           EXEC SQL
               SELECT OUTSTANDING_PRINCIPAL, INTEREST_RATE
               INTO :SQL-OUTSTANDING-PRINCIPAL, :SQL-INTEREST-RATE
               FROM COBOL.LOAN
               WHERE LOAN_NUMBER = :SQL-LOAN-NUMBER
                 AND LOAN_STATUS = 'A'
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'LOAN NOT FOUND OR NOT ACTIVE'
               GO TO 2500-EXIT
           END-IF
           
      *    CALCULATE MONTHLY INTEREST
      *    FORMULA: PRINCIPAL * (ANNUAL RATE / 12 / 100)
           COMPUTE WS-INTEREST-AMOUNT =
               SQL-OUTSTANDING-PRINCIPAL * 
               (SQL-INTEREST-RATE / 12 / 100)
           
      *    UPDATE OUTSTANDING INTEREST
           EXEC SQL
               UPDATE COBOL.LOAN
               SET OUTSTANDING_INTEREST = OUTSTANDING_INTEREST + 
                                          :WS-INTEREST-AMOUNT,
                   TOTAL_OUTSTANDING = TOTAL_OUTSTANDING + 
                                       :WS-INTEREST-AMOUNT,
                   LAST_INTEREST_DATE = CURRENT_DATE,
                   UPDATED_DATE = CURRENT_TIMESTAMP
               WHERE LOAN_NUMBER = :SQL-LOAN-NUMBER
           END-EXEC
           
           IF SQLCODE = 0
               EXEC SQL COMMIT END-EXEC
               DISPLAY 'INTEREST CALCULATED: ' SQL-LOAN-NUMBER
               DISPLAY 'INTEREST AMOUNT: ' WS-INTEREST-AMOUNT
           ELSE
               EXEC SQL ROLLBACK END-EXEC
               DISPLAY 'ERROR CALCULATING INTEREST: ' SQLCODE
           END-IF.
           
       2500-EXIT.
           EXIT.
       
       3000-FINALIZE.
           DISPLAY '========================================='
           DISPLAY 'LOAN PROCESSING SYSTEM - SUMMARY'
           DISPLAY '========================================='
           DISPLAY 'TOTAL LOANS PROCESSED: ' WS-LOANS-PROCESSED
           DISPLAY 'LOAN APPLICATIONS: ' WS-LOANS-APPLIED
           DISPLAY 'LOANS APPROVED: ' WS-LOANS-APPROVED
           DISPLAY 'LOANS DISBURSED: ' WS-LOANS-DISBURSED
           DISPLAY 'PAYMENTS PROCESSED: ' WS-PAYMENTS-PROCESSED
           DISPLAY 'ERRORS ENCOUNTERED: ' WS-ERRORS-ENCOUNTERED
           DISPLAY '========================================='
           
           EXEC SQL DISCONNECT END-EXEC.
       
       9999-ABNORMAL-TERMINATION.
           DISPLAY '========================================='
           DISPLAY 'ABNORMAL TERMINATION'
           DISPLAY 'ERROR CODE: ' WS-RETURN-CODE
           DISPLAY '========================================='
           EXEC SQL ROLLBACK END-EXEC
           EXEC SQL DISCONNECT END-EXEC
           STOP RUN.

* Made with Bob
