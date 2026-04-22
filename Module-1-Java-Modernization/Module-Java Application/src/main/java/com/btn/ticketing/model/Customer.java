package com.btn.ticketing.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import java.time.LocalDateTime;

/**
 * Modern Customer entity using Jakarta EE and Java 21 features
 * 
 * IMPROVEMENTS from legacy version:
 * - Uses jakarta.persistence instead of javax.persistence
 * - Uses jakarta.validation instead of javax.validation
 * - Enhanced validation with regex patterns
 * - Builder pattern for easier object creation
 * - Cleaner code structure
 */
@Entity
@Table(name = "customers")
public class Customer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Customer ID is required")
    @Column(name = "customer_id", unique = true, nullable = false, length = 20)
    private String customerId;

    @NotBlank(message = "Name is required")
    @Column(nullable = false, length = 100)
    private String name;

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    @Column(unique = true, nullable = false, length = 100)
    private String email;

    @NotBlank(message = "Phone number is required")
    @Pattern(regexp = "^\\+?[0-9]{10,15}$", message = "Phone number must be valid")
    @Column(name = "phone_number", nullable = false, length = 20)
    private String phoneNumber;

    @Column(length = 200)
    private String address;

    @NotBlank(message = "Account type is required")
    @Column(name = "account_type", nullable = false, length = 50)
    private String accountType; // SAVINGS, CHECKING, LOAN, CREDIT_CARD

    @Column(name = "registration_date", nullable = false)
    private LocalDateTime registrationDate;

    @Column(nullable = false)
    private Boolean active = true;

    // JPA requires no-arg constructor
    public Customer() {
    }

    // Builder pattern
    public static CustomerBuilder builder() {
        return new CustomerBuilder();
    }

    @PrePersist
    protected void onCreate() {
        if (registrationDate == null) {
            registrationDate = LocalDateTime.now();
        }
        if (active == null) {
            active = true;
        }
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getCustomerId() {
        return customerId;
    }

    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getAccountType() {
        return accountType;
    }

    public void setAccountType(String accountType) {
        this.accountType = accountType;
    }

    public LocalDateTime getRegistrationDate() {
        return registrationDate;
    }

    public void setRegistrationDate(LocalDateTime registrationDate) {
        this.registrationDate = registrationDate;
    }

    public Boolean getActive() {
        return active;
    }

    public void setActive(Boolean active) {
        this.active = active;
    }

    // Builder pattern implementation
    public static class CustomerBuilder {
        private final Customer customer = new Customer();

        public CustomerBuilder customerId(String customerId) {
            customer.customerId = customerId;
            return this;
        }

        public CustomerBuilder name(String name) {
            customer.name = name;
            return this;
        }

        public CustomerBuilder email(String email) {
            customer.email = email;
            return this;
        }

        public CustomerBuilder phoneNumber(String phoneNumber) {
            customer.phoneNumber = phoneNumber;
            return this;
        }

        public CustomerBuilder address(String address) {
            customer.address = address;
            return this;
        }

        public CustomerBuilder accountType(String accountType) {
            customer.accountType = accountType;
            return this;
        }

        public CustomerBuilder active(Boolean active) {
            customer.active = active;
            return this;
        }

        public Customer build() {
            return customer;
        }
    }
}

// Modernized with Bob - Jakarta EE + Java 21

// Made with Bob
