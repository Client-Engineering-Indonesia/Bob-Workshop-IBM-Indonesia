      ******************************************************************
      * ACCOUNT RECORD COPYBOOK                                        *
      * Description: Defines the structure for customer accounts       *
      * Used by: ACCTMGMT, TRANPROC, BATCHEOD                         *
      ******************************************************************
       01  ACCOUNT-RECORD.
           05  ACCT-KEY.
               10  ACCT-NUMBER            PIC 9(12).
           05  ACCT-DETAILS.
               10  ACCT-TYPE              PIC X(02).
                   88  SAVINGS-ACCT       VALUE 'SA'.
                   88  CHECKING-ACCT      VALUE 'CA'.
                   88  FIXED-DEPOSIT      VALUE 'FD'.
                   88  LOAN-ACCT          VALUE 'LA'.
               10  ACCT-STATUS            PIC X(01).
                   88  ACTIVE-ACCT        VALUE 'A'.
                   88  DORMANT-ACCT       VALUE 'D'.
                   88  CLOSED-ACCT        VALUE 'C'.
                   88  FROZEN-ACCT        VALUE 'F'.
               10  CUSTOMER-ID            PIC 9(10).
               10  BRANCH-CODE            PIC 9(04).
               10  CURRENCY-CODE          PIC X(03).
               10  ACCT-BALANCE           PIC S9(13)V99 COMP-3.
               10  AVAILABLE-BALANCE      PIC S9(13)V99 COMP-3.
               10  HOLD-AMOUNT            PIC S9(13)V99 COMP-3.
               10  OVERDRAFT-LIMIT        PIC S9(11)V99 COMP-3.
               10  INTEREST-RATE          PIC 9(02)V9(04) COMP-3.
               10  LAST-INTEREST-DATE     PIC 9(08).
               10  ACCT-OPEN-DATE         PIC 9(08).
               10  ACCT-CLOSE-DATE        PIC 9(08).
               10  LAST-TRAN-DATE         PIC 9(08).
               10  LAST-TRAN-TIME         PIC 9(06).
               10  LAST-STATEMENT-DATE    PIC 9(08).
               10  MINIMUM-BALANCE        PIC S9(11)V99 COMP-3.
               10  ACCRUED-INTEREST       PIC S9(11)V99 COMP-3.
               10  YTD-INTEREST           PIC S9(11)V99 COMP-3.
               10  MONTHLY-FEE            PIC S9(07)V99 COMP-3.
               10  LAST-FEE-DATE          PIC 9(08).
               10  ACCT-OFFICER-ID        PIC X(08).
               10  RISK-RATING            PIC X(02).
               10  FILLER                 PIC X(50).
