package com.bsn.banking.modern;

import com.bsn.banking.modern.dto.*;
import com.bsn.banking.modern.exception.*;
import com.bsn.banking.modern.repository.AccountRepository;
import com.bsn.banking.modern.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Modern Banking Service - Java 17 + Spring Boot 3
 * 
 * Improvements demonstrated:
 * - Java 17 features (records, sealed classes, pattern matching)
 * - Spring Boot 3 with Jakarta EE
 * - Dependency injection
 * - Proper exception handling
 * - Logging framework (SLF4J)
 * - Transaction management
 * - Input validation
 * - DTOs for data transfer
 * - Repository pattern
 * - Separation of concerns
 * - Security best practices
 * - Testable code
 */
@Service
@Slf4j
@RequiredArgsConstructor
@Validated
public class BankingService {
    
    private final AccountRepository accountRepository;
    private final TransactionRepository transactionRepository;
    private final InterestCalculator interestCalculator;
    private final AuditService auditService;
    private final NotificationService notificationService;
    
    // Constants instead of magic numbers
    private static final BigDecimal MAX_TRANSFER_AMOUNT = new BigDecimal("100000000");
    private static final int ACCOUNT_NUMBER_LENGTH = 10;
    
    /**
     * Get account balance with proper error handling
     * 
     * @param accountNumber the account number
     * @return account balance
     * @throws AccountNotFoundException if account doesn't exist
     */
    public BigDecimal getAccountBalance(@NotNull String accountNumber) {
        log.info("Retrieving balance for account: {}", accountNumber);
        
        return accountRepository.findByAccountNumber(accountNumber)
                .map(Account::getBalance)
                .orElseThrow(() -> new AccountNotFoundException(accountNumber));
    }
    
    /**
     * Transfer money between accounts with proper transaction management
     * 
     * @param request transfer request containing from/to accounts and amount
     * @return transfer result with transaction ID
     * @throws InsufficientFundsException if source account has insufficient funds
     * @throws AccountNotFoundException if either account doesn't exist
     * @throws InvalidTransferException if transfer validation fails
     */
    @Transactional(rollbackFor = Exception.class)
    public TransferResult transferMoney(@Valid TransferRequest request) {
        log.info("Processing transfer: {} -> {}, amount: {}", 
                request.fromAccount(), request.toAccount(), request.amount());
        
        // Validate transfer amount
        validateTransferAmount(request.amount());
        
        // Retrieve accounts
        Account fromAccount = getAccountOrThrow(request.fromAccount());
        Account toAccount = getAccountOrThrow(request.toAccount());
        
        // Validate sufficient funds
        if (fromAccount.getBalance().compareTo(request.amount()) < 0) {
            throw new InsufficientFundsException(request.fromAccount(), request.amount());
        }
        
        // Perform transfer
        fromAccount.debit(request.amount());
        toAccount.credit(request.amount());
        
        // Save updated accounts
        accountRepository.save(fromAccount);
        accountRepository.save(toAccount);
        
        // Create transaction records
        Transaction debitTx = createTransaction(fromAccount, TransactionType.DEBIT, request.amount());
        Transaction creditTx = createTransaction(toAccount, TransactionType.CREDIT, request.amount());
        
        transactionRepository.saveAll(List.of(debitTx, creditTx));
        
        // Audit trail
        auditService.logTransfer(fromAccount, toAccount, request.amount());
        
        // Send notifications
        notificationService.notifyTransfer(fromAccount, toAccount, request.amount());
        
        log.info("Transfer completed successfully. Transaction ID: {}", debitTx.getId());
        
        return new TransferResult(
                debitTx.getId(),
                LocalDateTime.now(),
                TransferStatus.SUCCESS,
                "Transfer completed successfully"
        );
    }
    
    /**
     * Get customer information with proper DTO
     * Sensitive data is not exposed
     * 
     * @param customerId the customer ID
     * @return customer information DTO
     * @throws CustomerNotFoundException if customer doesn't exist
     */
    public CustomerDTO getCustomerInfo(@NotNull String customerId) {
        log.info("Retrieving customer info for: {}", customerId);
        
        return accountRepository.findCustomerById(customerId)
                .map(this::mapToCustomerDTO)
                .orElseThrow(() -> new CustomerNotFoundException(customerId));
    }
    
    /**
     * Calculate monthly interest for all savings accounts
     * Business logic separated from data access
     * 
     * @return summary of interest calculation
     */
    @Transactional
    public InterestCalculationSummary calculateMonthlyInterest() {
        log.info("Starting monthly interest calculation");
        
        List<Account> savingsAccounts = accountRepository.findByAccountType(AccountType.SAVINGS);
        
        var results = savingsAccounts.stream()
                .map(this::calculateAndApplyInterest)
                .toList();
        
        var summary = new InterestCalculationSummary(
                results.size(),
                results.stream().map(InterestResult::amount).reduce(BigDecimal.ZERO, BigDecimal::add),
                LocalDateTime.now()
        );
        
        log.info("Interest calculation completed. Accounts processed: {}, Total interest: {}", 
                summary.accountsProcessed(), summary.totalInterest());
        
        return summary;
    }
    
