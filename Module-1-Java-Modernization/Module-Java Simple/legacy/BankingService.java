package com.bsn.banking.legacy;

import java.sql.*;
import java.util.*;
import java.text.SimpleDateFormat;

/**
 * Legacy Banking Service - Java 6 Style
 * This represents a typical legacy banking application with common anti-patterns
 * 
 * Issues demonstrated:
 * - Old Java version (6/7 style)
 * - No dependency injection
 * - Direct JDBC usage without connection pooling
 * - SQL injection vulnerabilities
 * - No exception handling best practices
 * - Hardcoded configuration
 * - No logging framework
 * - Tight coupling
 * - No unit tests possible
 */
public class BankingService {
    
    // Hardcoded database credentials (Security Issue!)
    private static final String DB_URL = "jdbc:oracle:thin:@localhost:1521:ORCL";
    private static final String DB_USER = "banking_user";
    private static final String DB_PASSWORD = "P@ssw0rd123"; // Hardcoded password!
    
    private Connection connection;
    
    public BankingService() {
        try {
            // Load JDBC driver (old style)
            Class.forName("oracle.jdbc.driver.OracleDriver");
            connection = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
        } catch (Exception e) {
            e.printStackTrace(); // Poor error handling
        }
    }
    
    /**
     * Get account balance - SQL Injection vulnerable!
     */
    public double getAccountBalance(String accountNumber) {
        double balance = 0.0;
        Statement stmt = null;
        ResultSet rs = null;
        
        try {
            stmt = connection.createStatement();
            // SQL Injection vulnerability - concatenating user input!
            String query = "SELECT balance FROM accounts WHERE account_number = '" + accountNumber + "'";
            rs = stmt.executeQuery(query);
            
            if (rs.next()) {
                balance = rs.getDouble("balance");
            }
            
            System.out.println("Balance retrieved: " + balance); // Poor logging
            
        } catch (SQLException e) {
            e.printStackTrace(); // Poor error handling
        } finally {
            // Resource leak potential - no proper cleanup
            try {
                if (rs != null) rs.close();
                if (stmt != null) stmt.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        
        return balance;
    }
    
    /**
     * Transfer money between accounts
     * Issues: No transaction management, no validation, magic numbers
     */
    public boolean transferMoney(String fromAccount, String toAccount, double amount) {
        
        // Magic number - should be constant
        if (amount > 100000000) {
            System.out.println("Amount exceeds limit");
            return false;
        }
        
        try {
            // No transaction management!
            Statement stmt = connection.createStatement();
            
            // Debit from source account
            String debitQuery = "UPDATE accounts SET balance = balance - " + amount + 
                              " WHERE account_number = '" + fromAccount + "'";
            stmt.executeUpdate(debitQuery);
            
            // Credit to destination account
            String creditQuery = "UPDATE accounts SET balance = balance + " + amount + 
                               " WHERE account_number = '" + toAccount + "'";
            stmt.executeUpdate(creditQuery);
            
            // No audit trail
            System.out.println("Transfer completed");
            
            stmt.close();
            return true;
            
        } catch (SQLException e) {
            e.printStackTrace();
            // No rollback!
            return false;
        }
    }
    
    /**
     * Get customer information
     * Issues: Returns raw data, no DTO, exposes internal structure
     */
    public Vector getCustomerInfo(String customerId) {
        Vector customerData = new Vector(); // Old collection type
        
        try {
            Statement stmt = connection.createStatement();
            String query = "SELECT * FROM customers WHERE customer_id = '" + customerId + "'";
            ResultSet rs = stmt.executeQuery(query);
            
            if (rs.next()) {
                customerData.add(rs.getString("customer_id"));
                customerData.add(rs.getString("name"));
                customerData.add(rs.getString("email"));
                customerData.add(rs.getString("phone"));
                customerData.add(rs.getString("address"));
                // Sensitive data exposed!
                customerData.add(rs.getString("ssn"));
                customerData.add(rs.getString("password")); // Password in plain text!
            }
            
            rs.close();
            stmt.close();
            
        } catch (SQLException e) {
            e.printStackTrace();
        }
        
        return customerData;
    }
    
    /**
     * Calculate interest - Business logic mixed with data access
     */
    public void calculateMonthlyInterest() {
        try {
            Statement stmt = connection.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM accounts WHERE account_type = 'SAVINGS'");
            
            while (rs.next()) {
                String accountNumber = rs.getString("account_number");
                double balance = rs.getDouble("balance");
                
                // Hardcoded business rule
                double interestRate = 0.05; // 5% annual
                double monthlyInterest = (balance * interestRate) / 12;
                
                // Update in same method - no separation of concerns
                String updateQuery = "UPDATE accounts SET balance = balance + " + monthlyInterest +
                                   " WHERE account_number = '" + accountNumber + "'";
                Statement updateStmt = connection.createStatement();
                updateStmt.executeUpdate(updateQuery);
                updateStmt.close();
                
                System.out.println("Interest calculated for: " + accountNumber);
            }
            
            rs.close();
            stmt.close();
            
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
    
    /**
     * Generate account statement
     * Issues: Date handling, formatting, no template engine
     */
    public String generateStatement(String accountNumber, String startDate, String endDate) {
        StringBuffer statement = new StringBuffer(); // Old style, should use StringBuilder
        
        try {
            Statement stmt = connection.createStatement();
            String query = "SELECT * FROM transactions WHERE account_number = '" + accountNumber + 
                         "' AND transaction_date BETWEEN '" + startDate + "' AND '" + endDate + "'";
            ResultSet rs = stmt.executeQuery(query);
            
            statement.append("ACCOUNT STATEMENT\n");
            statement.append("=================\n");
            statement.append("Account: " + accountNumber + "\n");
            statement.append("Period: " + startDate + " to " + endDate + "\n\n");
            
            double totalDebit = 0;
            double totalCredit = 0;
            
            while (rs.next()) {
                String date = rs.getString("transaction_date");
                String type = rs.getString("transaction_type");
                double amount = rs.getDouble("amount");
                
                statement.append(date + " | " + type + " | " + amount + "\n");
                
                if (type.equals("DEBIT")) {
                    totalDebit += amount;
                } else {
                    totalCredit += amount;
                }
            }
            
            statement.append("\nTotal Debit: " + totalDebit);
            statement.append("\nTotal Credit: " + totalCredit);
            
            rs.close();
            stmt.close();
            
        } catch (SQLException e) {
            e.printStackTrace();
        }
        
        return statement.toString();
    }
    
    /**
     * Validate account - Poor validation logic
     */
    public boolean validateAccount(String accountNumber) {
        // No input validation
        if (accountNumber == null || accountNumber.length() == 0) {
            return false;
        }
        
        // Magic number
        if (accountNumber.length() != 10) {
            return false;
        }
        
        // No regex validation
        return true;
    }
    
    /**
     * Close connection - Manual resource management
     */
    public void closeConnection() {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
    
    /**
     * Main method for testing - No proper unit tests
     */
    public static void main(String[] args) {
        BankingService service = new BankingService();
        
        // Test methods
        double balance = service.getAccountBalance("1234567890");
        System.out.println("Balance: " + balance);
        
        boolean result = service.transferMoney("1234567890", "0987654321", 1000.0);
        System.out.println("Transfer result: " + result);
        
        service.closeConnection();
    }
}

// Made with Bob
