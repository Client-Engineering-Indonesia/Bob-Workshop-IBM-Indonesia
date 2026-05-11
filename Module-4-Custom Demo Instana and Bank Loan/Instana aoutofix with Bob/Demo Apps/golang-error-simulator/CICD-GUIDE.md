# 🚀 GitLab CI/CD Guide - Golang Error Simulator

Panduan lengkap untuk setup dan menggunakan GitLab CI/CD pipeline untuk Golang Error Simulator.

## 📋 Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Pipeline Stages](#pipeline-stages)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Pipeline CI/CD ini mengotomasi proses:
1. **Testing** - Run unit tests dan security scanning
2. **Building** - Build Go binary dan Docker image
3. **Deployment** - Deploy ke development dan production

### Pipeline Architecture

```
┌─────────┐     ┌─────────┐     ┌──────────┐
│  TEST   │────▶│  BUILD  │────▶│  DEPLOY  │
└─────────┘     └─────────┘     └──────────┘
    │               │                 │
    ├─ Go Tests     ├─ Binary        ├─ Dev
    ├─ Coverage     ├─ Docker        └─ Prod
    └─ Security     └─ Push
```

---

## ✅ Prerequisites

### 1. GitLab Runner
Pastikan GitLab Runner sudah terinstall dan terdaftar:

```bash
# Install GitLab Runner (Ubuntu/Debian)
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt-get install gitlab-runner

# Register runner
sudo gitlab-runner register
```

**Runner Configuration:**
- Executor: `docker`
- Default image: `alpine:latest`
- Tags: `docker`, `golang`

### 2. Docker Registry
Aktifkan Container Registry di GitLab:
1. Go to **Settings** → **General** → **Visibility**
2. Enable **Container Registry**

### 3. Server untuk Deployment
- Development server dengan Docker installed
- Production server dengan Docker installed
- SSH access ke kedua server

---

## 🔄 Pipeline Stages

### Stage 1: Test

#### test:
- Runs Go unit tests
- Generates coverage report
- Runs on all branches and MRs

```yaml
test:
  stage: test
  image: golang:1.21-alpine
  script:
    - go test -v -race -coverprofile=coverage.out ./...
```

