# IBM Bob + Concert: Java Modernization & Security Remediation Labs

This repository demonstrates the complete workflow of using **IBM Bob** for Java modernization and **IBM Concert** for application security, vulnerability detection, and automated remediation.

## 🎯 Overview

This hands-on lab series guides you through:

1. **Java Modernization** - Upgrade legacy Java applications using Bob's AI-powered modernization
2. **Security Scanning** - Scan applications with IBM Concert to detect vulnerabilities
3. **Bob-Concert Integration** - Set up Bob's Security Remediation mode to connect with Concert
4. **Automated Remediation** - Use Bob to automatically fix security vulnerabilities detected by Concert

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Lab Structure](#lab-structure)
- [Getting Started](#getting-started)
- [Lab Guides](#lab-guides)
  - [Lab 1: Java Modernization with Bob](#lab-1-java-modernization-with-bob)
  - [Lab 2: Concert Security Scanning](#lab-2-concert-security-scanning)
  - [Lab 3: Bob-Concert Integration Setup](#lab-3-bob-concert-integration-setup)
  - [Lab 4: Automated Vulnerability Remediation](#lab-4-automated-vulnerability-remediation)
- [Reference Materials](#reference-materials)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Complete Workflow                             │
└─────────────────────────────────────────────────────────────────┘

1. Fork Repository (GitHub)
   └─> VulnerableSampleApp (Java 8 application)

2. Java Modernization (Bob)
   └─> Upgrade Java 8 → Java 17
   └─> Update dependencies
   └─> Refactor deprecated code

3. Push to GitHub
   └─> Trigger Concert scan

4. Security Scanning (Concert)
   └─> Detect CVEs (dependency vulnerabilities)
   └─> Identify SAST exposures (code-level issues)
   └─> Prioritize by severity

5. Automated Remediation (Bob + Concert)
   └─> Bob fetches vulnerabilities from Concert API
   └─> Analyzes code and proposes fixes
   └─> Applies secure patches
   └─> Runs tests and updates Concert status

6. Verification (Concert)
   └─> Re-scan shows reduced vulnerability count
   └─> Track remediation progress
```

---

## ✅ Prerequisites

Before starting the labs, ensure you have:

### General Requirements

- **IBM Bob IDE** (latest version) - VS Code or JetBrains with Bob extension
- **IBM Concert Access** - URL, credentials, and API key
- **GitHub Access** - Ability to fork repositories on `github.com`
- **Basic Knowledge** - Java programming, Git workflows, CLI basics

### Lab-Specific Prerequisites

Each lab has its own detailed prerequisites section:
- **Lab 1** requires SDKMAN! and Maven installation (detailed instructions provided)
- **Lab 2** requires GitHub Personal Access Token (PAT) creation steps
- **Lab 3** requires Concert API credentials configuration
- **Lab 4** requires completion of Labs 1-3

> 💡 **Tip:** Each lab README contains complete installation instructions for its specific requirements. Start with Lab 1 for full setup guidance.

---

## 📁 Lab Structure

```
beacon-bob-concert/
├── README.md                                    ← You are here
├── Lab1-java-modernization/
│   ├── README.md                                ← Java modernization guide
│   └── image/                                   ← Screenshots (01-23)
├── Lab2-concert-part/
│   ├── README.md                                ← Concert scanning guide
│   └── image/                                   ← Screenshots (1-15)
├── Lab3-bob-mode-security-remediation/
│   ├── README.md                                ← Bob-Concert setup guide
│   ├── .env.example                             ← Concert credentials template
│   ├── .bob/
│   │   ├── custom_modes.yaml                    ← Bob mode configuration
│   │   └── rules/
│   │       └── rules-security-remediation/
│   │           ├── README.md                    ← Mode overview
│   │           ├── concert-api-integration.md   ← Concert API reference
│   │           └── remediation-strategies.md    ← Fix patterns for 10+ CVEs
│   └── image/                                   ← Screenshots (1-3)
└── Lab4-vulnerabilities-mitigation-using-bob/
    ├── README.md                                ← Automated remediation guide
    └── image/                                   ← Screenshots (01-18)
```

---

## 🚀 Getting Started

### Step 1: Clone This Repository

```bash
git clone https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp.git
cd VulnerableSampleApp
```

### Step 2: Install Prerequisites

Follow the [Prerequisites](#prerequisites) section to install required software.

### Step 3: Choose Your Starting Point

- **New to Bob?** Start with [Lab 1](#lab-1-java-modernization-with-bob)
- **Already have a modernized app?** Jump to [Lab 2](#lab-2-concert-security-scanning)
- **Want to set up Bob-Concert integration?** Go to [Lab 3](#lab-3-bob-concert-integration-setup)
- **Ready for automated remediation?** Begin with [Lab 4](#lab-4-automated-vulnerability-remediation)

---

## 📚 Lab Guides

### Lab 1: Java Modernization with Bob

**Duration:** 30-45 minutes  
**Difficulty:** Beginner  
**Prerequisites:** Bob IDE, SDKMAN!, Maven

#### What You'll Learn

- How to fork a GitHub repository for isolated development
- Using Bob's Java Modernization mode
- Upgrading Java applications from Java 8 to Java 17
- Updating dependencies and refactoring deprecated code
- Generating comprehensive upgrade documentation

#### Key Outcomes

- ✅ Forked `VulnerableSampleApp` repository
- ✅ Java application upgraded from Java 8 to Java 17
- ✅ All dependencies updated to compatible versions
- ✅ Deprecated code refactored
- ✅ Build successful with all tests passing
- ✅ Changes pushed to your GitHub fork

#### 📖 [Start Lab 1: Java Modernization →](Lab1-java-modernization/README.md)

**Topics Covered:**
- Git forking workflow
- Bob Java Modernization mode activation
- Automated dependency analysis
- Code refactoring and migration
- Documentation generation with Mermaid diagrams

---

### Lab 2: Concert Security Scanning

**Duration:** 20-30 minutes  
**Difficulty:** Beginner  
**Prerequisites:** Completed Lab 1, Concert access, GitHub PAT

#### What You'll Learn

- Creating GitHub Personal Access Tokens (PAT)
- Configuring Concert to scan GitHub repositories
- Understanding CVE (Common Vulnerabilities and Exposures)
- Analyzing SAST (Static Application Security Testing) findings
- Using WatsonX AI for vulnerability explanations

#### Key Outcomes

- ✅ GitHub PAT created and configured
- ✅ Concert connected to your GitHub repository
- ✅ Application scanned for vulnerabilities
- ✅ CVEs and SAST exposures identified
- ✅ Vulnerability priorities understood (Priority 1, 2, 3)
- ✅ WatsonX AI explanations reviewed

#### 📖 [Start Lab 2: Concert Security Scanning →](Lab2-concert-part/README.md)

**Topics Covered:**
- GitHub authentication for Concert
- Repository discovery and scanning
- CVE vs SAST exposure differences
- Vulnerability prioritization
- Cross-application vulnerability mapping
- AI-powered security insights

---

### Lab 3: Bob-Concert Integration Setup

**Duration:** 15-20 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Bob IDE, Concert API credentials

#### What You'll Learn

- Understanding Bob's custom mode architecture
- Configuring Concert API credentials
- Setting up Security Remediation mode
- Testing Bob-Concert connectivity
- Understanding the remediation workflow

#### Key Outcomes

- ✅ `.bob` directory copied to workspace
- ✅ Concert credentials configured in `.env` file
- ✅ Security Remediation mode activated in Bob
- ✅ Concert API connection tested successfully
- ✅ Ready for automated vulnerability remediation

#### 📖 [Start Lab 3: Bob-Concert Integration →](Lab3-bob-mode-security-remediation/README.md)

**Topics Covered:**
- Bob custom modes and rules
- Concert API authentication (C_API_KEY format)
- Environment variable configuration
- Interactive vs manual setup
- API connectivity testing

**Important Files:**
- `custom_modes.yaml` - Bob mode configuration
- `.env.example` - Concert credentials template
- `concert-api-integration.md` - Complete API reference
- `remediation-strategies.md` - Fix patterns for 10+ vulnerability types

---

### Lab 4: Automated Vulnerability Remediation

**Duration:** 45-60 minutes  
**Difficulty:** Advanced  
**Prerequisites:** Completed Labs 1-3, Application with vulnerabilities in Concert

#### What You'll Learn

- Using Bob's Security Remediation mode end-to-end
- Fetching vulnerabilities from Concert API
- Analyzing and fixing SAST exposures
- Applying secure code patterns
- Running automated tests
- Updating Concert status after remediation
- Verifying fixes in Concert dashboard

#### Key Outcomes

- ✅ Bob connected to Concert and fetched vulnerabilities
- ✅ Application with 14 SAST exposures identified
- ✅ Priority 1 vulnerabilities fixed automatically
- ✅ Secure code patterns applied (PreparedStatement, input validation, etc.)
- ✅ All tests passing after fixes
- ✅ Changes committed and pushed to GitHub
- ✅ Concert re-scan shows reduced exposure count (14 → 1)

#### 📖 [Start Lab 4: Automated Remediation →](Lab4-vulnerabilities-mitigation-using-bob/README.md)

**Topics Covered:**
- 6-phase remediation workflow
- CVE vs SAST exposure remediation
- SQL Injection fixes (CWE-89)
- Cross-Site Scripting (XSS) fixes (CWE-79)
- Remote Code Execution (RCE) fixes (CWE-94)
- Path Traversal fixes (CWE-22)
- Command Injection fixes (CWE-78)
- Git workflow for security patches
- Concert status updates

**Vulnerability Types Covered:**
1. SQL Injection (CWE-89)
2. Cross-Site Scripting (XSS) (CWE-79)
3. Path Traversal (CWE-22)
4. Insecure Deserialization (CWE-502)
5. Authentication Bypass (CWE-287)
6. Weak Cryptography (CWE-327)
7. Command Injection (CWE-78)
8. LDAP Injection (CWE-90)
9. XML External Entity (XXE) (CWE-611)
10. Remote Code Execution via ScriptEngine (CWE-94)

---

## 📖 Reference Materials

### Sample Repositories

- **Original Application (Vulnerable):**
  `https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp`
  - Java 8 application
  - 14 SAST exposures
  - Multiple CVEs

- **Upgraded Application (Reference):**
  `https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp`
  - Java 17 application
  - Modernized dependencies
  - Security fixes applied

### Concert Environment

- **Concert Demo Environment:**  
  `https://ibm.github.io/platinum-demos/ibm-concert-demo-environment/assets`
  - Credentials and access information
  - Environment setup guide

### Documentation

- **SDKMAN! Installation:**  
  `https://sdkman.io/install/`

- **Bob Documentation:**  
  Available in your Bob IDE (Help → Documentation)

- **Concert API Reference:**  
  See `Lab3-bob-mode-security-remediation/.bob/rules/rules-security-remediation/concert-api-integration.md`

---

## 🔧 Troubleshooting

### Common Issues

#### Bob Cannot Detect Maven

**Problem:** Bob shows "Maven not found" error

**Solution:**
1. Verify Maven installation: `mvn --version`
2. Restart Bob IDE completely
3. Check that SDKMAN! is initialized in your shell

#### Concert API Connection Failed

**Problem:** Bob cannot connect to Concert API

**Solution:**
1. Verify `.env` file exists in workspace root
2. Check Concert credentials are correct
3. Ensure Concert URL ends with `/concert/core/api/v1`
4. Verify API key is base64-encoded `username:api_key`
5. Test connection manually:
   ```bash
   source .env
   curl -s -k -X GET "${CONCERT_BASE_URL}/applications?page_size=1" \
     -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
     -H "InstanceId: ${CONCERT_INSTANCE_ID}"
   ```

#### Fork Already Exists

**Problem:** Cannot fork repository because fork already exists

**Solution:**
1. Delete existing fork from your GitHub account
2. Or use existing fork and pull latest changes:
   ```bash
   git remote add upstream https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp.git
   git fetch upstream
   git merge upstream/main
   ```

#### Tests Failing After Remediation

**Problem:** Tests fail after Bob applies security fixes

**Solution:**
1. Review Bob's proposed changes carefully
2. Check if test data needs updating
3. Verify database connections use new secure patterns
4. Run tests individually to isolate failures:
   ```bash
   mvn test -Dtest=ClassName#methodName
   ```

#### Concert Not Showing Updated Status

**Problem:** Concert still shows old vulnerability count after fixes

**Solution:**
1. Wait 5-10 minutes for Concert to process updates
2. Manually trigger re-scan in Concert UI
3. Verify changes were pushed to GitHub
4. Check Concert is monitoring the correct branch

---

## 🎓 Learning Path

### Recommended Order

1. **Start Here:** [Lab 1 - Java Modernization](#lab-1-java-modernization-with-bob)
   - Learn Bob basics
   - Understand Java upgrade process
   - Get comfortable with Bob's workflow

2. **Next:** [Lab 2 - Concert Scanning](#lab-2-concert-security-scanning)
   - Understand security scanning
   - Learn about CVEs and SAST
   - See vulnerabilities in action

3. **Then:** [Lab 3 - Integration Setup](#lab-3-bob-concert-integration-setup)
   - Connect Bob to Concert
   - Configure API access
   - Test connectivity

4. **Finally:** [Lab 4 - Automated Remediation](#lab-4-automated-vulnerability-remediation)
   - Put it all together
   - Fix real vulnerabilities
   - See the complete workflow

### Time Commitment

- **Quick Demo (1 hour):** Labs 1 + 2
- **Full Workshop (2-3 hours):** All 4 labs
- **Deep Dive (4+ hours):** All labs + exploring additional vulnerabilities

---

## 🤝 Contributing

Found an issue or have suggestions? Please open an issue or submit a pull request.

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 🆘 Support

For questions or issues:
- Review the [Troubleshooting](#troubleshooting) section
- Check individual lab READMEs for detailed guidance
- Contact your IBM Concert administrator for API access
- Reach out to the Bob support team for IDE issues

---

**Ready to get started?** 🚀

👉 [Begin with Lab 1: Java Modernization →](Lab1-java-modernization/README.md)
