      ******************************************************************
      * ERROR CODE DEFINITIONS                                         *
      * Description: Standard error codes used across all programs     *
      * Used by: All programs                                          *
      ******************************************************************
       01  ERROR-CODES.
           05  ERR-SUCCESS                PIC X(04) VALUE '0000'.
           05  ERR-ACCOUNT-NOT-FOUND      PIC X(04) VALUE '1001'.
           05  ERR-ACCOUNT-CLOSED         PIC X(04) VALUE '1002'.
           05  ERR-ACCOUNT-FROZEN         PIC X(04) VALUE '1003'.
           05  ERR-INSUFFICIENT-FUNDS     PIC X(04) VALUE '1004'.
           05  ERR-INVALID-AMOUNT         PIC X(04) VALUE '1005'.
           05  ERR-DAILY-LIMIT-EXCEEDED   PIC X(04) VALUE '1006'.
           05  ERR-CUSTOMER-NOT-FOUND     PIC X(04) VALUE '2001'.
           05  ERR-CUSTOMER-BLOCKED       PIC X(04) VALUE '2002'.
           05  ERR-KYC-EXPIRED            PIC X(04) VALUE '2003'.
           05  ERR-DUPLICATE-CUSTOMER     PIC X(04) VALUE '2004'.
           05  ERR-LOAN-NOT-FOUND         PIC X(04) VALUE '3001'.
           05  ERR-LOAN-DEFAULTED         PIC X(04) VALUE '3002'.
           05  ERR-LOAN-LIMIT-EXCEEDED    PIC X(04) VALUE '3003'.
           05  ERR-INVALID-LOAN-TYPE      PIC X(04) VALUE '3004'.
           05  ERR-TRANSACTION-FAILED     PIC X(04) VALUE '4001'.
           05  ERR-DUPLICATE-TRANSACTION  PIC X(04) VALUE '4002'.
           05  ERR-INVALID-TRANSACTION    PIC X(04) VALUE '4003'.
           05  ERR-AUTHORIZATION-FAILED   PIC X(04) VALUE '4004'.
           05  ERR-FILE-NOT-FOUND         PIC X(04) VALUE '5001'.
           05  ERR-FILE-OPEN-ERROR        PIC X(04) VALUE '5002'.
           05  ERR-FILE-READ-ERROR        PIC X(04) VALUE '5003'.
           05  ERR-FILE-WRITE-ERROR       PIC X(04) VALUE '5004'.
           05  ERR-SYSTEM-ERROR           PIC X(04) VALUE '9999'.
           
       01  ERROR-MESSAGES.
           05  ERR-MSG-SUCCESS            PIC X(50) 
               VALUE 'OPERATION COMPLETED SUCCESSFULLY'.
           05  ERR-MSG-ACCT-NOT-FOUND     PIC X(50)
               VALUE 'ACCOUNT NUMBER NOT FOUND'.
           05  ERR-MSG-ACCT-CLOSED        PIC X(50)
               VALUE 'ACCOUNT IS CLOSED'.
           05  ERR-MSG-ACCT-FROZEN        PIC X(50)
               VALUE 'ACCOUNT IS FROZEN'.
           05  ERR-MSG-INSUFF-FUNDS       PIC X(50)
               VALUE 'INSUFFICIENT FUNDS'.
           05  ERR-MSG-INVALID-AMT        PIC X(50)
               VALUE 'INVALID TRANSACTION AMOUNT'.
           05  ERR-MSG-LIMIT-EXCEEDED     PIC X(50)
               VALUE 'DAILY TRANSACTION LIMIT EXCEEDED'.
           05  ERR-MSG-CUST-NOT-FOUND     PIC X(50)
               VALUE 'CUSTOMER NOT FOUND'.
           05  ERR-MSG-CUST-BLOCKED       PIC X(50)
               VALUE 'CUSTOMER ACCOUNT IS BLOCKED'.
           05  ERR-MSG-KYC-EXPIRED        PIC X(50)
               VALUE 'KYC DOCUMENTATION HAS EXPIRED'.
           05  ERR-MSG-SYSTEM-ERROR       PIC X(50)
               VALUE 'SYSTEM ERROR - CONTACT SUPPORT'.
