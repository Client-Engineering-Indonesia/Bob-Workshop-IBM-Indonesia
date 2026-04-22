       IDENTIFICATION DIVISION.
       PROGRAM-ID. CUSTINFO.
       AUTHOR. LEGACY BANKING SYSTEMS.
      ******************************************************************
      * CUSTOMER INFORMATION SYSTEM                                    *
      * Description: Manages customer profiles and KYC information     *
      * Dependencies: CUSTREC.CPY, ERRCODE.CPY                        *
      * Database: PostgreSQL via EXEC SQL                             *
      ******************************************************************
       
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-370.
       OBJECT-COMPUTER. IBM-370.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       COPY CUSTREC.
       COPY ERRCODE.
       
       EXEC SQL INCLUDE SQLCA END-EXEC.
       
       01  WS-OPERATION-CODE              PIC X(02).
           88  CREATE-CUSTOMER            VALUE 'CR'.
           88  UPDATE-CUSTOMER            VALUE 'UP'.
           88  INQUIRY-CUSTOMER           VALUE 'IN'.
           88  BLOCK-CUSTOMER             VALUE 'BL'.
           88  UPDATE-KYC                 VALUE 'KY'.
       
       01  WS-WORK-FIELDS.
           05  WS-CURRENT-DATE.
               10  WS-CURR-YEAR           PIC 9(04).
               10  WS-CURR-MONTH          PIC 9(02).
               10  WS-CURR-DAY            PIC 9(02).
           05  WS-FORMATTED-DATE          PIC 9(08).
           05  WS-RETURN-CODE             PIC X(04).
           05  WS-ERROR-MESSAGE           PIC X(100).
           05  WS-SQL-CODE                PIC S9(9) COMP.
       
       01  WS-CUSTOMER-WORK-AREA.
           05  WS-NEW-CUST-ID             PIC 9(10).
           05  WS-SEARCH-CUST-ID          PIC 9(10).
           05  WS-SEARCH-ID-NUMBER        PIC X(20).
           05  WS-AGE                     PIC 9(03).
           05  WS-CREDIT-LIMIT            PIC S9(13)V99 COMP-3.
       
       01  WS-COUNTERS.
           05  WS-CUSTOMERS-PROCESSED     PIC 9(08) VALUE ZERO.
           05  WS-CUSTOMERS-CREATED       PIC 9(08) VALUE ZERO.
           05  WS-CUSTOMERS-UPDATED       PIC 9(08) VALUE ZERO.
           05  WS-KYC-UPDATES             PIC 9(08) VALUE ZERO.
           05  WS-ERRORS-ENCOUNTERED      PIC 9(08) VALUE ZERO.
       
       01  WS-SQL-VARIABLES.
           05  SQL-CUSTOMER-ID            PIC 9(10).
           05  SQL-TITLE                  PIC X(05).
           05  SQL-FIRST-NAME             PIC X(30).
           05  SQL-MIDDLE-NAME            PIC X(30).
           05  SQL-LAST-NAME              PIC X(30).
           05  SQL-FULL-NAME              PIC X(100).
           05  SQL-DOB                    PIC X(10).
           05  SQL-GENDER                 PIC X(01).
           05  SQL-MARITAL-STATUS         PIC X(01).
           05  SQL-NATIONALITY            PIC X(03).
           05  SQL-ID-TYPE                PIC X(03).
           05  SQL-ID-NUMBER              PIC X(20).
           05  SQL-EMAIL                  PIC X(60).
           05  SQL-MOBILE                 PIC X(20).
           05  SQL-ANNUAL-INCOME          PIC S9(13)V99 COMP-3.
           05  SQL-CUSTOMER-STATUS        PIC X(01).
           05  SQL-CREDIT-SCORE           PIC 9(04).
           05  SQL-KYC-STATUS             PIC X(01).
       
       PROCEDURE DIVISION.
       0000-MAIN-PROCESS.
           PERFORM 1000-INITIALIZE
           PERFORM 2000-PROCESS-CUSTOMERS
           PERFORM 3000-FINALIZE
           STOP RUN.
       
       1000-INITIALIZE.
           DISPLAY '========================================='
           DISPLAY 'CUSTOMER INFORMATION SYSTEM - STARTING'
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
       
       2000-PROCESS-CUSTOMERS.
           DISPLAY 'PROCESSING CUSTOMER OPERATIONS...'
           
      *    THIS SECTION DEMONSTRATES VARIOUS CUSTOMER OPERATIONS
      *    IN PRODUCTION, INPUT WOULD COME FROM:
      *    - ONLINE TERMINALS (CICS/IMS)
      *    - BATCH INPUT FILES
      *    - WEB SERVICES
           
           PERFORM 2100-CREATE-NEW-CUSTOMER
           PERFORM 2200-UPDATE-CUSTOMER-INFO
           PERFORM 2300-INQUIRY-CUSTOMER
           PERFORM 2400-UPDATE-KYC-STATUS
           PERFORM 2500-CALCULATE-CREDIT-LIMIT.
       
       2100-CREATE-NEW-CUSTOMER.
           DISPLAY 'CREATING NEW CUSTOMER...'
           
      *    GENERATE NEW CUSTOMER ID
           PERFORM 2110-GENERATE-CUSTOMER-ID
           
      *    CHECK FOR DUPLICATE ID NUMBER
           MOVE '3201011505850001' TO WS-SEARCH-ID-NUMBER
           
           EXEC SQL
               SELECT CUSTOMER_ID
               INTO :SQL-CUSTOMER-ID
               FROM COBOL.CUSTOMER
               WHERE ID_NUMBER = :WS-SEARCH-ID-NUMBER
           END-EXEC
           
           IF SQLCODE = 0
               DISPLAY 'DUPLICATE ID NUMBER FOUND'
               MOVE ERR-DUPLICATE-CUSTOMER TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2100-EXIT
           END-IF
           
      *    PREPARE CUSTOMER DATA
           MOVE WS-NEW-CUST-ID TO SQL-CUSTOMER-ID
           MOVE 'Mr.' TO SQL-TITLE
           MOVE 'John' TO SQL-FIRST-NAME
           MOVE 'Michael' TO SQL-MIDDLE-NAME
           MOVE 'Doe' TO SQL-LAST-NAME
           MOVE 'John Michael Doe' TO SQL-FULL-NAME
           MOVE '1985-05-15' TO SQL-DOB
           MOVE 'M' TO SQL-GENDER
           MOVE 'M' TO SQL-MARITAL-STATUS
           MOVE 'IDN' TO SQL-NATIONALITY
           MOVE 'KTP' TO SQL-ID-TYPE
           MOVE WS-SEARCH-ID-NUMBER TO SQL-ID-NUMBER
           MOVE 'john.doe@email.com' TO SQL-EMAIL
           MOVE '081234567890' TO SQL-MOBILE
           MOVE 150000000.00 TO SQL-ANNUAL-INCOME
           MOVE 'A' TO SQL-CUSTOMER-STATUS
           MOVE 700 TO SQL-CREDIT-SCORE
           MOVE 'P' TO SQL-KYC-STATUS
           
      *    INSERT NEW CUSTOMER
           EXEC SQL
               INSERT INTO COBOL.CUSTOMER (
                   CUSTOMER_ID, TITLE, FIRST_NAME, MIDDLE_NAME,
                   LAST_NAME, FULL_NAME, DATE_OF_BIRTH, GENDER,
                   MARITAL_STATUS, NATIONALITY, ID_TYPE, ID_NUMBER,
                   EMAIL, MOBILE_PHONE, ANNUAL_INCOME,
                   CUSTOMER_STATUS, CREDIT_SCORE, KYC_STATUS,
                   CUSTOMER_SINCE, CUSTOMER_SEGMENT
               ) VALUES (
                   :SQL-CUSTOMER-ID, :SQL-TITLE, :SQL-FIRST-NAME,
                   :SQL-MIDDLE-NAME, :SQL-LAST-NAME, :SQL-FULL-NAME,
                   :SQL-DOB, :SQL-GENDER, :SQL-MARITAL-STATUS,
                   :SQL-NATIONALITY, :SQL-ID-TYPE, :SQL-ID-NUMBER,
                   :SQL-EMAIL, :SQL-MOBILE, :SQL-ANNUAL-INCOME,
                   :SQL-CUSTOMER-STATUS, :SQL-CREDIT-SCORE,
                   :SQL-KYC-STATUS, CURRENT_DATE, 'RET'
               )
           END-EXEC
           
           IF SQLCODE = 0
               EXEC SQL COMMIT END-EXEC
               DISPLAY 'CUSTOMER CREATED: ' SQL-CUSTOMER-ID
               ADD 1 TO WS-CUSTOMERS-CREATED
               ADD 1 TO WS-CUSTOMERS-PROCESSED
           ELSE
               EXEC SQL ROLLBACK END-EXEC
               DISPLAY 'ERROR CREATING CUSTOMER: ' SQLCODE
               MOVE ERR-FILE-WRITE-ERROR TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
           END-IF.
           
       2100-EXIT.
           EXIT.
       
       2110-GENERATE-CUSTOMER-ID.
      *    IN PRODUCTION, USE SEQUENCE OR AUTO-INCREMENT
      *    FOR DEMO, USE TIMESTAMP-BASED ID
           COMPUTE WS-NEW-CUST-ID =
               (WS-CURR-YEAR * 1000000) +
               (WS-CURR-MONTH * 10000) +
               (WS-CURR-DAY * 100) +
               FUNCTION RANDOM(1000).
       
       2200-UPDATE-CUSTOMER-INFO.
           DISPLAY 'UPDATING CUSTOMER INFORMATION...'
           
           MOVE WS-NEW-CUST-ID TO SQL-CUSTOMER-ID
           
      *    CHECK IF CUSTOMER EXISTS
           EXEC SQL
               SELECT CUSTOMER_STATUS
               INTO :SQL-CUSTOMER-STATUS
               FROM COBOL.CUSTOMER
               WHERE CUSTOMER_ID = :SQL-CUSTOMER-ID
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'CUSTOMER NOT FOUND'
               MOVE ERR-CUSTOMER-NOT-FOUND TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2200-EXIT
           END-IF
           
      *    CHECK IF CUSTOMER IS BLOCKED
           IF SQL-CUSTOMER-STATUS = 'B'
               DISPLAY 'CUSTOMER IS BLOCKED'
               MOVE ERR-CUSTOMER-BLOCKED TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2200-EXIT
           END-IF
           
      *    UPDATE CUSTOMER INFORMATION
           MOVE 'john.doe.updated@email.com' TO SQL-EMAIL
           MOVE '081298765432' TO SQL-MOBILE
           MOVE 180000000.00 TO SQL-ANNUAL-INCOME
           
           EXEC SQL
               UPDATE COBOL.CUSTOMER
               SET EMAIL = :SQL-EMAIL,
                   MOBILE_PHONE = :SQL-MOBILE,
                   ANNUAL_INCOME = :SQL-ANNUAL-INCOME,
                   UPDATED_DATE = CURRENT_TIMESTAMP
               WHERE CUSTOMER_ID = :SQL-CUSTOMER-ID
           END-EXEC
           
           IF SQLCODE = 0
               EXEC SQL COMMIT END-EXEC
               DISPLAY 'CUSTOMER UPDATED: ' SQL-CUSTOMER-ID
               ADD 1 TO WS-CUSTOMERS-UPDATED
               ADD 1 TO WS-CUSTOMERS-PROCESSED
           ELSE
               EXEC SQL ROLLBACK END-EXEC
               DISPLAY 'ERROR UPDATING CUSTOMER: ' SQLCODE
               MOVE ERR-FILE-WRITE-ERROR TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
           END-IF.
           
       2200-EXIT.
           EXIT.
       
       2300-INQUIRY-CUSTOMER.
           DISPLAY 'CUSTOMER INQUIRY...'
           
           MOVE WS-NEW-CUST-ID TO SQL-CUSTOMER-ID
           
           EXEC SQL
               SELECT CUSTOMER_ID, FULL_NAME, EMAIL, MOBILE_PHONE,
                      CUSTOMER_STATUS, CREDIT_SCORE, KYC_STATUS,
                      ANNUAL_INCOME
               INTO :SQL-CUSTOMER-ID, :SQL-FULL-NAME, :SQL-EMAIL,
                    :SQL-MOBILE, :SQL-CUSTOMER-STATUS,
                    :SQL-CREDIT-SCORE, :SQL-KYC-STATUS,
                    :SQL-ANNUAL-INCOME
               FROM COBOL.CUSTOMER
               WHERE CUSTOMER_ID = :SQL-CUSTOMER-ID
           END-EXEC
           
           IF SQLCODE = 0
               DISPLAY 'CUSTOMER ID: ' SQL-CUSTOMER-ID
               DISPLAY 'FULL NAME: ' SQL-FULL-NAME
               DISPLAY 'EMAIL: ' SQL-EMAIL
               DISPLAY 'MOBILE: ' SQL-MOBILE
               DISPLAY 'STATUS: ' SQL-CUSTOMER-STATUS
               DISPLAY 'CREDIT SCORE: ' SQL-CREDIT-SCORE
               DISPLAY 'KYC STATUS: ' SQL-KYC-STATUS
               DISPLAY 'ANNUAL INCOME: ' SQL-ANNUAL-INCOME
               ADD 1 TO WS-CUSTOMERS-PROCESSED
           ELSE
               DISPLAY 'CUSTOMER NOT FOUND'
               MOVE ERR-CUSTOMER-NOT-FOUND TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
           END-IF.
       
       2300-EXIT.
           EXIT.
       
       2400-UPDATE-KYC-STATUS.
           DISPLAY 'UPDATING KYC STATUS...'
           
           MOVE WS-NEW-CUST-ID TO SQL-CUSTOMER-ID
           
      *    CHECK CURRENT KYC STATUS
           EXEC SQL
               SELECT KYC_STATUS
               INTO :SQL-KYC-STATUS
               FROM COBOL.CUSTOMER
               WHERE CUSTOMER_ID = :SQL-CUSTOMER-ID
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'CUSTOMER NOT FOUND'
               MOVE ERR-CUSTOMER-NOT-FOUND TO WS-RETURN-CODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
               GO TO 2400-EXIT
           END-IF
           
      *    UPDATE KYC TO COMPLETE
           MOVE 'C' TO SQL-KYC-STATUS
           
           EXEC SQL
               UPDATE COBOL.CUSTOMER
               SET KYC_STATUS = :SQL-KYC-STATUS,
                   KYC_DATE = CURRENT_DATE,
                   LAST_REVIEW_DATE = CURRENT_DATE,
                   UPDATED_DATE = CURRENT_TIMESTAMP
               WHERE CUSTOMER_ID = :SQL-CUSTOMER-ID
           END-EXEC
           
           IF SQLCODE = 0
               EXEC SQL COMMIT END-EXEC
               DISPLAY 'KYC STATUS UPDATED: ' SQL-CUSTOMER-ID
               ADD 1 TO WS-KYC-UPDATES
               ADD 1 TO WS-CUSTOMERS-PROCESSED
           ELSE
               EXEC SQL ROLLBACK END-EXEC
               DISPLAY 'ERROR UPDATING KYC: ' SQLCODE
               ADD 1 TO WS-ERRORS-ENCOUNTERED
           END-IF.
           
       2400-EXIT.
           EXIT.
       
       2500-CALCULATE-CREDIT-LIMIT.
           DISPLAY 'CALCULATING CREDIT LIMIT...'
           
           MOVE WS-NEW-CUST-ID TO SQL-CUSTOMER-ID
           
      *    GET CUSTOMER FINANCIAL INFO
           EXEC SQL
               SELECT ANNUAL_INCOME, CREDIT_SCORE
               INTO :SQL-ANNUAL-INCOME, :SQL-CREDIT-SCORE
               FROM COBOL.CUSTOMER
               WHERE CUSTOMER_ID = :SQL-CUSTOMER-ID
           END-EXEC
           
           IF SQLCODE NOT = 0
               DISPLAY 'CUSTOMER NOT FOUND'
               GO TO 2500-EXIT
           END-IF
           
      *    CALCULATE CREDIT LIMIT BASED ON INCOME AND SCORE
      *    FORMULA: (ANNUAL INCOME * 30%) * SCORE FACTOR
           IF SQL-CREDIT-SCORE >= 750
               COMPUTE WS-CREDIT-LIMIT = SQL-ANNUAL-INCOME * 0.30
           ELSE IF SQL-CREDIT-SCORE >= 650
               COMPUTE WS-CREDIT-LIMIT = SQL-ANNUAL-INCOME * 0.20
           ELSE IF SQL-CREDIT-SCORE >= 550
               COMPUTE WS-CREDIT-LIMIT = SQL-ANNUAL-INCOME * 0.10
           ELSE
               MOVE ZERO TO WS-CREDIT-LIMIT
           END-IF
           
           DISPLAY 'CUSTOMER: ' SQL-CUSTOMER-ID
           DISPLAY 'ANNUAL INCOME: ' SQL-ANNUAL-INCOME
           DISPLAY 'CREDIT SCORE: ' SQL-CREDIT-SCORE
           DISPLAY 'CALCULATED CREDIT LIMIT: ' WS-CREDIT-LIMIT.
           
       2500-EXIT.
           EXIT.
       
       3000-FINALIZE.
           DISPLAY '========================================='
           DISPLAY 'CUSTOMER INFORMATION SYSTEM - SUMMARY'
           DISPLAY '========================================='
           DISPLAY 'TOTAL CUSTOMERS PROCESSED: ' 
                   WS-CUSTOMERS-PROCESSED
           DISPLAY 'CUSTOMERS CREATED: ' WS-CUSTOMERS-CREATED
           DISPLAY 'CUSTOMERS UPDATED: ' WS-CUSTOMERS-UPDATED
           DISPLAY 'KYC UPDATES: ' WS-KYC-UPDATES
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
