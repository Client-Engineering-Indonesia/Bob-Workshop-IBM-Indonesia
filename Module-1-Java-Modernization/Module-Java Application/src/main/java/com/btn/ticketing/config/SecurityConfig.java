package com.btn.ticketing.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Modern Security configuration for Spring Boot 3.x
 * 
 * IMPROVEMENTS:
 * - Uses SecurityFilterChain instead of deprecated WebSecurityConfigurerAdapter
 * - Uses jakarta.servlet instead of javax.servlet
 * - CSRF protection ENABLED (modern security)
 * - Method-level security enabled with @EnableMethodSecurity
 * - Proper password encoding with BCrypt
 *
 * @author Bank IT Team - Modernized
 * @version 2.0.0-MODERN
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf
                .ignoringRequestMatchers("/h2-console/**") // Only disable for H2 console
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/error").permitAll()
                .requestMatchers("/h2-console/**").permitAll()
                .requestMatchers("/api/**").authenticated()
                .requestMatchers("/dashboard").authenticated()
                .anyRequest().permitAll()
            )
            .httpBasic(basic -> {})
            .headers(headers -> headers
                .frameOptions(frame -> frame.sameOrigin()) // Allow frames from same origin
            );
        
        return http.build();
    }

    @Bean
    public UserDetailsService userDetailsService() {
        // TODO: Replace with database-backed user service in production
        UserDetails admin = User.builder()
            .username("admin")
            .password(passwordEncoder().encode("admin123"))
            .roles("ADMIN", "USER")
            .build();
        
        UserDetails agent = User.builder()
            .username("agent")
            .password(passwordEncoder().encode("agent123"))
            .roles("AGENT", "USER")
            .build();
        
        UserDetails user = User.builder()
            .username("user")
            .password(passwordEncoder().encode("user123"))
            .roles("USER")
            .build();
        
        return new InMemoryUserDetailsManager(admin, agent, user);
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}

// Modernized with Bob - Spring Security 6.x + Java 21

// Made with Bob
