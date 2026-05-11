// BAD PRACTICE: Global variables everywhere - no encapsulation
var userData = {};
var loanData = {};
var isLoggedIn = false;
var currentUser = null;
var loans = [];
var applications = [];

// BAD PRACTICE: No error handling, synchronous operations
function calculateLoan() {
    // BAD PRACTICE: Direct DOM manipulation without validation
    var amount = document.getElementById('loanAmount').value.replace(/\D/g, '');
    var tenor = document.getElementById('loanTenor').value;
    var rate = document.getElementById('interestRate').value;
    
    // BAD PRACTICE: No input validation
    var principal = parseInt(amount);
    var months = parseInt(tenor);
    var interest = parseFloat(rate) / 100 / 12;
    
    // BAD PRACTICE: Complex calculation without comments
    var x = Math.pow(1 + interest, months);
    var monthly = (principal * x * interest) / (x - 1);
    
    // BAD PRACTICE: Potential NaN or Infinity not handled
    var totalPayment = monthly * months;
    var totalInterest = totalPayment - principal;
    
    // BAD PRACTICE: Direct innerHTML manipulation - XSS vulnerability
    document.getElementById('monthlyPayment').innerHTML = 'Rp ' + formatNumber(monthly);
    document.getElementById('totalInterest').innerHTML = 'Rp ' + formatNumber(totalInterest);
    document.getElementById('totalPayment').innerHTML = 'Rp ' + formatNumber(totalPayment);
    
    // BAD PRACTICE: Storing sensitive data in global variable
    loanData = {
        amount: principal,
        tenor: months,
        rate: rate,
        monthly: monthly,
        total: totalPayment,
        interest: totalInterest
    };
}

