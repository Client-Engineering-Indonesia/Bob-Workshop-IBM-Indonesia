// BAD PRACTICE: Missing required dependencies that are in package.json
const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');

// BAD PRACTICE: No error handling for dotenv
dotenv.config();

// BAD PRACTICE: Creating express app without proper configuration
var app = express();

// BAD PRACTICE: Using var instead of const
var PORT = process.env.PORT || 3000;

// BAD PRACTICE: Hardcoded database credentials - security risk
// FIXED: Added better error handling and environment variables support
var db = mysql.createConnection({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'bank_loan_db'
});

// FIXED: Added connection error handling
db.connect(function(err) {
    if (err) {
        console.error('Error connecting to database:', err.message);
        console.log('Please make sure MySQL is running and database is created.');
        console.log('Run: mysql -u root -p < database.sql');
        // Don't exit, let the app run for frontend testing
    } else {
        console.log('Database connected successfully!');
    }
});

// BAD PRACTICE: Hardcoded JWT secret - major security issue
var JWT_SECRET = 'my-super-secret-key-12345';

// BAD PRACTICE: Body parser deprecated usage
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// BAD PRACTICE: Serving static files without security headers
app.use(express.static('public'));

// BAD PRACTICE: No CORS configuration
// BAD PRACTICE: No helmet for security headers
// BAD PRACTICE: No rate limiting
// BAD PRACTICE: No input validation middleware

// BAD PRACTICE: Global error handler missing
// BAD PRACTICE: No logging middleware

// BAD PRACTICE: Inline route handlers - no separation of concerns
app.post('/api/register', function(req, res) {
    // BAD PRACTICE: No input validation
    var name = req.body.name;
    var email = req.body.email;
    var password = req.body.password;
    
    // BAD PRACTICE: Synchronous bcrypt - blocks event loop
    var hashedPassword = bcrypt.hashSync(password, 10);
    
    // BAD PRACTICE: SQL injection vulnerable - no prepared statements
    var query = "INSERT INTO users (name, email, password) VALUES ('" + name + "', '" + email + "', '" + hashedPassword + "')";
    
    // BAD PRACTICE: No error handling
    db.query(query, function(err, result) {
        if (err) {
            // BAD PRACTICE: Exposing internal error to client
            res.status(500).send(err);
        } else {
            res.send({ message: 'User registered successfully' });
        }
    });
});

// BAD PRACTICE: No authentication middleware
app.post('/api/login', function(req, res) {
    var email = req.body.email;
    var password = req.body.password;
    
    // BAD PRACTICE: SQL injection vulnerable
    var query = "SELECT * FROM users WHERE email = '" + email + "'";
    
    db.query(query, function(err, results) {
        if (err) {
            res.status(500).send(err);
        }
        
        // BAD PRACTICE: No check if user exists
        var user = results[0];
        
        // BAD PRACTICE: Synchronous compare - blocks event loop
        var isValid = bcrypt.compareSync(password, user.password);
        
        if (isValid) {
            // BAD PRACTICE: Token never expires
            var token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET);
            
            // BAD PRACTICE: Sending sensitive user data
            res.send({
                token: token,
                user: user // Contains password hash!
            });
        } else {
            // BAD PRACTICE: Generic error message reveals user exists
            res.status(401).send({ message: 'Invalid password' });
        }
    });
});

// BAD PRACTICE: No authentication check
app.post('/api/loan-application', function(req, res) {
    // BAD PRACTICE: Accepting all data without validation
    var data = req.body;
    
    // BAD PRACTICE: SQL injection vulnerable
    var query = "INSERT INTO loan_applications (user_id, full_name, nik, email, phone, address, occupation, income, loan_type, amount, purpose, status) VALUES (" +
        data.userId + ", '" + data.fullName + "', '" + data.nik + "', '" + data.email + "', '" + 
        data.phone + "', '" + data.address + "', '" + data.occupation + "', " + data.income + ", '" + 
        data.loanType + "', " + data.amount + ", '" + data.purpose + "', 'pending')";
    
    db.query(query, function(err, result) {
        if (err) {
            res.status(500).send(err);
        } else {
            res.send({ message: 'Application submitted', id: result.insertId });
        }
    });
});

// BAD PRACTICE: No pagination
app.get('/api/loan-applications', function(req, res) {
    // BAD PRACTICE: Returning all data without filtering
    var query = "SELECT * FROM loan_applications";
    
    db.query(query, function(err, results) {
        if (err) {
            res.status(500).send(err);
        } else {
            // BAD PRACTICE: Exposing all user data
            res.send(results);
        }
    });
});

