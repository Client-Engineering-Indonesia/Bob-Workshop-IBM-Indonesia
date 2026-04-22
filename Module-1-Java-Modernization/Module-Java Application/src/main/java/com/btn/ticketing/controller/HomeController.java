package com.btn.ticketing.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * Simple REST controller for application info
 */
@RestController
public class HomeController {

    @GetMapping("/")
    public Map<String, Object> welcome() {
        Map<String, Object> response = new HashMap<>();
        response.put("application", "Bank Customer Service Ticketing System");
        response.put("version", "1.0.0-LEGACY");
        response.put("description", "Java Modernization Demo - Legacy Application");
        response.put("techStack", Map.of(
            "java", "8",
            "springBoot", "2.7.18",
            "namespace", "javax (legacy)"
        ));
        response.put("status", "✅ Running");
        response.put("availableEndpoints", Map.of(
            "info", "GET /info - Detailed application info",
            "tickets", "GET /api/tickets - List all tickets (requires auth)",
            "dashboard", "GET /dashboard - Dashboard view",
            "h2Console", "GET /h2-console - H2 Database console"
        ));
        response.put("credentials", Map.of(
            "username", "admin",
            "password", "admin123"
        ));
        response.put("message", "🏦 Welcome to Bank Ticketing System Demo");
        return response;
    }

    @GetMapping("/info")
    public Map<String, Object> info() {
        Map<String, Object> info = new HashMap<>();
        info.put("application", "Bank Customer Service Ticketing System");
        info.put("version", "1.0.0-LEGACY");
        info.put("java", System.getProperty("java.version"));
        info.put("springBoot", "2.7.18");
        info.put("status", "running");
        info.put("endpoints", new String[]{
            "GET / - Welcome page",
            "GET /info - Application info",
            "GET /dashboard - Dashboard view",
            "GET /api/tickets - List all tickets",
            "GET /h2-console - H2 Database console"
        });
        return info;
    }
}

// Made with Bob
