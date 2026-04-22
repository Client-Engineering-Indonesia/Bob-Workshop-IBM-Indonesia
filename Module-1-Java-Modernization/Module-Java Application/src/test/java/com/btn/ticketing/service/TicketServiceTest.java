package com.btn.ticketing.service;

import com.btn.ticketing.model.Customer;
import com.btn.ticketing.model.Ticket;
import com.btn.ticketing.repository.TicketRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.*;

/**
 * Unit tests for TicketService
 * 
 * Uses JUnit 5 and Mockito for modern testing
 * Demonstrates best practices:
 * - Given-When-Then pattern
 * - Descriptive test names
 * - AssertJ for fluent assertions
 * - Proper mocking
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("Ticket Service Tests")
class TicketServiceTest {

    @Mock
    private TicketRepository ticketRepository;

    @InjectMocks
    private TicketService ticketService;

    private Ticket testTicket;
    private Customer testCustomer;

    @BeforeEach
    void setUp() {
        // Given: Setup test data
        testCustomer = new Customer();
        testCustomer.setId(1L);
        testCustomer.setCustomerId("BSN001");
        testCustomer.setName("Budi Santoso");
        testCustomer.setEmail("budi@email.com");

        testTicket = new Ticket();
        testTicket.setId(1L);
        testTicket.setTicketNumber("TKT-12345678");
        testTicket.setCustomer(testCustomer);
        testTicket.setSubject("Test Subject");
        testTicket.setDescription("Test Description");
        testTicket.setCategory("ACCOUNT_ISSUE");
        testTicket.setPriority("HIGH");
        testTicket.setStatus("OPEN");
        testTicket.setCreatedDate(LocalDateTime.now());
    }

    @Test
    @DisplayName("Should create ticket successfully")
    void shouldCreateTicketSuccessfully() {
        // Given
        when(ticketRepository.save(any(Ticket.class))).thenReturn(testTicket);

        // When
        Ticket createdTicket = ticketService.createTicket(testTicket);

        // Then
        assertThat(createdTicket).isNotNull();
        assertThat(createdTicket.getTicketNumber()).startsWith("TKT-");
        assertThat(createdTicket.getStatus()).isEqualTo("OPEN");
        assertThat(createdTicket.getCreatedDate()).isNotNull();
        
        verify(ticketRepository, times(1)).save(any(Ticket.class));
    }

    @Test
    @DisplayName("Should get all tickets")
    void shouldGetAllTickets() {
        // Given
        Ticket ticket2 = new Ticket();
        ticket2.setId(2L);
        ticket2.setTicketNumber("TKT-87654321");
        
        List<Ticket> tickets = Arrays.asList(testTicket, ticket2);
        when(ticketRepository.findAll()).thenReturn(tickets);

        // When
        List<Ticket> result = ticketService.getAllTickets();

        // Then
        assertThat(result).hasSize(2);
        assertThat(result).contains(testTicket, ticket2);
        verify(ticketRepository, times(1)).findAll();
    }

    @Test
    @DisplayName("Should get ticket by ID when exists")
    void shouldGetTicketByIdWhenExists() {
        // Given
        when(ticketRepository.findById(1L)).thenReturn(Optional.of(testTicket));

        // When
        Optional<Ticket> result = ticketService.getTicketById(1L);

        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getId()).isEqualTo(1L);
        assertThat(result.get().getTicketNumber()).isEqualTo("TKT-12345678");
        verify(ticketRepository, times(1)).findById(1L);
    }

    @Test
    @DisplayName("Should return empty when ticket not found")
    void shouldReturnEmptyWhenTicketNotFound() {
        // Given
        when(ticketRepository.findById(999L)).thenReturn(Optional.empty());

        // When
        Optional<Ticket> result = ticketService.getTicketById(999L);

        // Then
        assertThat(result).isEmpty();
        verify(ticketRepository, times(1)).findById(999L);
    }

    @Test
    @DisplayName("Should update ticket successfully")
    void shouldUpdateTicketSuccessfully() {
        // Given
        Ticket updatedDetails = new Ticket();
        updatedDetails.setSubject("Updated Subject");
        updatedDetails.setDescription("Updated Description");
        updatedDetails.setCategory("TRANSACTION_DISPUTE");
        updatedDetails.setPriority("CRITICAL");
        updatedDetails.setStatus("IN_PROGRESS");
        updatedDetails.setAssignedTo("agent1");

        when(ticketRepository.findById(1L)).thenReturn(Optional.of(testTicket));
        when(ticketRepository.save(any(Ticket.class))).thenReturn(testTicket);

        // When
        Ticket result = ticketService.updateTicket(1L, updatedDetails);

        // Then
        assertThat(result.getSubject()).isEqualTo("Updated Subject");
        assertThat(result.getStatus()).isEqualTo("IN_PROGRESS");
        assertThat(result.getAssignedTo()).isEqualTo("agent1");
        verify(ticketRepository, times(1)).findById(1L);
        verify(ticketRepository, times(1)).save(any(Ticket.class));
    }

    @Test
    @DisplayName("Should throw exception when updating non-existent ticket")
    void shouldThrowExceptionWhenUpdatingNonExistentTicket() {
        // Given
        when(ticketRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> ticketService.updateTicket(999L, testTicket))
            .isInstanceOf(RuntimeException.class)
            .hasMessageContaining("Ticket not found");
        
        verify(ticketRepository, times(1)).findById(999L);
        verify(ticketRepository, never()).save(any(Ticket.class));
    }

    @Test
    @DisplayName("Should delete ticket successfully")
    void shouldDeleteTicketSuccessfully() {
        // Given
        doNothing().when(ticketRepository).deleteById(1L);

        // When
        ticketService.deleteTicket(1L);

        // Then
        verify(ticketRepository, times(1)).deleteById(1L);
    }

    @Test
    @DisplayName("Should get tickets by status")
    void shouldGetTicketsByStatus() {
        // Given
        List<Ticket> openTickets = Arrays.asList(testTicket);
        when(ticketRepository.findByStatus("OPEN")).thenReturn(openTickets);

        // When
        List<Ticket> result = ticketService.getTicketsByStatus("OPEN");

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getStatus()).isEqualTo("OPEN");
        verify(ticketRepository, times(1)).findByStatus("OPEN");
    }

    @Test
    @DisplayName("Should get tickets by customer")
    void shouldGetTicketsByCustomer() {
        // Given
        List<Ticket> customerTickets = Arrays.asList(testTicket);
        when(ticketRepository.findByCustomerId(1L)).thenReturn(customerTickets);

        // When
        List<Ticket> result = ticketService.getTicketsByCustomer(1L);

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getCustomer().getId()).isEqualTo(1L);
        verify(ticketRepository, times(1)).findByCustomerId(1L);
    }

    @Test
    @DisplayName("Should assign ticket to agent")
    void shouldAssignTicketToAgent() {
        // Given
        when(ticketRepository.findById(1L)).thenReturn(Optional.of(testTicket));
        when(ticketRepository.save(any(Ticket.class))).thenReturn(testTicket);

        // When
        Ticket result = ticketService.assignTicket(1L, "agent1");

        // Then
        assertThat(result.getAssignedTo()).isEqualTo("agent1");
        assertThat(result.getStatus()).isEqualTo("IN_PROGRESS");
        verify(ticketRepository, times(1)).findById(1L);
        verify(ticketRepository, times(1)).save(any(Ticket.class));
    }

    @Test
    @DisplayName("Should resolve ticket")
    void shouldResolveTicket() {
        // Given
        testTicket.setStatus("IN_PROGRESS");
        when(ticketRepository.findById(1L)).thenReturn(Optional.of(testTicket));
        when(ticketRepository.save(any(Ticket.class))).thenReturn(testTicket);

        // When
        Ticket result = ticketService.resolveTicket(1L, "Issue resolved successfully");

        // Then
        assertThat(result.getStatus()).isEqualTo("RESOLVED");
        assertThat(result.getResolution()).isEqualTo("Issue resolved successfully");
        assertThat(result.getResolvedDate()).isNotNull();
        verify(ticketRepository, times(1)).findById(1L);
        verify(ticketRepository, times(1)).save(any(Ticket.class));
    }

    @Test
    @DisplayName("Should close ticket")
    void shouldCloseTicket() {
        // Given
        testTicket.setStatus("RESOLVED");
        when(ticketRepository.findById(1L)).thenReturn(Optional.of(testTicket));
        when(ticketRepository.save(any(Ticket.class))).thenReturn(testTicket);

        // When
        Ticket result = ticketService.closeTicket(1L);

        // Then
        assertThat(result.getStatus()).isEqualTo("CLOSED");
        assertThat(result.getClosedDate()).isNotNull();
        verify(ticketRepository, times(1)).findById(1L);
        verify(ticketRepository, times(1)).save(any(Ticket.class));
    }

    @Test
    @DisplayName("Should count tickets by status")
    void shouldCountTicketsByStatus() {
        // Given
        when(ticketRepository.countByStatus("OPEN")).thenReturn(5L);

        // When
        Long count = ticketService.countTicketsByStatus("OPEN");

        // Then
        assertThat(count).isEqualTo(5L);
        verify(ticketRepository, times(1)).countByStatus("OPEN");
    }
}

// Modern Unit Testing with Bob - JUnit 5 + Mockito + AssertJ

// Made with Bob
