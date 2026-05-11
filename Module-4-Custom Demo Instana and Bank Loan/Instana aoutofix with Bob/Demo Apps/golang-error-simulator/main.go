package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

// User represents a user entity
type User struct {
	ID      int     `json:"id"`
	Name    string  `json:"name"`
	Email   string  `json:"email"`
	Age     int     `json:"age"`
	Balance float64 `json:"balance"`
}

// Payment represents a payment transaction
type Payment struct {
	ID       string  `json:"id"`
	UserID   int     `json:"user_id"`
	Amount   float64 `json:"amount"`
	Currency string  `json:"currency"`
	Status   string  `json:"status"`
}

// Global variables (intentionally problematic for demo)
var users map[int]*User
var payments []Payment
var config map[string]string

func main() {
	// Initialize data
	initializeData()

	// Setup routes
	http.HandleFunc("/", homeHandler)
	http.HandleFunc("/health", healthHandler)

	// Error simulation endpoints
	http.HandleFunc("/api/panic", panicHandler)
	http.HandleFunc("/api/nil-pointer", nilPointerHandler)
	http.HandleFunc("/api/index-out-of-bounds", indexOutOfBoundsHandler)
	http.HandleFunc("/api/divide-by-zero", divideByZeroHandler)
	http.HandleFunc("/api/type-assertion", typeAssertionHandler)
	http.HandleFunc("/api/json-unmarshal", jsonUnmarshalHandler)
	http.HandleFunc("/api/file-not-found", fileNotFoundHandler)
	http.HandleFunc("/api/memory-leak", memoryLeakHandler)
	http.HandleFunc("/api/race-condition", raceConditionHandler)

	// Business logic endpoints (with bugs)
	http.HandleFunc("/api/users", getUsersHandler)
	http.HandleFunc("/api/user", getUserHandler)
	http.HandleFunc("/api/payment", processPaymentHandler)
	http.HandleFunc("/api/calculate", calculateHandler)
	http.HandleFunc("/api/config", getConfigHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("🚀 Server starting on port %s", port)
	log.Printf("📊 Available error endpoints:")
	log.Printf("   - GET  /api/panic              - Trigger panic")
	log.Printf("   - GET  /api/nil-pointer        - Nil pointer dereference")
	log.Printf("   - GET  /api/index-out-of-bounds - Array index out of bounds")
	log.Printf("   - GET  /api/divide-by-zero     - Division by zero")
	log.Printf("   - GET  /api/type-assertion     - Type assertion failure")
	log.Printf("   - GET  /api/json-unmarshal     - JSON unmarshal error")
	log.Printf("   - GET  /api/file-not-found     - File not found error")
	log.Printf("   - GET  /api/memory-leak        - Memory leak simulation")
	log.Printf("   - GET  /api/race-condition     - Race condition")
	log.Printf("   - GET  /api/users              - Get all users (buggy)")
	log.Printf("   - GET  /api/user?id=X          - Get user by ID (buggy)")
	log.Printf("   - POST /api/payment            - Process payment (buggy)")
	log.Printf("   - GET  /api/calculate?a=X&b=Y  - Calculate (buggy)")
	log.Printf("   - GET  /api/config?key=X       - Get config (buggy)")

	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func initializeData() {
	// Initialize users map
	users = make(map[int]*User)
	users[1] = &User{ID: 1, Name: "John Doe", Email: "john@example.com", Age: 30, Balance: 1000.50}
	users[2] = &User{ID: 2, Name: "Jane Smith", Email: "jane@example.com", Age: 25, Balance: 2500.75}
	users[3] = &User{ID: 3, Name: "Bob Johnson", Email: "bob@example.com", Age: 35, Balance: 500.00}

	// Initialize payments
	payments = []Payment{
		{ID: "PAY001", UserID: 1, Amount: 100.00, Currency: "USD", Status: "completed"},
		{ID: "PAY002", UserID: 2, Amount: 250.50, Currency: "USD", Status: "pending"},
	}

	// Initialize config (intentionally leave some nil)
	config = make(map[string]string)
	config["api_key"] = "test-key-123"
	config["environment"] = "development"
}

func homeHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	response := map[string]interface{}{
		"service": "Error Simulator API",
		"version": "1.0.0",
		"status":  "running",
		"message": "Demo application for Instana monitoring with intentional errors",
	}
	json.NewEncoder(w).Encode(response)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
}

// ERROR 1: Panic
func panicHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("⚠️  Triggering panic...")
	panic("This is an intentional panic for testing!")
}

