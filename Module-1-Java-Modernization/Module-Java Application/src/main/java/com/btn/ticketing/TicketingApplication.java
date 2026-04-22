package com.btn.ticketing;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Main application class for Bank Customer Service Ticketing System
 *
 * This is a legacy application using:
 * - Spring Boot 2.7.18
 * - Java 8
 * - javax namespace (pre-Jakarta EE)
 *
 * @author Bank IT Team
 * @version 1.0.0-LEGACY
 */
@SpringBootApplication
public class TicketingApplication {

    public static void main(String[] args) {
        SpringApplication.run(TicketingApplication.class, args);
        System.out.println("===========================================");
        System.out.println("Bank Ticketing System Started Successfully!");
        System.out.println("Access at: http://localhost:8080");
        System.out.println("===========================================");
    }
}

// Made with Bob
