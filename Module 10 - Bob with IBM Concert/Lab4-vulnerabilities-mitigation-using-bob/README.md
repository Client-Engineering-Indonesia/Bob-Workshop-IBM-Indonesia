# BOB + Concert Security Remediation Demo Guide

**IBM BOB (SDLC AI Assistant) × IBM Concert (Application Security)**
A step-by-step walkthrough of how BOB, integrated with IBM Concert, automatically identifies and remediates SAST (Static Application Security Testing) exposures in an e-commerce Java application.

---

For this lab we will use this repo 
`https://github.ibm.com/ibm-concert-platinum-demos/ecommerce-backend`

## Overview

This demo shows the complete security remediation loop:

```
Deploy Rules → Activate Mode → Discover Apps via Concert
   → Scan for Vulnerabilities → Fix SAST Issues (Code Mode)
      → Push to GitHub → Verify in Concert (Reduced Exposure Count)
```

**Starting state:** `ecommerce-backend` has **14 SAST exposures** detected in IBM Concert.  
**End state:** After BOB's automated remediation, Concert shows only **1 remaining SAST exposure**.

---

## Repositories & Key Paths

| Asset | Path | Description |
|-------|------|-------------|
| Security Remediation Rules | `beacon-bob-concert/bob-security-remediation-mode/rules/rules-security-remediation/` | BOB mode rules and Concert API integration guides |
| BOB Mode Config | `beacon-bob-concert/bob-security-remediation-mode/custom_modes.yaml` | Custom mode definitions for BOB |
| Original Application (14 SAST) | `ecommerce-backend/` | Vulnerable e-commerce Java app (pre-fix) |
| Fixed Application | `upgraded-java-app/` | Remediated version with SAST exposures resolved |

> **Note:** If your code lives at a different path, replace `ecommerce-backend/` and `upgraded-java-app/` with your actual directories throughout this guide. These are referenced as placeholders.

---

## Prerequisites

Before starting the demo, ensure you have:

- [ ] IBM BOB installed and accessible in your IDE (VS Code / JetBrains)
- [ ] IBM Concert instance running and accessible (note your Concert URL and API key)
- [ ] The `ecommerce-backend` application already registered and scanned in IBM Concert (showing 14 SAST exposures)
- [ ] Git access (HTTPS token or SSH key) to the target repository
- [ ] `jq` installed on your machine (`brew install jq` / `apt install jq`)

---

## Step 1 — Deploy Security Remediation Rules to BOB

The Security Remediation mode is defined by a set of rule files and a custom mode YAML. These must be available to BOB before the mode can be activated.

### 1.1 Locate the Rules Directory

The rules live at:

```
beacon-bob-concert/bob-security-remediation-mode/
├── custom_modes.yaml                         ← Mode definition (slug, role, workflow)
└── rules/
    └── rules-security-remediation/
        ├── README.md                         ← Mode overview & quick start
        ├── concert-api-integration.md        ← Concert REST API reference
        └── remediation-strategies.md         ← Fix patterns for 10 vulnerability types
```

### 1.2 Register the Custom Mode in BOB

Copy or reference the `custom_modes.yaml` into your BOB global configuration. The file defines the following mode:

- `security-remediation` — for Concert-integrated vulnerability fixing

![BOB Settings - Custom Modes Loaded](image/01-bob-settings-custom-modes.png)
> *📸 BOB settings panel showing custom_modes.yaml loaded, with "Security Remediation" mode visible in the modes list*

### 1.3 Place Rules in the Workspace

Ensure the rules directory is accessible to BOB in your working workspace. BOB will reference these files during the remediation workflow:

```bash
# Example: copy rules to your project's .bob directory
cp -r beacon-bob-concert/bob-security-remediation-mode/rules .bob/rules
```

> **Note:** The `.env` file containing your Concert credentials should be placed in the root of the workspace you are remediating. BOB will create it interactively on first use if it is not present.

---

## Step 2 — Activate Security Remediation Mode in BOB

### 2.1 Review the Security Remediation Mode

Before activating, you can view the mode details — role definition, when to use, and the 6-phase workflow.