// ERROR 2: Nil Pointer Dereference
func nilPointerHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("⚠️  Triggering nil pointer dereference...")
	var user *User
	name := user.Name
	w.Write([]byte(name))
}

// ERROR 3: Index Out of Bounds
func indexOutOfBoundsHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("⚠️  Triggering index out of bounds...")
	arr := []int{1, 2, 3}
	value := arr[10]
	w.Write([]byte(fmt.Sprintf("Value: %d", value)))
}

// ERROR 4: Divide by Zero
func divideByZeroHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("⚠️  Triggering divide by zero...")
	a := 100
	b := 0
	result := a / b
	w.Write([]byte(fmt.Sprintf("Result: %d", result)))
}

// ERROR 5: Type Assertion Failure
func typeAssertionHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("⚠️  Triggering type assertion failure...")
	var data interface{} = "string value"
	number := data.(int)
	w.Write([]byte(fmt.Sprintf("Number: %d", number)))
}

// ERROR 6: JSON Unmarshal Error
func jsonUnmarshalHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("⚠️  Triggering JSON unmarshal error...")
	invalidJSON := `{"name": "John", "age": "invalid"}`
	var user User
	err := json.Unmarshal([]byte(invalidJSON), &user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	json.NewEncoder(w).Encode(user)
}

// ERROR 7: File Not Found
func fileNotFoundHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("⚠️  Triggering file not found error...")
	_, err := os.ReadFile("/nonexistent/file.txt")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

// ERROR 8: Memory Leak Simulation
func memoryLeakHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("⚠️  Triggering memory leak...")
	leak := make([]byte, 10*1024*1024) // 10MB
	_ = leak
	w.Write([]byte("Memory leak created (10MB)"))
}

// ERROR 9: Race Condition
var counter int

func raceConditionHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("⚠️  Triggering race condition...")
	for i := 0; i < 100; i++ {
		go func() {
			counter++
		}()
	}
	time.Sleep(100 * time.Millisecond)
	w.Write([]byte(fmt.Sprintf("Counter: %d", counter)))
}

// BUSINESS LOGIC ERROR 1: Get Users (Nil Map Access)
func getUsersHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("📋 Getting all users...")

	var tempUsers map[int]*User
	for _, user := range tempUsers {
		log.Printf("User: %v", user)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(users)
}

// BUSINESS LOGIC ERROR 2: Get User by ID (Nil Pointer)
func getUserHandler(w http.ResponseWriter, r *http.Request) {
	idStr := r.URL.Query().Get("id")
	log.Printf("🔍 Getting user with ID: %s", idStr)

	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid user ID", http.StatusBadRequest)
		return
	}

	user := users[id]
	log.Printf("User email: %s", user.Email)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// BUSINESS LOGIC ERROR 3: Process Payment (Nil Pointer)
func processPaymentHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var payment Payment
	if err := json.NewDecoder(r.Body).Decode(&payment); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	log.Printf("💳 Processing payment: %+v", payment)

	user := users[payment.UserID]
	if user.Balance < payment.Amount {
		http.Error(w, "Insufficient balance", http.StatusBadRequest)
		return
	}

	user.Balance = user.Balance - payment.Amount
	payment.Status = "completed"
	payments = append(payments, payment)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(payment)
}

// BUSINESS LOGIC ERROR 4: Calculate (Divide by Zero)
func calculateHandler(w http.ResponseWriter, r *http.Request) {
	aStr := r.URL.Query().Get("a")
	bStr := r.URL.Query().Get("b")

	log.Printf("🧮 Calculating: a=%s, b=%s", aStr, bStr)

	a, _ := strconv.Atoi(aStr)
	b, _ := strconv.Atoi(bStr)

	result := a / b

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]int{"result": result})
}

// BUSINESS LOGIC ERROR 5: Get Config (Nil Pointer)
func getConfigHandler(w http.ResponseWriter, r *http.Request) {
	key := r.URL.Query().Get("key")
	log.Printf("⚙️  Getting config for key: %s", key)

	value := config[key]
	var ptr *string
	if value == "" {
		value = *ptr
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"key": key, "value": value})
}

// Made with Bob
