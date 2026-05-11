# Golang Error Simulator

Demo aplikasi backend dalam Golang dengan berbagai tipe error untuk testing Instana monitoring.

## 📦 Prerequisites

### Install Golang di Ubuntu 22.04

#### Opsi 1: Install dari Official Repository (Recommended)

```bash
# Update package list
sudo apt update

# Install Golang
sudo apt install golang-go -y

# Verify installation
go version
```

#### Opsi 2: Install Versi Terbaru dari Official Website

```bash
# Download Golang (ganti dengan versi terbaru)
wget https://go.dev/dl/go1.21.6.linux-amd64.tar.gz

# Remove old installation (jika ada)
sudo rm -rf /usr/local/go

# Extract ke /usr/local
sudo tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz

# Setup environment variables
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc

# Reload bashrc
source ~/.bashrc

# Verify installation
go version
```

#### Opsi 3: Install via Snap

```bash
# Install via snap
sudo snap install go --classic

# Verify installation
go version
```

### Verify Installation

```bash
# Check Go version
go version

# Check Go environment
go env

# Test Go installation
mkdir -p ~/test-go
cd ~/test-go
echo 'package main

import "fmt"

func main() {
    fmt.Println("Hello, Go!")
}' > hello.go

go run hello.go
# Output: Hello, Go!

# Cleanup
cd ~
rm -rf ~/test-go
```

## 🚀 Cara Menjalankan Aplikasi

### Opsi 1: Run Langsung dengan Go

```bash
# Run langsung
go run main.go

# Atau build dulu
go build -o error-simulator
./error-simulator
```

### Opsi 2: Run dengan Docker

```bash
# Build Docker image
docker build -t golang-error-simulator .

# Run container
docker run -p 8080:8080 golang-error-simulator
```

### Opsi 3: Run dengan Docker Compose

```bash
# Start application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

Server akan berjalan di `http://localhost:8080`

## 📡 API Endpoints

### Error Simulation
- `GET /api/panic` - Trigger panic
- `GET /api/nil-pointer` - Nil pointer dereference
- `GET /api/index-out-of-bounds` - Array index error
- `GET /api/divide-by-zero` - Division by zero
- `GET /api/type-assertion` - Type assertion failure
- `GET /api/json-unmarshal` - JSON parsing error
- `GET /api/file-not-found` - File not found
- `GET /api/memory-leak` - Memory leak (10MB)
- `GET /api/race-condition` - Race condition

### Business Logic (dengan bugs)
- `GET /api/users` - Get all users
- `GET /api/user?id=1` - Get user by ID
- `POST /api/payment` - Process payment
- `GET /api/calculate?a=100&b=5` - Calculate
- `GET /api/config?key=api_key` - Get config

## 🧪 Testing

```bash
# Health check
curl http://localhost:8080/health

# Test error
curl http://localhost:8080/api/nil-pointer
```

## 🎯 Purpose

This application is designed for:
- Testing Instana monitoring capabilities
- Demonstrating error detection and alerting
- Integration with Bob AI for automated error fixing
- Training and demo purposes

## 🔄 CI/CD Pipeline

Aplikasi ini dilengkapi dengan GitLab CI/CD pipeline yang lengkap:

- ✅ Automated testing
- ✅ Code coverage reporting
- ✅ Security scanning
- ✅ Docker image building
- ✅ Automated deployment

### Quick Start CI/CD

1. Push code ke GitLab
2. Pipeline akan berjalan otomatis
3. Review test results dan coverage
4. Deploy ke development (manual trigger)
5. Create tag untuk production release
6. Deploy ke production (manual trigger)

📚 **Dokumentasi Lengkap**: Lihat [CICD-GUIDE.md](./CICD-GUIDE.md) untuk setup dan konfigurasi detail.

## 📁 Project Structure

```
golang-error-simulator/
├── main.go                 # Main application
├── go.mod                  # Go module definition
├── README.md               # This file
├── CICD-GUIDE.md          # CI/CD documentation
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── .gitlab-ci.yml         # GitLab CI/CD pipeline
├── .dockerignore          # Docker build exclusions
└── .env.example           # Environment variables template
```

## ⚠️ Important

**PENTING**: Aplikasi ini sengaja dibuat dengan bugs untuk testing. Jangan gunakan di production!

## 📚 Documentation

- [CI/CD Guide](./CICD-GUIDE.md) - Complete CI/CD setup and usage
- [Setup Submodule](../SETUP-SUBMODULE.md) - How to add as git submodule

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Merge Request

---

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Repository**: http://162.133.131.244/root/golang-error-simulator