![BOB Security Remediation Mode Detail](image/02-bob-security-remediation-mode-detail.png)
> *📸 BOB showing the Security Remediation mode details — role definition, when to use, and the 6-phase workflow description*

### 2.2 Switch to Security Remediation Mode

In the BOB interface, click the mode selector and choose **"🔒 Security Remediation"**.

![BOB Security Remediation Mode Selected](image/03-bob-security-remediation-mode-selected.png)
> *📸 BOB mode dropdown showing "🔒 Security Remediation" selected*

### 2.3 Configure Concert Credentials (First Time Only)

On first activation in a new workspace, BOB will interactively guide you through setting up your `.env` file:

```
BOB: This mode is currently compatible for Concert v2.3.1.

BOB: What is your Concert instance URL?
     (e.g., https://<your-concert-host>:12443)

You: https://<your-concert-host>:12443

BOB: What is your Concert username?
You: concertuser

BOB: What is your Concert API key?
You: <your-api-key>

BOB: What is your Concert Instance ID? (default: 0000-0000-0000-0000)
You: [press Enter for default]

BOB: ✅ .env file created successfully!
```

The resulting `.env` will look like:

```env
CONCERT_BASE_URL=https://<your-concert-host>:12443/concert/core/api/v1
CONCERT_API_KEY=<base64-encoded-username:apikey>
CONCERT_INSTANCE_ID=0000-0000-0000-0000
```

---

## Step 3 — Ask BOB to Discover All Projects in Concert

Type the following single command in the BOB chat:

```
Check Concert for vulnerabilities
```

BOB automatically runs two things back-to-back — no extra input needed:

1. **Tests the API connection** by calling the Concert `/kpis` endpoint
2. **Fetches all registered applications** and presents them in a table

![BOB Concert Connection + API Test Running](image/05-bob-concert-connection-success.png)
> *📸 BOB running the Concert API connection test and returning "✅ Concert API connection successful!"*

![BOB Concert Applications Table](image/06-bob-concert-applications-table.png)
> *📸 BOB immediately fetching and displaying all applications registered in Concert after the connection is verified*

---

## Step 4 — Select Application & Scan for Vulnerabilities

### 4.1 BOB Presents the Scope Selection

```
BOB: What would you like to fix?

  1. CVEs (Dependency vulnerabilities — Log4j, Spring, etc.)
  2. SAST Exposures (Code-level issues — SQL injection, XSS, RCE, etc.)
```

![BOB Scope Selection CVE vs SAST](image/07-bob-scope-selection-cve-vs-sast.png)
> *📸 BOB showing the CVE vs SAST Exposures choice prompt*

---

## Step 5 — Choose SAST Exposures

> *This Bob Model can not only be used for SAST but also for CVEs but for this demo we give you one naratives*
### 5.1 Select SAST

```
You: SAST Exposures (Code-level security issues like SQL Injection, XSS, RCE)
```

BOB automatically fetches all SAST exposures from Concert.

### 5.2 BOB Displays All 14 Exposures

BOB parses and sorts the results by priority:

```
BOB: 🔍 Fetching SAST exposures...
BOB: Found 14 exposures (3 Priority 1, 6 Priority 2, 5 Priority 3):

| # | Priority   | Severity | Vulnerability Type                          |
|---|------------|----------|---------------------------------------------|
| 1 | Priority 1 | error    | java-rce-scriptengine-eval-tainted          |
| 2 | Priority 1 | error    | sqli.java.method-param-sql-concat           |
| 3 | Priority 1 | error    | xss.java.servlet-writer                     |
| 4 | Priority 2 | warning  | path-traversal.java.file-constructor-tainted|
| 5 | Priority 2 | warning  | insecure-deserialization.java               |
| ...                                                               |
|14 | Priority 3 | note     | weak-crypto.java.md5-digest                 |

Which exposure would you like to fix? (Enter number or "all")
```

![BOB SAST Exposures List 14](image/08-bob-sast-exposures-list-14.png)
> *📸 BOB chat displaying the full list of 14 SAST exposures from Concert, sorted by priority with severity indicators*

---

## Step 6 — Ask BOB to Fix & Push the Code

### 6.1 Ask BOB to Fix the SAST Exposures

