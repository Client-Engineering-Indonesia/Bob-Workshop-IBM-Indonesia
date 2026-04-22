       IDENTIFICATION DIVISION.
       PROGRAM-ID. INITFILE.
      ******************************************************************
      * PROGRAM: INITFILE                                              *
      * PURPOSE: Initialize indexed files for demo                     *
      ******************************************************************
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACCOUNT-FILE
               ASSIGN TO ACCTMAST
               ORGANIZATION IS INDEXED
               ACCESS MODE IS DYNAMIC
               RECORD KEY IS ACCT-NUMBER
               FILE STATUS IS WS-ACCT-STATUS.
               
           SELECT CUSTOMER-FILE
               ASSIGN TO CUSTMAST
               ORGANIZATION IS INDEXED
               ACCESS MODE IS DYNAMIC
               RECORD KEY IS CUST-ID
               FILE STATUS IS WS-CUST-STATUS.
       
       DATA DIVISION.
       FILE SECTION.
       FD  ACCOUNT-FILE.
       01  ACCOUNT-RECORD.
           05  ACCT-NUMBER            PIC 9(12).
           05  FILLER                 PIC X(488).
           
       FD  CUSTOMER-FILE.
       01  CUSTOMER-RECORD.
           05  CUST-ID                PIC 9(10).
           05  FILLER                 PIC X(690).
       
       WORKING-STORAGE SECTION.
       01  WS-ACCT-STATUS             PIC XX.
       01  WS-CUST-STATUS             PIC XX.
       
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           DISPLAY "========================================="
           DISPLAY "INITIALIZING DATA FILES"
           DISPLAY "========================================="
           
           OPEN OUTPUT ACCOUNT-FILE
           IF WS-ACCT-STATUS NOT = "00"
               DISPLAY "ERROR CREATING ACCOUNT FILE: " 
                       WS-ACCT-STATUS
               STOP RUN
           END-IF
           DISPLAY "✓ Account file created"
           CLOSE ACCOUNT-FILE
           
           OPEN OUTPUT CUSTOMER-FILE
           IF WS-CUST-STATUS NOT = "00"
               DISPLAY "ERROR CREATING CUSTOMER FILE: " 
                       WS-CUST-STATUS
               STOP RUN
           END-IF
           DISPLAY "✓ Customer file created"
           CLOSE CUSTOMER-FILE
           
           DISPLAY "========================================="
           DISPLAY "FILES INITIALIZED SUCCESSFULLY"
           DISPLAY "========================================="
           STOP RUN.
