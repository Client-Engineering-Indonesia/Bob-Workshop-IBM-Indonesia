      ******************************************************************
      * CUSTOMER RECORD COPYBOOK                                       *
      * Description: Defines customer information structure            *
      * Used by: CUSTINFO, ACCTMGMT, LOANPROC                         *
      ******************************************************************
       01  CUSTOMER-RECORD.
           05  CUST-KEY.
               10  CUSTOMER-ID            PIC 9(10).
           05  CUST-PERSONAL-INFO.
               10  CUST-TITLE             PIC X(05).
               10  CUST-FIRST-NAME        PIC X(30).
               10  CUST-MIDDLE-NAME       PIC X(30).
               10  CUST-LAST-NAME         PIC X(30).
               10  CUST-FULL-NAME         PIC X(100).
               10  CUST-DATE-OF-BIRTH     PIC 9(08).
               10  CUST-GENDER            PIC X(01).
                   88  MALE               VALUE 'M'.
                   88  FEMALE             VALUE 'F'.
               10  CUST-MARITAL-STATUS    PIC X(01).
                   88  SINGLE             VALUE 'S'.
                   88  MARRIED            VALUE 'M'.
                   88  DIVORCED           VALUE 'D'.
                   88  WIDOWED            VALUE 'W'.
               10  CUST-NATIONALITY       PIC X(03).
               10  CUST-ID-TYPE           PIC X(03).
               10  CUST-ID-NUMBER         PIC X(20).
               10  CUST-ID-EXPIRY         PIC 9(08).
           05  CUST-CONTACT-INFO.
               10  CUST-ADDRESS-LINE1     PIC X(50).
               10  CUST-ADDRESS-LINE2     PIC X(50).
               10  CUST-CITY              PIC X(30).
               10  CUST-STATE             PIC X(30).
               10  CUST-POSTAL-CODE       PIC X(10).
               10  CUST-COUNTRY           PIC X(03).
               10  CUST-HOME-PHONE        PIC X(20).
               10  CUST-MOBILE-PHONE      PIC X(20).
               10  CUST-EMAIL             PIC X(60).
           05  CUST-EMPLOYMENT-INFO.
               10  CUST-EMPLOYER-NAME     PIC X(50).
               10  CUST-OCCUPATION        PIC X(30).
               10  CUST-ANNUAL-INCOME     PIC S9(13)V99 COMP-3.
               10  CUST-EMPLOYMENT-STATUS PIC X(01).
                   88  EMPLOYED           VALUE 'E'.
                   88  SELF-EMPLOYED      VALUE 'S'.
                   88  UNEMPLOYED         VALUE 'U'.
                   88  RETIRED            VALUE 'R'.
           05  CUST-BANKING-INFO.
               10  CUST-SEGMENT           PIC X(03).
                   88  RETAIL-SEGMENT     VALUE 'RET'.
                   88  PRIORITY-SEGMENT   VALUE 'PRI'.
                   88  WEALTH-SEGMENT     VALUE 'WLT'.
               10  CUST-RELATIONSHIP-MGR  PIC X(08).
               10  CUST-SINCE-DATE        PIC 9(08).
               10  CUST-STATUS            PIC X(01).
                   88  ACTIVE-CUST        VALUE 'A'.
                   88  INACTIVE-CUST      VALUE 'I'.
                   88  BLOCKED-CUST       VALUE 'B'.
               10  CUST-RISK-RATING       PIC X(02).
               10  CUST-CREDIT-SCORE      PIC 9(04).
               10  CUST-KYC-STATUS        PIC X(01).
                   88  KYC-COMPLETE       VALUE 'C'.
                   88  KYC-PENDING        VALUE 'P'.
                   88  KYC-EXPIRED        VALUE 'E'.
               10  CUST-KYC-DATE          PIC 9(08).
               10  CUST-LAST-REVIEW-DATE  PIC 9(08).
           05  FILLER                     PIC X(100).