You can ask BOB to fix all exposures or one at a time. For this demo, request a fix plan:

```
You: Fix all SAST exposures
```

BOB switches to its code analysis and remediation workflow. It will generate a task plan:

```
BOB: Perfect! I can see all the vulnerabilities. Now I'll create a comprehensive fix to
     all exposures identified by Concert. Let me create a TODO list to track the fixes:

  ☐ Fix RCE via ScriptEngine (lines 200-205)
  ☐ Fix Insecure Deserialization (lines 92-97)
  ☐ Fix Path Traversal - File constructor (line 71)
  ☐ Fix Path Traversal - Files.read (line 72)
  ☐ Fix Path Traversal - Files.write (line 172)
  ☐ Fix SQL Injection - method param concat (lines 41-42)
  ☐ Fix SQL Injection - query variable concat (lines 41-42, 146, 300)
  ☐ Fix SQL Injection - single quote concat (lines 41-42)
  ☐ Fix SQL Injection - string concatenation (lines 41-42, 146, 300)
  ☐ ...
```

![BOB Remediation Task Plan](image/09-bob-remediation-task-plan.png)
> *📸 BOB generating the remediation task list with file paths and line numbers for each SAST exposure*

### 6.2 BOB Applies Each Fix

Confirm and BOB applies changes surgically, one file at a time:

```
You: Yes, apply all fixes

BOB: ✅ Fix 1/14 applied — ProductController.java:67 (RCE removed)
BOB: ✅ Fix 2/14 applied — ProductController.java:45 (SQL Injection → PreparedStatement)
BOB: ✅ Fix 3/14 applied — CommentController.java:120 (XSS → encoded output)
...
BOB: ✅ All 14 fixes applied. Running tests...
BOB: 🧪 Tests passed (47/47)
```

![BOB Fixes Applied Progress](image/10-bob-fixes-applied-progress.png)
> *📸 BOB applying fixes sequentially, showing the "✅ Fix X/14 applied" progress messages*

![BOB Tests Passing](image/11-bob-tests-passing.png)
> *📸 BOB showing the test run output with all tests passing after remediation*

### 6.3 Push Fixed Code to GitHub

After all fixes are applied, ask BOB to push:

```
You: Push the fixed code to GitHub
```

BOB commits all changes and pushes the security branch to GitHub in one go.

![BOB Git Push to GitHub](image/12-bob-git-push.png)
> *📸 BOB confirming all fix commits are pushed and the branch is available on GitHub*

---

## Step 7 — Verify in IBM Concert

Now we return to IBM Concert to confirm the SAST exposure count has dropped from 14 to 1.

### 7.1 Open IBM Concert Dashboard

Navigate to your Concert instance and open the main dashboard.

![Concert Dashboard](image/13-concert-dashboard.png)
> *📸 IBM Concert main dashboard/landing page*

### 7.2 Click "Discover Your Data"

In Concert, trigger a new data discovery / scan by clicking **"Discover your data"**.

![Concert Discover Your Data](image/14-concert-discover-data-button.png)
> *📸 IBM Concert "Discover your data" button/option highlighted in the UI*

### 7.3 Configure the GitHub Repository for Scanning

In the discovery configuration, point Concert to the updated GitHub repository:

- **Repository URL:** `https://github.com/<org>/ecommerce-backend`
- **Branch:** `main` (or the merged branch)
- **Scan type:** SAST

![Concert Repo Config](image/15-concert-repo-config.png)
> *📸 Concert repository configuration screen with the GitHub repo URL and branch entered*

### 7.4 Wait for the Scan to Complete

Concert will pull the latest code and run a fresh SAST scan. This typically takes 1–3 minutes.

![Concert Scan In Progress](image/16-concert-scan-in-progress.png)
> *📸 Concert showing the scan "In Progress" status with a loading indicator*

### 7.5 Review the New Results

Once the scan completes, navigate to the `ecommerce-app-bob-upgraded` application in Concert.

**Before (14 SAST Exposures):**

![Concert Before 14 SAST](image/17-concert-before-14-sast.png)
> *📸 IBM Concert showing the ecommerce application with 14 SAST exposures — captured before the demo*

**After (1 SAST Exposure remaining):**

