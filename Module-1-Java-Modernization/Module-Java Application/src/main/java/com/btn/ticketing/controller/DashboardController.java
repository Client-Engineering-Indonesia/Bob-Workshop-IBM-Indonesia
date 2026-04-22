package com.btn.ticketing.controller;

import com.btn.ticketing.service.CustomerService;
import com.btn.ticketing.service.TicketService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * MVC Controller for Dashboard views
 * Uses Thymeleaf for server-side rendering
 */
@Controller
public class DashboardController {

    @Autowired
    private TicketService ticketService;

    @Autowired
    private CustomerService customerService;

    @GetMapping("/dashboard")
    public String dashboard(Model model) {
        try {
            // Get ticket statistics
            Long openTickets = ticketService.countTicketsByStatus("OPEN");
            Long inProgressTickets = ticketService.countTicketsByStatus("IN_PROGRESS");
            Long resolvedTickets = ticketService.countTicketsByStatus("RESOLVED");
            Long closedTickets = ticketService.countTicketsByStatus("CLOSED");

            model.addAttribute("openTickets", openTickets);
            model.addAttribute("inProgressTickets", inProgressTickets);
            model.addAttribute("resolvedTickets", resolvedTickets);
            model.addAttribute("closedTickets", closedTickets);
            model.addAttribute("totalTickets", openTickets + inProgressTickets + resolvedTickets + closedTickets);

            // Get recent tickets
            model.addAttribute("recentTickets", ticketService.getActiveTickets());

            // Get customer count
            model.addAttribute("totalCustomers", customerService.getAllCustomers().size());
            model.addAttribute("activeCustomers", customerService.getActiveCustomers().size());

            return "dashboard";
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
            return "error";
        }
    }

    @GetMapping("/tickets")
    public String tickets(Model model) {
        model.addAttribute("tickets", ticketService.getAllTickets());
        return "tickets";
    }

    @GetMapping("/customers")
    public String customers(Model model) {
        model.addAttribute("customers", customerService.getAllCustomers());
        return "customers";
    }
}

// Made with Bob
