package com.btn.ticketing.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDateTime;

/**
 * Modern Ticket entity using Jakarta EE and Java 21 features
 * 
 * IMPROVEMENTS from legacy version:
 * - Uses jakarta.persistence instead of javax.persistence
 * - Uses jakarta.validation instead of javax.validation
 * - Cleaner code with modern Java patterns
 * - Proper encapsulation with immutable fields where possible
 * 
 * Note: Still using class instead of record because JPA entities
 * require mutable state and no-arg constructor
 */
@Entity
@Table(name = "tickets")
public class Ticket {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Ticket number is required")
    @Column(unique = true, nullable = false, length = 20)
    private String ticketNumber;

    @NotNull(message = "Customer is required")
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;

    @NotBlank(message = "Subject is required")
    @Column(nullable = false, length = 200)
    private String subject;

    @NotBlank(message = "Description is required")
    @Column(nullable = false, columnDefinition = "TEXT")
    private String description;

    @NotBlank(message = "Category is required")
    @Column(nullable = false, length = 50)
    private String category; // ACCOUNT_ISSUE, TRANSACTION_DISPUTE, CARD_ISSUE, LOAN_INQUIRY, GENERAL

    @NotBlank(message = "Priority is required")
    @Column(nullable = false, length = 20)
    private String priority; // LOW, MEDIUM, HIGH, CRITICAL

    @NotBlank(message = "Status is required")
    @Column(nullable = false, length = 20)
    private String status; // OPEN, IN_PROGRESS, PENDING, RESOLVED, CLOSED

    @Column(length = 100)
    private String assignedTo;

    @Column(columnDefinition = "TEXT")
    private String resolution;

    @Column(nullable = false)
    private LocalDateTime createdDate;

    @Column
    private LocalDateTime updatedDate;

    @Column
    private LocalDateTime resolvedDate;

    @Column
    private LocalDateTime closedDate;

    // JPA requires no-arg constructor
    public Ticket() {
    }

    // Builder pattern for easier object creation
    public static TicketBuilder builder() {
        return new TicketBuilder();
    }

    @PrePersist
    protected void onCreate() {
        createdDate = LocalDateTime.now();
        updatedDate = LocalDateTime.now();
        if (status == null) {
            status = "OPEN";
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedDate = LocalDateTime.now();
        if ("RESOLVED".equals(status) && resolvedDate == null) {
            resolvedDate = LocalDateTime.now();
        }
        if ("CLOSED".equals(status) && closedDate == null) {
            closedDate = LocalDateTime.now();
        }
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTicketNumber() {
        return ticketNumber;
    }

    public void setTicketNumber(String ticketNumber) {
        this.ticketNumber = ticketNumber;
    }

    public Customer getCustomer() {
        return customer;
    }

    public void setCustomer(Customer customer) {
        this.customer = customer;
    }

    public String getSubject() {
        return subject;
    }

    public void setSubject(String subject) {
        this.subject = subject;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getPriority() {
        return priority;
    }

    public void setPriority(String priority) {
        this.priority = priority;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getAssignedTo() {
        return assignedTo;
    }

    public void setAssignedTo(String assignedTo) {
        this.assignedTo = assignedTo;
    }

    public String getResolution() {
        return resolution;
    }

    public void setResolution(String resolution) {
        this.resolution = resolution;
    }

    public LocalDateTime getCreatedDate() {
        return createdDate;
    }

    public void setCreatedDate(LocalDateTime createdDate) {
        this.createdDate = createdDate;
    }

    public LocalDateTime getUpdatedDate() {
        return updatedDate;
    }

    public void setUpdatedDate(LocalDateTime updatedDate) {
        this.updatedDate = updatedDate;
    }

    public LocalDateTime getResolvedDate() {
        return resolvedDate;
    }

    public void setResolvedDate(LocalDateTime resolvedDate) {
        this.resolvedDate = resolvedDate;
    }

    public LocalDateTime getClosedDate() {
        return closedDate;
    }

    public void setClosedDate(LocalDateTime closedDate) {
        this.closedDate = closedDate;
    }

    // Builder pattern implementation
    public static class TicketBuilder {
        private final Ticket ticket = new Ticket();

        public TicketBuilder ticketNumber(String ticketNumber) {
            ticket.ticketNumber = ticketNumber;
            return this;
        }

        public TicketBuilder customer(Customer customer) {
            ticket.customer = customer;
            return this;
        }

        public TicketBuilder subject(String subject) {
            ticket.subject = subject;
            return this;
        }

        public TicketBuilder description(String description) {
            ticket.description = description;
            return this;
        }

        public TicketBuilder category(String category) {
            ticket.category = category;
            return this;
        }

        public TicketBuilder priority(String priority) {
            ticket.priority = priority;
            return this;
        }

        public TicketBuilder status(String status) {
            ticket.status = status;
            return this;
        }

        public TicketBuilder assignedTo(String assignedTo) {
            ticket.assignedTo = assignedTo;
            return this;
        }

        public Ticket build() {
            return ticket;
        }
    }
}

// Modernized with Bob - Jakarta EE + Java 21

// Made with Bob
