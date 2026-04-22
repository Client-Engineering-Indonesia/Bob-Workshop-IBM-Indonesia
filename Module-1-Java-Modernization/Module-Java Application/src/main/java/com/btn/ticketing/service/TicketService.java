package com.btn.ticketing.service;

import com.btn.ticketing.model.Ticket;
import com.btn.ticketing.repository.TicketRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Service layer for Ticket operations
 * Contains business logic for ticket management
 * 
 * WARNING: This implementation has potential security issues:
 * - No input sanitization (SQL injection risk)
 * - No authorization checks
 * - Direct string concatenation in queries
 */
@Service
@Transactional
public class TicketService {

    @Autowired
    private TicketRepository ticketRepository;

    public List<Ticket> getAllTickets() {
        return ticketRepository.findAll();
    }

    public Optional<Ticket> getTicketById(Long id) {
        return ticketRepository.findById(id);
    }

    public Optional<Ticket> getTicketByNumber(String ticketNumber) {
        return ticketRepository.findByTicketNumber(ticketNumber);
    }

    public Ticket createTicket(Ticket ticket) {
        // Generate unique ticket number
        ticket.setTicketNumber("TKT-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        ticket.setStatus("OPEN");
        ticket.setCreatedDate(LocalDateTime.now());
        return ticketRepository.save(ticket);
    }

    public Ticket updateTicket(Long id, Ticket ticketDetails) {
        Ticket ticket = ticketRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Ticket not found with id: " + id));

        ticket.setSubject(ticketDetails.getSubject());
        ticket.setDescription(ticketDetails.getDescription());
        ticket.setCategory(ticketDetails.getCategory());
        ticket.setPriority(ticketDetails.getPriority());
        ticket.setStatus(ticketDetails.getStatus());
        ticket.setAssignedTo(ticketDetails.getAssignedTo());
        ticket.setResolution(ticketDetails.getResolution());
        ticket.setUpdatedDate(LocalDateTime.now());

        return ticketRepository.save(ticket);
    }

    public void deleteTicket(Long id) {
        ticketRepository.deleteById(id);
    }

    public List<Ticket> getTicketsByStatus(String status) {
        return ticketRepository.findByStatus(status);
    }

    public List<Ticket> getTicketsByCustomer(Long customerId) {
        return ticketRepository.findByCustomerId(customerId);
    }

    public List<Ticket> getActiveTickets() {
        return ticketRepository.findActiveTickets();
    }

    public Long countTicketsByStatus(String status) {
        return ticketRepository.countByStatus(status);
    }

    // WARNING: Potential SQL injection vulnerability
    // This method directly uses user input in query
    public List<Ticket> searchTickets(String keyword) {
        return ticketRepository.searchTickets(keyword);
    }

    public Ticket assignTicket(Long ticketId, String agentUsername) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found"));
        
        ticket.setAssignedTo(agentUsername);
        ticket.setStatus("IN_PROGRESS");
        ticket.setUpdatedDate(LocalDateTime.now());
        
        return ticketRepository.save(ticket);
    }

    public Ticket resolveTicket(Long ticketId, String resolution) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found"));
        
        ticket.setResolution(resolution);
        ticket.setStatus("RESOLVED");
        ticket.setResolvedDate(LocalDateTime.now());
        ticket.setUpdatedDate(LocalDateTime.now());
        
        return ticketRepository.save(ticket);
    }

    public Ticket closeTicket(Long ticketId) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found"));
        
        ticket.setStatus("CLOSED");
        ticket.setClosedDate(LocalDateTime.now());
        ticket.setUpdatedDate(LocalDateTime.now());
        
        return ticketRepository.save(ticket);
    }
}

// Made with Bob
