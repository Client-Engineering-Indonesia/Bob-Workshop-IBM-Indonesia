package com.btn.ticketing.repository;

import com.btn.ticketing.model.Ticket;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for Ticket entity
 * Uses Spring Data JPA for database operations
 */
@Repository
public interface TicketRepository extends JpaRepository<Ticket, Long> {

    Optional<Ticket> findByTicketNumber(String ticketNumber);

    List<Ticket> findByStatus(String status);

    List<Ticket> findByPriority(String priority);

    List<Ticket> findByCategory(String category);

    List<Ticket> findByAssignedTo(String assignedTo);

    List<Ticket> findByCustomerId(Long customerId);

    @Query("SELECT t FROM Ticket t WHERE t.status IN ('OPEN', 'IN_PROGRESS')")
    List<Ticket> findActiveTickets();

    @Query("SELECT COUNT(t) FROM Ticket t WHERE t.status = ?1")
    Long countByStatus(String status);

    @Query("SELECT t FROM Ticket t WHERE t.subject LIKE %?1% OR t.description LIKE %?1%")
    List<Ticket> searchTickets(String keyword);
}

// Made with Bob
