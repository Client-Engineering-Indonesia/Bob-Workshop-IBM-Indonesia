-- Sample data for Bank Customer Service Ticketing System
-- This file is automatically executed on application startup

-- Insert sample customers
INSERT INTO customers (id, customer_id, name, email, phone_number, address, account_type, registration_date, active) VALUES
(1, 'BSN001', 'Budi Santoso', 'budi.santoso@email.com', '+628123456789', 'Jl. Sudirman No. 123, Jakarta', 'SAVINGS', CURRENT_TIMESTAMP, true),
(2, 'BSN002', 'Siti Nurhaliza', 'siti.nurhaliza@email.com', '+628234567890', 'Jl. Thamrin No. 45, Jakarta', 'CHECKING', CURRENT_TIMESTAMP, true),
(3, 'BSN003', 'Ahmad Wijaya', 'ahmad.wijaya@email.com', '+628345678901', 'Jl. Gatot Subroto No. 67, Jakarta', 'LOAN', CURRENT_TIMESTAMP, true),
(4, 'BSN004', 'Dewi Lestari', 'dewi.lestari@email.com', '+628456789012', 'Jl. Rasuna Said No. 89, Jakarta', 'CREDIT_CARD', CURRENT_TIMESTAMP, true),
(5, 'BSN005', 'Rudi Hartono', 'rudi.hartono@email.com', '+628567890123', 'Jl. HR Rasuna Said No. 12, Jakarta', 'SAVINGS', CURRENT_TIMESTAMP, true);

-- Insert sample users
INSERT INTO users (id, username, password, full_name, role, active, created_date) VALUES
(1, 'admin', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Administrator', 'ADMIN', true, CURRENT_TIMESTAMP),
(2, 'agent1', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Agent Satu', 'AGENT', true, CURRENT_TIMESTAMP),
(3, 'agent2', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Agent Dua', 'AGENT', true, CURRENT_TIMESTAMP),
(4, 'supervisor', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Supervisor', 'SUPERVISOR', true, CURRENT_TIMESTAMP);

-- Insert sample tickets
INSERT INTO tickets (id, ticket_number, customer_id, subject, description, category, priority, status, assigned_to, created_date, updated_date) VALUES
(1, 'TKT-A1B2C3D4', 1, 'Cannot access online banking', 'Customer reports unable to login to online banking portal. Error message: Invalid credentials', 'ACCOUNT_ISSUE', 'HIGH', 'OPEN', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'TKT-E5F6G7H8', 2, 'Unauthorized transaction on account', 'Customer noticed unauthorized debit transaction of Rp 5,000,000 on 15 March 2026', 'TRANSACTION_DISPUTE', 'CRITICAL', 'IN_PROGRESS', 'agent1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'TKT-I9J0K1L2', 3, 'Loan payment inquiry', 'Customer wants to know remaining loan balance and payment schedule', 'LOAN_INQUIRY', 'MEDIUM', 'RESOLVED', 'agent2', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(4, 'TKT-M3N4O5P6', 4, 'Credit card not working', 'Credit card declined at merchant. Card is not expired and has available credit', 'CARD_ISSUE', 'HIGH', 'IN_PROGRESS', 'agent1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(5, 'TKT-Q7R8S9T0', 5, 'Request for account statement', 'Customer requests account statement for last 6 months for tax purposes', 'GENERAL', 'LOW', 'OPEN', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(6, 'TKT-U1V2W3X4', 1, 'Update contact information', 'Customer wants to update phone number and email address', 'ACCOUNT_ISSUE', 'LOW', 'CLOSED', 'agent2', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(7, 'TKT-Y5Z6A7B8', 3, 'Early loan repayment inquiry', 'Customer wants to know penalty for early loan repayment', 'LOAN_INQUIRY', 'MEDIUM', 'RESOLVED', 'agent1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Note: Password for all users is 'password123' (BCrypt encoded)
-- In production, use strong passwords and proper password policies

-- Made with Bob
