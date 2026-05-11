# 🎯 Custom Demos

This directory contains custom demonstration projects and integration examples.

## 📁 Contents

### 🤖 Instana Autofix with Bob

An advanced integration project that combines IBM Instana monitoring, Bob AI assistant, and GitLab to create an automated error detection and fixing system.

**Key Components:**
- **Integration Plan**: Complete architecture and implementation plan for the Instana-Bob-GitLab integration
- **Demo Applications**: Sample applications with intentional errors for testing

#### Demo Apps

##### Golang Error Simulator
A Go-based backend application designed to simulate various types of errors for testing Instana monitoring capabilities.

**Features:**
- Multiple error types (panic, nil pointer, divide by zero, etc.)
- Business logic errors (payment processing, user management)
- REST API endpoints for triggering errors
- Instana monitoring integration ready

**Location**: `Instana aoutofix with Bob/Demo Apps/golang-error-simulator/`

**Quick Start:**
```bash
cd "Custom Demos/Instana aoutofix with Bob/Demo Apps/golang-error-simulator"
go run main.go
```

Server runs on `http://localhost:8080`

**Documentation**: See the [Integration Plan](Instana%20aoutofix%20with%20Bob/Instana-Bob-GitLab-Integration-Plan.md) for complete details.

## 🎯 Purpose

These demos serve as:
- Proof of concept implementations
- Testing environments for monitoring tools
- Reference implementations for integration patterns
- Training materials for automation workflows

## 🚀 Getting Started

Each demo includes its own README with specific setup instructions. Navigate to the respective directory for detailed documentation.

## 📝 Contributing

When adding new demos:
1. Create a dedicated subdirectory
2. Include a comprehensive README
3. Document prerequisites and setup steps
4. Provide example usage and test cases
5. Update this main README

---

**Last Updated**: 2026-02-05