// BAD PRACTICE: Inconsistent function naming
function formatNumber(num) {
    // BAD PRACTICE: No error handling for invalid input
    return Math.round(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

// BAD PRACTICE: Function does too many things
function formatCurrency(input) {
    var value = input.value.replace(/\D/g, '');
    input.value = formatNumber(value);
}

// BAD PRACTICE: Callback hell potential
function updateLoanAmount(value) {
    document.getElementById('loanAmount').value = formatNumber(value);
    calculateLoan();
}

function updateTenor(value) {
    document.getElementById('loanTenor').value = value;
    calculateLoan();
}

function updateInterestRate() {
    var loanType = document.getElementById('loanType').value;
    document.getElementById('interestRate').value = loanType;
    calculateLoan();
}

// BAD PRACTICE: No validation before scrolling
function scrollToCalculator() {
    document.getElementById('calculator').scrollIntoView({ behavior: 'smooth' });
}

// BAD PRACTICE: Modal management without proper state
function showLogin() {
    // BAD PRACTICE: Multiple modals can be open at once
    document.getElementById('loginModal').style.display = 'block';
    document.getElementById('registerModal').style.display = 'none';
    document.getElementById('applicationModal').style.display = 'none';
}

function showRegister() {
    document.getElementById('registerModal').style.display = 'block';
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('applicationModal').style.display = 'none';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function closeRegisterModal() {
    document.getElementById('registerModal').style.display = 'none';
}

function closeModal() {
    document.getElementById('applicationModal').style.display = 'none';
}

// BAD PRACTICE: No actual authentication, just fake it
function handleLogin(event) {
    event.preventDefault();
    
    // BAD PRACTICE: No validation
    var username = document.getElementById('loginUsername').value;
    var password = document.getElementById('loginPassword').value;
    
    // BAD PRACTICE: Storing password in plain text in memory
    userData.username = username;
    userData.password = password;
    
    // BAD PRACTICE: Always successful login
    isLoggedIn = true;
    currentUser = username;
    
    // BAD PRACTICE: Using alert for user feedback
    alert('Login berhasil! Selamat datang ' + username);
    closeLoginModal();
    
    // BAD PRACTICE: Storing sensitive data in localStorage
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('isLoggedIn', 'true');
}

// BAD PRACTICE: No password strength validation
function handleRegister(event) {
    event.preventDefault();
    
    var name = document.getElementById('registerName').value;
    var email = document.getElementById('registerEmail').value;
    var password = document.getElementById('registerPassword').value;
    var confirmPassword = document.getElementById('registerConfirmPassword').value;
    
    // BAD PRACTICE: Simple string comparison, no proper validation
    if (password != confirmPassword) {
        alert('Password tidak cocok!');
        return;
    }
    
    // BAD PRACTICE: No email validation
    // BAD PRACTICE: Storing password in plain text
    var newUser = {
        name: name,
        email: email,
        password: password,
        registeredAt: new Date()
    };
    
    // BAD PRACTICE: Storing in localStorage without encryption
    localStorage.setItem('user_' + email, JSON.stringify(newUser));
    
    alert('Registrasi berhasil! Silakan login.');
    showLogin();
}

// BAD PRACTICE: Function name doesn't match what it does
function applyLoan(type) {
    // BAD PRACTICE: No authentication check
    document.getElementById('applicationModal').style.display = 'block';
    document.getElementById('applicationLoanType').value = type;
    
    // BAD PRACTICE: Accessing global variable
    if (loanData.amount) {
        document.getElementById('applicationAmount').value = formatNumber(loanData.amount);
    }
}

function applyFromCalculator() {
    // BAD PRACTICE: Duplicate code
    document.getElementById('applicationModal').style.display = 'block';
    
    if (loanData.amount) {
        document.getElementById('applicationAmount').value = formatNumber(loanData.amount);
    }
    
    var loanType = document.getElementById('loanType').selectedOptions[0].text;
    document.getElementById('applicationLoanType').value = loanType.split('(')[0].trim();
}

// BAD PRACTICE: No actual form submission to backend
function submitApplication(event) {
    event.preventDefault();
    
    // BAD PRACTICE: Collecting data without sanitization
    var application = {
        fullName: document.getElementById('fullName').value,
        nik: document.getElementById('nik').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        address: document.getElementById('address').value,
        occupation: document.getElementById('occupation').value,
        income: document.getElementById('income').value,
        loanType: document.getElementById('applicationLoanType').value,
        amount: document.getElementById('applicationAmount').value,
        purpose: document.getElementById('loanPurpose').value,
        submittedAt: new Date(),
        status: 'pending'
    };
    
    // BAD PRACTICE: Pushing to global array
    applications.push(application);
    
    // BAD PRACTICE: Storing in localStorage without limit
    localStorage.setItem('applications', JSON.stringify(applications));
    
    // BAD PRACTICE: Using alert for important feedback
    alert('Pengajuan pinjaman berhasil dikirim! Kami akan menghubungi Anda dalam 1x24 jam.');
    
    closeModal();
    
    // BAD PRACTICE: Not clearing form after submission
}

// BAD PRACTICE: Event listeners added in global scope
window.onclick = function(event) {
    // BAD PRACTICE: Checking multiple modals inefficiently
    if (event.target.className == 'modal') {
        event.target.style.display = 'none';
    }
}

// BAD PRACTICE: Code runs immediately without DOM ready check
calculateLoan();

// BAD PRACTICE: Trying to load data from localStorage on page load
try {
    var storedUser = localStorage.getItem('user');
    if (storedUser) {
        userData = JSON.parse(storedUser);
        isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    }
    
    var storedApplications = localStorage.getItem('applications');
    if (storedApplications) {
        applications = JSON.parse(storedApplications);
    }
} catch (e) {
    // BAD PRACTICE: Silent error handling
    console.log('Error loading data');
}

// BAD PRACTICE: Simulating API calls with setTimeout
function fetchUserLoans() {
    setTimeout(function() {
        // BAD PRACTICE: Fake data generation
        loans = [
            {
                id: 1,
                type: 'KPR',
                amount: 500000000,
                remaining: 450000000,
                status: 'active'
            },
            {
                id: 2,
                type: 'Kendaraan',
                amount: 150000000,
                remaining: 100000000,
                status: 'active'
            }
        ];
        
        // BAD PRACTICE: Storing in global variable
        window.userLoans = loans;
    }, 1000);
}

// BAD PRACTICE: Calling function that doesn't exist yet
if (isLoggedIn) {
    fetchUserLoans();
}

// BAD PRACTICE: Polluting global namespace
var API_URL = 'http://localhost:3000/api';
var TOKEN = null;
var REFRESH_TOKEN = null;

// BAD PRACTICE: Hardcoded credentials
var ADMIN_USER = 'admin';
var ADMIN_PASS = 'admin123';

// BAD PRACTICE: Exposing sensitive function
function debugMode() {
    console.log('User Data:', userData);
    console.log('Loan Data:', loanData);
    console.log('Applications:', applications);
    console.log('Is Logged In:', isLoggedIn);
    console.log('Current User:', currentUser);
}

// BAD PRACTICE: Making debug function globally accessible
window.debug = debugMode;

// BAD PRACTICE: No proper module pattern or IIFE
// BAD PRACTICE: Mixed concerns - UI, business logic, data access all in one file
// BAD PRACTICE: No separation of concerns
// BAD PRACTICE: No use of modern JavaScript features (let, const, arrow functions, async/await)
// BAD PRACTICE: No error boundaries
// BAD PRACTICE: No loading states
// BAD PRACTICE: Direct DOM manipulation everywhere
// BAD PRACTICE: No accessibility considerations
// BAD PRACTICE: No performance optimization
// BAD PRACTICE: Memory leaks potential with event listeners
// BAD PRACTICE: No code documentation
// BAD PRACTICE: Inconsistent code style
// BAD PRACTICE: Magic numbers everywhere
// BAD PRACTICE: No constants for repeated values
// BAD PRACTICE: No input sanitization - XSS vulnerable
// BAD PRACTICE: No CSRF protection
// BAD PRACTICE: Storing sensitive data in localStorage
// BAD PRACTICE: No data encryption
// BAD PRACTICE: No rate limiting
// BAD PRACTICE: No proper state management
// BAD PRACTICE: Callback hell potential
// BAD PRACTICE: No proper error messages
// BAD PRACTICE: Using var instead of let/const
// BAD PRACTICE: No TypeScript or JSDoc
// BAD PRACTICE: No testing considerations
// BAD PRACTICE: Tight coupling between components
// BAD PRACTICE: No dependency injection
// BAD PRACTICE: Hard to maintain and extend

// Made with Bob
