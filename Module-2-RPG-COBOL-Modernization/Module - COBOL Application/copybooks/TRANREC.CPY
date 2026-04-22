      ******************************************************************
      * TRANSACTION RECORD COPYBOOK                                    *
      * Description: Defines transaction record structure              *
      * Used by: TRANPROC, BATCHEOD, ACCTMGMT                         *
      ******************************************************************
       01  TRANSACTION-RECORD.
           05  TRAN-KEY.
               10  TRAN-ID                PIC 9(16).
           05  TRAN-DETAILS.
               10  TRAN-TYPE              PIC X(03).
                   88  DEPOSIT            VALUE 'DEP'.
                   88  WITHDRAWAL         VALUE 'WDL'.
                   88  TRANSFER           VALUE 'TRF'.
                   88  FEE-CHARGE         VALUE 'FEE'.
                   88  INTEREST-CREDIT    VALUE 'INT'.
                   88  LOAN-DISBURSEMENT  VALUE 'LDB'.
                   88  LOAN-PAYMENT       VALUE 'LPY'.
               10  TRAN-DATE              PIC 9(08).
               10  TRAN-TIME              PIC 9(06).
               10  TRAN-TIMESTAMP         PIC X(26).
               10  VALUE-DATE             PIC 9(08).
               10  TRAN-AMOUNT            PIC S9(13)V99 COMP-3.
               10  TRAN-CURRENCY          PIC X(03).
               10  EXCHANGE-RATE          PIC 9(05)V9(06) COMP-3.
               10  LOCAL-AMOUNT           PIC S9(13)V99 COMP-3.
           05  TRAN-ACCOUNT-INFO.
               10  FROM-ACCOUNT           PIC 9(12).
               10  TO-ACCOUNT             PIC 9(12).
               10  FROM-BALANCE-BEFORE    PIC S9(13)V99 COMP-3.
               10  FROM-BALANCE-AFTER     PIC S9(13)V99 COMP-3.
               10  TO-BALANCE-BEFORE      PIC S9(13)V99 COMP-3.
               10  TO-BALANCE-AFTER       PIC S9(13)V99 COMP-3.
           05  TRAN-PROCESSING-INFO.
               10  TRAN-STATUS            PIC X(01).
                   88  TRAN-PENDING       VALUE 'P'.
                   88  TRAN-COMPLETED     VALUE 'C'.
                   88  TRAN-FAILED        VALUE 'F'.
                   88  TRAN-REVERSED      VALUE 'R'.
               10  TRAN-CHANNEL           PIC X(03).
                   88  BRANCH-CHANNEL     VALUE 'BRN'.
                   88  ATM-CHANNEL        VALUE 'ATM'.
                   88  ONLINE-CHANNEL     VALUE 'ONL'.
                   88  MOBILE-CHANNEL     VALUE 'MOB'.
                   88  BATCH-CHANNEL      VALUE 'BAT'.
               10  TRAN-BRANCH            PIC 9(04).
               10  TRAN-TERMINAL          PIC X(10).
               10  TRAN-USER-ID           PIC X(08).
               10  TRAN-AUTH-CODE         PIC X(12).
               10  TRAN-REFERENCE         PIC X(20).
               10  TRAN-DESCRIPTION       PIC X(100).
               10  TRAN-REMARKS           PIC X(200).
           05  TRAN-AUDIT-INFO.
               10  POSTED-FLAG            PIC X(01).
                   88  POSTED             VALUE 'Y'.
                   88  NOT-POSTED         VALUE 'N'.
               10  POSTED-DATE            PIC 9(08).
               10  POSTED-TIME            PIC 9(06).
               10  REVERSAL-FLAG          PIC X(01).
               10  ORIGINAL-TRAN-ID       PIC 9(16).
               10  ERROR-CODE             PIC X(04).
               10  ERROR-MESSAGE          PIC X(100).
           05  FILLER                     PIC X(50).
