      ******************************************************************
      * LOAN RECORD COPYBOOK                                           *
      * Description: Defines loan account structure                    *
      * Used by: LOANPROC, INTCALC, BATCHEOD                          *
      ******************************************************************
       01  LOAN-RECORD.
           05  LOAN-KEY.
               10  LOAN-NUMBER            PIC 9(12).
           05  LOAN-DETAILS.
               10  LOAN-TYPE              PIC X(03).
                   88  PERSONAL-LOAN      VALUE 'PER'.
                   88  HOME-LOAN          VALUE 'HOM'.
                   88  AUTO-LOAN          VALUE 'AUT'.
                   88  BUSINESS-LOAN      VALUE 'BUS'.
                   88  CREDIT-CARD        VALUE 'CRD'.
               10  CUSTOMER-ID            PIC 9(10).
               10  LOAN-ACCOUNT           PIC 9(12).
               10  DISBURSEMENT-ACCOUNT   PIC 9(12).
               10  LOAN-STATUS            PIC X(01).
                   88  LOAN-ACTIVE        VALUE 'A'.
                   88  LOAN-CLOSED        VALUE 'C'.
                   88  LOAN-DEFAULT       VALUE 'D'.
                   88  LOAN-WRITEOFF      VALUE 'W'.
               10  LOAN-CURRENCY          PIC X(03).
           05  LOAN-AMOUNTS.
               10  ORIGINAL-AMOUNT        PIC S9(13)V99 COMP-3.
               10  DISBURSED-AMOUNT       PIC S9(13)V99 COMP-3.
               10  OUTSTANDING-PRINCIPAL  PIC S9(13)V99 COMP-3.
               10  OUTSTANDING-INTEREST   PIC S9(13)V99 COMP-3.
               10  TOTAL-OUTSTANDING      PIC S9(13)V99 COMP-3.
               10  OVERDUE-PRINCIPAL      PIC S9(13)V99 COMP-3.
               10  OVERDUE-INTEREST       PIC S9(13)V99 COMP-3.
               10  PENALTY-AMOUNT         PIC S9(11)V99 COMP-3.
           05  LOAN-TERMS.
               10  INTEREST-RATE          PIC 9(02)V9(04) COMP-3.
               10  INTEREST-TYPE          PIC X(01).
                   88  FIXED-RATE         VALUE 'F'.
                   88  VARIABLE-RATE      VALUE 'V'.
               10  LOAN-TERM-MONTHS       PIC 9(04).
               10  PAYMENT-FREQUENCY      PIC X(01).
                   88  MONTHLY-PAYMENT    VALUE 'M'.
                   88  QUARTERLY-PAYMENT  VALUE 'Q'.
                   88  ANNUAL-PAYMENT     VALUE 'A'.
               10  INSTALLMENT-AMOUNT     PIC S9(11)V99 COMP-3.
               10  BALLOON-PAYMENT        PIC S9(13)V99 COMP-3.
           05  LOAN-DATES.
               10  APPLICATION-DATE       PIC 9(08).
               10  APPROVAL-DATE          PIC 9(08).
               10  DISBURSEMENT-DATE      PIC 9(08).
               10  FIRST-PAYMENT-DATE     PIC 9(08).
               10  NEXT-PAYMENT-DATE      PIC 9(08).
               10  LAST-PAYMENT-DATE      PIC 9(08).
               10  MATURITY-DATE          PIC 9(08).
               10  LAST-INTEREST-DATE     PIC 9(08).
           05  LOAN-PAYMENT-INFO.
               10  TOTAL-PAYMENTS-MADE    PIC 9(04).
               10  PAYMENTS-REMAINING     PIC 9(04).
               10  LAST-PAYMENT-AMOUNT    PIC S9(11)V99 COMP-3.
               10  LAST-PAYMENT-DATE      PIC 9(08).
               10  TOTAL-PAID-PRINCIPAL   PIC S9(13)V99 COMP-3.
               10  TOTAL-PAID-INTEREST    PIC S9(13)V99 COMP-3.
               10  DAYS-PAST-DUE          PIC 9(04).
               10  DELINQUENCY-STATUS     PIC X(01).
                   88  CURRENT-STATUS     VALUE 'C'.
                   88  DPD-30             VALUE '1'.
                   88  DPD-60             VALUE '2'.
                   88  DPD-90             VALUE '3'.
                   88  DPD-120-PLUS       VALUE '4'.
           05  LOAN-COLLATERAL.
               10  COLLATERAL-TYPE        PIC X(03).
               10  COLLATERAL-VALUE       PIC S9(13)V99 COMP-3.
               10  LTV-RATIO              PIC 9(03)V99 COMP-3.
               10  COLLATERAL-DESC        PIC X(100).
           05  LOAN-OFFICER-INFO.
               10  LOAN-OFFICER-ID        PIC X(08).
               10  APPROVER-ID            PIC X(08).
               10  BRANCH-CODE            PIC 9(04).
           05  FILLER                     PIC X(100).