// BAD PRACTICE: No authorization check - anyone can approve
app.put('/api/loan-applications/:id/approve', function(req, res) {
    var id = req.params.id;
    
    // BAD PRACTICE: SQL injection vulnerable
    var query = "UPDATE loan_applications SET status = 'approved' WHERE id = " + id;
    
    db.query(query, function(err, result) {
        if (err) {
            res.status(500).send(err);
        } else {
            res.send({ message: 'Application approved' });
        }
    });
});

// BAD PRACTICE: No authorization check
app.delete('/api/loan-applications/:id', function(req, res) {
    var id = req.params.id;
    
    // BAD PRACTICE: Hard delete without soft delete option
    var query = "DELETE FROM loan_applications WHERE id = " + id;
    
    db.query(query, function(err, result) {
        if (err) {
            res.status(500).send(err);
        } else {
            res.send({ message: 'Application deleted' });
        }
    });
});

// BAD PRACTICE: Exposing all users without authentication
app.get('/api/users', function(req, res) {
    var query = "SELECT * FROM users";
    
    db.query(query, function(err, results) {
        if (err) {
            res.status(500).send(err);
        } else {
            // BAD PRACTICE: Sending password hashes to client
            res.send(results);
        }
    });
});

// BAD PRACTICE: No input validation for loan calculation
app.post('/api/calculate-loan', function(req, res) {
    var amount = req.body.amount;
    var tenor = req.body.tenor;
    var rate = req.body.rate;
    
    // BAD PRACTICE: No validation, potential division by zero
    var monthlyRate = rate / 100 / 12;
    var x = Math.pow(1 + monthlyRate, tenor);
    var monthly = (amount * x * monthlyRate) / (x - 1);
    
    res.send({
        monthlyPayment: monthly,
        totalPayment: monthly * tenor,
        totalInterest: (monthly * tenor) - amount
    });
});

// BAD PRACTICE: Debug endpoint in production
app.get('/api/debug', function(req, res) {
    res.send({
        database: {
            host: db.config.host,
            user: db.config.user,
            database: db.config.database
        },
        jwtSecret: JWT_SECRET,
        environment: process.env
    });
});

// BAD PRACTICE: No 404 handler
// BAD PRACTICE: No global error handler

// BAD PRACTICE: Server starts without checking database connection
app.listen(PORT, function() {
    console.log('Server running on port ' + PORT);
    // BAD PRACTICE: Logging sensitive information
    console.log('Database connected to ' + db.config.host);
    console.log('JWT Secret: ' + JWT_SECRET);
});

// BAD PRACTICE: No graceful shutdown
// BAD PRACTICE: No process error handlers
// BAD PRACTICE: No clustering for performance
// BAD PRACTICE: No health check endpoint
// BAD PRACTICE: No metrics/monitoring
// BAD PRACTICE: No request logging
// BAD PRACTICE: No API versioning
// BAD PRACTICE: No request timeout
// BAD PRACTICE: No file upload handling
// BAD PRACTICE: No email verification
// BAD PRACTICE: No password reset functionality
// BAD PRACTICE: No session management
// BAD PRACTICE: No refresh token mechanism
// BAD PRACTICE: No API documentation
// BAD PRACTICE: No testing setup
// BAD PRACTICE: Mixing database logic with route handlers
// BAD PRACTICE: No service layer
// BAD PRACTICE: No repository pattern
// BAD PRACTICE: No dependency injection
// BAD PRACTICE: Callback hell potential
// BAD PRACTICE: No async/await usage
// BAD PRACTICE: No proper error classes
// BAD PRACTICE: No validation schemas (Joi, Yup, etc.)
// BAD PRACTICE: No sanitization of inputs
// BAD PRACTICE: No rate limiting per user
// BAD PRACTICE: No IP whitelisting for admin routes
// BAD PRACTICE: No audit logging
// BAD PRACTICE: No data encryption at rest
// BAD PRACTICE: No SSL/TLS enforcement
// BAD PRACTICE: No security headers (CSP, HSTS, etc.)
// BAD PRACTICE: No protection against common attacks (XSS, CSRF, etc.)
// BAD PRACTICE: Database credentials in code
// BAD PRACTICE: No environment-specific configurations
// BAD PRACTICE: No database migration system
// BAD PRACTICE: No database connection pooling
// BAD PRACTICE: No caching layer
// BAD PRACTICE: No queue system for async tasks
// BAD PRACTICE: No microservices architecture consideration
// BAD PRACTICE: Monolithic structure
// BAD PRACTICE: No containerization setup
// BAD PRACTICE: No CI/CD configuration
// BAD PRACTICE: No load balancing consideration

// Made with Bob