![Concert After 1 SAST](image/18-concert-after-1-sast.png)
> *📸 IBM Concert showing the ecommerce application with only 1 SAST exposure remaining after BOB's automated remediation*

The exposure count dropped from **14 → 1**, confirming that BOB's automated security remediation successfully resolved 13 of 14 SAST findings.

---

## Results Summary

| Metric | Before | After |
|--------|--------|-------|
| SAST Exposures | 14 | 1 |
| Critical (Priority 1) | 3 | 0 |
| High (Priority 2) | 6 | 0 |
| Medium/Low (Priority 3–4) | 5 | 1 |
| Time to remediate | Manual (days) | Automated via BOB (minutes) |

---

## Appendix

### A. Folder Structure Reference

```
Bob-Artemis/
├── DEMO-GUIDE.md
├── image/                                          ← All screenshot images go here
│   ├── 01-bob-settings-custom-modes.png
│   ├── 02-bob-security-remediation-mode-detail.png
│   ├── 03-bob-security-remediation-mode-selected.png
│   ├── 04-bob-env-setup-conversation.png
│   ├── 05-bob-concert-connection-success.png
│   ├── 06-bob-concert-applications-table.png
│   ├── 07-bob-scope-selection-cve-vs-sast.png
│   ├── 08-bob-sast-exposures-list-14.png
│   ├── 09-bob-remediation-task-plan.png
│   ├── 10-bob-fixes-applied-progress.png
│   ├── 11-bob-tests-passing.png
│   ├── 12-bob-git-push.png
│   ├── 13-concert-dashboard.png
│   ├── 14-concert-discover-data-button.png
│   ├── 15-concert-repo-config.png
│   ├── 16-concert-scan-in-progress.png
│   ├── 17-concert-before-14-sast.png
│   └── 18-concert-after-1-sast.png
│
├── beacon-bob-concert/
│   └── bob-security-remediation-mode/
│       ├── custom_modes.yaml
│       └── rules/
│           └── rules-security-remediation/
│               ├── README.md
│               ├── concert-api-integration.md
│               └── remediation-strategies.md
│
├── ecommerce-backend/                               ← Original code (14 SAST issues)
│   ├── VulnerableApp.java
│   └── pom.xml
│
└── upgraded-java-app/                               ← Remediated code (1 SAST remaining)
    ├── src/
    ├── pom.xml
    └── Dockerfile
```

### B. BOB Workflow Phases Reference

| Phase | Name | What Happens |
|-------|------|-------------|
| 0 | Setup Environment | BOB creates `.env` with Concert credentials (first use only) |
| 1 | Test API Connection | BOB pings Concert `/kpis` endpoint to verify connectivity |
| 2 | Discover Applications | BOB lists all apps registered in Concert |
| 3 | Clone Repository | BOB clones the selected app's repo via HTTPS or SSH |
| 4 | Choose Vulnerability Scope | User chooses CVEs or SAST Exposures |
| 5 | Fetch & Display Issues | BOB pulls and sorts all exposures/CVEs from Concert |
| 6 | Remediate | BOB analyzes code, proposes fixes, applies with approval, runs tests |
| 7 | Push to GitHub | BOB commits and pushes the security branch |

### C. Concert API Endpoints Used

| Purpose | Endpoint |
|---------|----------|
| Health check | `GET /kpis` |
| List applications | `GET /applications?page_size=100` |
| Fetch SAST exposures | `GET /applications/{id}/exposures?page_size=100` |
| Fetch CVEs | `GET /vulnerability/cves?show_associations=true&filter=application_id:{id}` |
| Update exposure status | `PATCH /vulnerability/exposures/{id}` |

### D. Adapting This Guide to Different Repositories

If the application code is at a different path than shown above, update these placeholders:

| Placeholder | Replace With |
|-------------|-------------|
| `ecommerce-backend/` | Path to your original (vulnerable) application |
| `upgraded-java-app/` | Path to your remediated application |
| `ecommerce-app-bob-upgraded` | Your Concert application name |
| `https://github.com/<org>/ecommerce-backend` | Your actual GitHub repository URL |
| `https://<your-concert-host>:12443` | Your Concert instance URL |