    /**
     * Generate account statement using modern date/time API
     * 
     * @param request statement request with account and date range
     * @return formatted account statement
     */
    public AccountStatement generateStatement(@Valid StatementRequest request) {
        log.info("Generating statement for account: {} from {} to {}", 
                request.accountNumber(), request.startDate(), request.endDate());
        
        Account account = getAccountOrThrow(request.accountNumber());
        
        List<Transaction> transactions = transactionRepository
                .findByAccountNumberAndDateBetween(
                        request.accountNumber(),
                        request.startDate().atStartOfDay(),
                        request.endDate().atTime(23, 59, 59)
                );
        
        var summary = calculateTransactionSummary(transactions);
        
        return new AccountStatement(
                account.getAccountNumber(),
                account.getCustomerName(),
                request.startDate(),
                request.endDate(),
                account.getBalance(),
                transactions.stream().map(this::mapToTransactionDTO).toList(),
                summary
        );
    }
    
    /**
     * Validate account number with proper regex
     * 
     * @param accountNumber the account number to validate
     * @return true if valid, false otherwise
     */
    public boolean validateAccount(String accountNumber) {
        if (accountNumber == null || accountNumber.isBlank()) {
            return false;
        }
        
        // Proper validation with regex
        return accountNumber.matches("\\d{" + ACCOUNT_NUMBER_LENGTH + "}");
    }
    
    // Private helper methods
    
    private void validateTransferAmount(BigDecimal amount) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new InvalidTransferException("Transfer amount must be positive");
        }
        
        if (amount.compareTo(MAX_TRANSFER_AMOUNT) > 0) {
            throw new InvalidTransferException(
                    "Transfer amount exceeds maximum limit of " + MAX_TRANSFER_AMOUNT
            );
        }
    }
    
    private Account getAccountOrThrow(String accountNumber) {
        return accountRepository.findByAccountNumber(accountNumber)
                .orElseThrow(() -> new AccountNotFoundException(accountNumber));
    }
    
    private Transaction createTransaction(Account account, TransactionType type, BigDecimal amount) {
        return Transaction.builder()
                .accountNumber(account.getAccountNumber())
                .transactionType(type)
                .amount(amount)
                .timestamp(LocalDateTime.now())
                .balance(account.getBalance())
                .build();
    }
    
    private InterestResult calculateAndApplyInterest(Account account) {
        BigDecimal interest = interestCalculator.calculateMonthlyInterest(
                account.getBalance(),
                account.getInterestRate()
        );
        
        account.credit(interest);
        accountRepository.save(account);
        
        // Create transaction record
        Transaction interestTx = createTransaction(account, TransactionType.INTEREST, interest);
        transactionRepository.save(interestTx);
        
        log.debug("Interest calculated for account {}: {}", account.getAccountNumber(), interest);
        
        return new InterestResult(account.getAccountNumber(), interest);
    }
    
    private CustomerDTO mapToCustomerDTO(Customer customer) {
        // Map to DTO without exposing sensitive data
        return new CustomerDTO(
                customer.getId(),
                customer.getName(),
                customer.getEmail(),
                customer.getPhone(),
                customer.getAddress()
                // Note: SSN and password are NOT included
        );
    }
    
    private TransactionDTO mapToTransactionDTO(Transaction transaction) {
        return new TransactionDTO(
                transaction.getId(),
                transaction.getTransactionType(),
                transaction.getAmount(),
                transaction.getTimestamp(),
                transaction.getBalance()
        );
    }
    
    private TransactionSummary calculateTransactionSummary(List<Transaction> transactions) {
        BigDecimal totalDebit = transactions.stream()
                .filter(tx -> tx.getTransactionType() == TransactionType.DEBIT)
                .map(Transaction::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        
        BigDecimal totalCredit = transactions.stream()
                .filter(tx -> tx.getTransactionType() == TransactionType.CREDIT)
                .map(Transaction::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        
        return new TransactionSummary(
                transactions.size(),
                totalDebit,
                totalCredit,
                totalCredit.subtract(totalDebit)
        );
    }
}

/**
 * Modern DTOs using Java Records (Java 17 feature)
 */
record TransferRequest(
        @NotNull String fromAccount,
        @NotNull String toAccount,
        @NotNull @Positive BigDecimal amount
) {}

record TransferResult(
        String transactionId,
        LocalDateTime timestamp,
        TransferStatus status,
        String message
) {}

record StatementRequest(
        @NotNull String accountNumber,
        @NotNull LocalDate startDate,
        @NotNull LocalDate endDate
) {}

record InterestResult(
        String accountNumber,
        BigDecimal amount
) {}

record InterestCalculationSummary(
        int accountsProcessed,
        BigDecimal totalInterest,
        LocalDateTime calculationDate
) {}

record TransactionSummary(
        int transactionCount,
        BigDecimal totalDebit,
        BigDecimal totalCredit,
        BigDecimal netAmount
) {}

/**
 * Sealed class for transfer status (Java 17 feature)
 */
sealed interface TransferStatus permits Success, Failed, Pending {
    record Success() implements TransferStatus {}
    record Failed(String reason) implements TransferStatus {}
    record Pending() implements TransferStatus {}
    
    TransferStatus SUCCESS = new Success();
    TransferStatus PENDING = new Pending();
}

/**
 * Enum for transaction types
 */
enum TransactionType {
    DEBIT, CREDIT, INTEREST, FEE
}

/**
 * Enum for account types
 */
enum AccountType {
    SAVINGS, CHECKING, FIXED_DEPOSIT
}

// Made with Bob
