package com.btn.ticketing.repository;

import com.btn.ticketing.model.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for Customer entity
 * Uses Spring Data JPA for database operations
 */
@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    Optional<Customer> findByCustomerId(String customerId);

    Optional<Customer> findByEmail(String email);

    List<Customer> findByActiveTrue();

    List<Customer> findByAccountType(String accountType);

    List<Customer> findByNameContainingIgnoreCase(String name);
}

// Made with Bob