#### security:scan:
- Runs security vulnerability scanning
- Uses `gosec` tool
- Allows failure (won't block pipeline)

```yaml
security:scan:
  stage: test
  script:
    - gosec -fmt json -out gosec-report.json ./...
  allow_failure: true
```

### Stage 2: Build

#### build:binary:
- Builds static Go binary
- Optimized with `-ldflags="-w -s"`
- Runs on all branches

```yaml
build:binary:
  stage: build
  script:
    - CGO_ENABLED=0 go build -ldflags="-w -s" -o golang-error-simulator main.go
```

#### build:docker:
- Builds Docker image
- Pushes to GitLab Container Registry
- Tags: `$CI_COMMIT_SHORT_SHA` and `latest`
- Runs only on `main`/`master` and tags

```yaml
build:docker:
  stage: build
  script:
    - docker build -t $DOCKER_IMAGE:$DOCKER_TAG .
    - docker push $DOCKER_IMAGE:$DOCKER_TAG
```

### Stage 3: Deploy

#### deploy:dev:
- Deploys to development environment
- Manual trigger
- Runs on `develop` and `main` branches

#### deploy:prod:
- Deploys to production environment
- Manual trigger
- Runs only on tags (releases)

---

## ⚙️ Setup Instructions

### Step 1: Configure GitLab CI/CD Variables

Go to **Settings** → **CI/CD** → **Variables** dan tambahkan:

#### Required Variables:

| Variable | Type | Value | Protected | Masked |
|----------|------|-------|-----------|--------|
| `CI_REGISTRY` | Variable | `162.133.131.244` | ✅ | ❌ |
| `CI_REGISTRY_USER` | Variable | `your-username` | ✅ | ❌ |
| `CI_REGISTRY_PASSWORD` | Variable | `your-password` | ✅ | ✅ |
| `SSH_PRIVATE_KEY` | File | `<private-key-content>` | ✅ | ✅ |

#### Deployment Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `DEV_SERVER` | `dev.example.com` | Development server hostname |
| `DEV_USER` | `deploy` | SSH user for dev server |
| `PROD_SERVER` | `prod.example.com` | Production server hostname |
| `PROD_USER` | `deploy` | SSH user for prod server |

### Step 2: Setup SSH Keys

#### Generate SSH Key Pair:
```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "gitlab-ci@example.com" -f gitlab-ci-key

# Copy public key to servers
ssh-copy-id -i gitlab-ci-key.pub deploy@dev.example.com
ssh-copy-id -i gitlab-ci-key.pub deploy@prod.example.com
```

#### Add Private Key to GitLab:
```bash
# Copy private key content
cat gitlab-ci-key

# Paste to GitLab CI/CD Variables as SSH_PRIVATE_KEY
```

### Step 3: Prepare Deployment Servers

#### On Development Server:
```bash
# Create application directory
sudo mkdir -p /opt/apps/golang-error-simulator
sudo chown deploy:deploy /opt/apps/golang-error-simulator

# Create docker-compose.yml
cd /opt/apps/golang-error-simulator
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  golang-error-simulator:
    image: 162.133.131.244/root/golang-error-simulator:latest
    container_name: golang-error-simulator
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
EOF

# Login to GitLab Container Registry
docker login 162.133.131.244
```

#### On Production Server:
```bash
# Same steps as development server
# But use production-specific configuration
```

### Step 4: Test Pipeline

#### Push to trigger pipeline:
```bash
git add .
git commit -m "Add CI/CD configuration"
git push origin main
```

#### Monitor pipeline:
1. Go to **CI/CD** → **Pipelines**
2. Click on running pipeline
3. View job logs

---

## 🔐 Environment Variables

### Application Variables

```bash
# .env file (for local development)
PORT=8080
APP_NAME=golang-error-simulator
```

### CI/CD Variables

Set in GitLab **Settings** → **CI/CD** → **Variables**:

```bash
# Docker Registry
CI_REGISTRY=162.133.131.244
CI_REGISTRY_USER=your-username
CI_REGISTRY_PASSWORD=your-password

# Deployment
DEV_SERVER=dev.example.com
DEV_USER=deploy
PROD_SERVER=prod.example.com
PROD_USER=deploy

# SSH
SSH_PRIVATE_KEY=<content-of-private-key>
```

---

## 🚀 Deployment

### Manual Deployment to Development

1. Go to **CI/CD** → **Pipelines**
2. Find successful pipeline on `main` branch
3. Click **deploy:dev** job
4. Click **Play** button
5. Monitor deployment logs

### Manual Deployment to Production

1. Create a new tag:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

2. Go to **CI/CD** → **Pipelines**
3. Find pipeline for the tag
4. Click **deploy:prod** job
5. Click **Play** button
6. Monitor deployment logs

### Automatic Deployment (Optional)

Remove `when: manual` from `.gitlab-ci.yml` untuk auto-deploy:

```yaml
deploy:dev:
  # Remove this line:
  # when: manual
  only:
    - main
```

---

## 🐛 Troubleshooting

### Problem 1: Docker Build Fails

**Error**: `Cannot connect to Docker daemon`

**Solution**:
```bash
# Check GitLab Runner configuration
sudo gitlab-runner verify

# Restart Docker service
sudo systemctl restart docker

# Restart GitLab Runner
sudo gitlab-runner restart
```

### Problem 2: SSH Connection Failed

**Error**: `Permission denied (publickey)`

**Solution**:
```bash
# Verify SSH key is added to server
ssh -i gitlab-ci-key deploy@dev.example.com

# Check SSH_PRIVATE_KEY variable in GitLab
# Make sure it includes BEGIN and END lines
```

### Problem 3: Docker Registry Login Failed

**Error**: `unauthorized: authentication required`

**Solution**:
```bash
# Verify CI_REGISTRY_PASSWORD is correct
# Login manually to test
docker login 162.133.131.244 -u your-username

# Update GitLab CI/CD variable if needed
```

### Problem 4: Go Tests Fail

**Error**: `go: cannot find main module`

**Solution**:
```bash
# Ensure go.mod exists
go mod init github.com/demo/error-simulator

# Update dependencies
go mod tidy
```

### Problem 5: Deployment Fails

**Error**: `docker-compose: command not found`

**Solution**:
```bash
# Install docker-compose on deployment server
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

## 📊 Pipeline Monitoring

### View Pipeline Status

```bash
# Using GitLab CLI
glab ci status

# View specific pipeline
glab ci view <pipeline-id>

# View job logs
glab ci trace <job-id>
```

### Pipeline Badges

Add to README.md:

```markdown
[![pipeline status](http://162.133.131.244/root/golang-error-simulator/badges/main/pipeline.svg)](http://162.133.131.244/root/golang-error-simulator/-/commits/main)

[![coverage report](http://162.133.131.244/root/golang-error-simulator/badges/main/coverage.svg)](http://162.133.131.244/root/golang-error-simulator/-/commits/main)
```

---

## 🎯 Best Practices

### 1. Use Semantic Versioning
```bash
# Major release
git tag -a v2.0.0 -m "Major release with breaking changes"

# Minor release
git tag -a v1.1.0 -m "New features added"

# Patch release
git tag -a v1.0.1 -m "Bug fixes"
```

### 2. Always Test Locally First
```bash
# Build Docker image locally
docker build -t golang-error-simulator:test .

# Run container
docker run -p 8080:8080 golang-error-simulator:test

# Test endpoints
curl http://localhost:8080/health
```

### 3. Use Branch Protection
- Require MR approval before merge
- Require pipeline success
- Prevent force push to main

### 4. Monitor Resource Usage
```bash
# Check runner disk space
df -h

# Check Docker images
docker images

# Clean up old images
docker image prune -a
```

---

## 📚 Additional Resources

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Docker Documentation](https://docs.docker.com/)
- [Go Testing Documentation](https://golang.org/pkg/testing/)
- [GitLab Runner Documentation](https://docs.gitlab.com/runner/)

---

## 🔄 Pipeline Workflow Example

### Complete Development Workflow:

```bash
# 1. Create feature branch
git checkout -b feature/new-endpoint

# 2. Make changes
# ... edit code ...

# 3. Test locally
go test ./...
docker build -t test .

# 4. Commit and push
git add .
git commit -m "Add new endpoint"
git push origin feature/new-endpoint

# 5. Create Merge Request
# Pipeline runs automatically (test stage)

# 6. After approval, merge to main
# Pipeline runs (test + build stages)

# 7. Deploy to development
# Click "Play" on deploy:dev job

# 8. Test on development
curl http://dev.example.com:8080/health

# 9. Create release tag
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# 10. Deploy to production
# Click "Play" on deploy:prod job
```

---

**Last Updated**: 2026-02-05  
**Version**: 1.0.0  
**Author**: Wahyu Herlambang