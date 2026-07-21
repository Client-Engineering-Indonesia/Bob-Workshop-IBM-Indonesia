# 📚 Bob Workshop — IBM Indonesia

A hands-on workshop series demonstrating how **IBM Bob** (AI-powered developer assistant) accelerates real-world engineering tasks — from code modernization and ML pipelines to SRE incident analysis and agentic service desk automation.

---

## 🗂️ Module Overview (8 Modules)

| # | Module | Topic | Key Tech |
|---|--------|-------|----------|
| 0 | [Bob Introduction](#module-0--bob-introduction) | Getting started with Bob | IBM Bob |
| 1 | [Java Modernization](#module-1--java-modernization) | Modernize legacy Java/Spring Boot | Java, Lombok, Spring Security |
| 2 | [COBOL Modernization](#module-2--cobol--rpg-modernization) | Understand & modernize COBOL | COBOL, Python, PostgreSQL |
| 3 | [Data Science & ML](#module-3--data-science--ml) | ML pipeline with watsonx | Python, watsonx.ai, Streamlit |
| 4 | [Instana + Bank Loan App](#module-4--custom-demo-instana--bank-loan-app) | Frontend QA & Instana autofix | Go, Node.js, IBM Instana, GitLab |
| 5 | [Deployment Platform](#module-5--deployment-platform) | Deploy apps to OpenShift via UI | Flask, Kubernetes, OpenShift |
| 6 | [Instana SRE](#module-6--instana-sre) | AI-driven incident root cause analysis | Python, IBM Instana, Bob SRE Mode |
| 7 | [Service Desk Assistant](#module-7--service-desk-assistant) | Multi-agent service desk automation | Watsonx Orchestrate, ServiceNow, Elasticsearch |

---

## Module 0 — Bob Introduction

📄 [`Module 0 - Bob Introduction/IBM-bob-trial-tutorial.pdf`](Module%200%20-%20Bob%20Introduction/IBM-bob-trial-tutorial.pdf)

A PDF tutorial to get started with IBM Bob — covers installation, basic usage, and navigating key features before the hands-on modules begin.

---

## Module 1 — Java Modernization

📄 [`Module-1-Java-Modernization/Module-Java Application/DEMO-GUIDE.md`](Module-1-Java-Modernization/Module-Java%20Application/DEMO-GUIDE.md)

Modernize a legacy Spring Boot banking ticketing application with Bob's assistance.

**5 Simple Steps:**
1. Ask Bob about Java/Spring Boot versions and dependencies
2. Let Bob analyze technical debt across the codebase
3. Modernize models with Lombok (remove boilerplate)
4. Add input validation and security hardening
5. Generate an architecture diagram

**Sub-modules:**
- `Module-Java Application/` — Full Spring Boot app (controllers, services, repositories, frontend) ⭐ Main demo
- `Module-Java Simple/` — Side-by-side legacy vs. modern Java comparison (backup)

---

## Module 2 — COBOL & RPG Modernization

📄 [`Module-2-RPG-COBOL-Modernization/Module - COBOL Application/DEMO-GUIDE.md`](Module-2-RPG-COBOL-Modernization/Module%20-%20COBOL%20Application/DEMO-GUIDE.md)

Use Bob to explain, analyze, and build a modernization strategy for a legacy COBOL banking system.

**5 Simple Steps:**
1. Ask Bob to explain the COBOL program structure
2. Analyze code flow and data structures
3. Identify modernization opportunities
4. Generate a flowchart / documentation
5. Get a step-by-step modernization strategy

**Sub-modules:**
- `Module - COBOL Application/` — Full COBOL app with copybooks, PostgreSQL database, Python/Flask frontend ⭐ Main demo
- `Module -COBOL Simple/` — Legacy vs. modern COBOL side-by-side (backup)

---

## Module 3 — Data Science & ML

📄 [`Module-3-DataScientist and ML/Instructions Guide/IMPLEMENTATION_GUIDE.md`](Module-3-DataScientist%20and%20ML/Instructions%20Guide/IMPLEMENTATION_GUIDE.md)

Build a Trade Settlement Prediction ML pipeline assisted by Bob, with interactive HTML dashboards at each stage.

**5 Simple Steps:**
1. **Data Analysis** → Generate analysis dashboard
2. **Code Development** → Generate code documentation dashboard
3. **Model Building** → Generate model performance dashboard
4. **Deployment** → Generate deployment dashboard (watsonx.ai or Streamlit)
5. **Final Dashboard** → Comprehensive 12-tab overview

**Features:**
- Trade settlement prediction ML model (CSV data included)
- Interactive HTML dashboards generated at each step
- Two deployment paths: Cloud (watsonx.ai) or Local (Streamlit)
- Data lineage queries via MCP server or local pre-generated files

---

## Module 4 — Custom Demo: Instana & Bank Loan App

📄 [`Module-4-Custom Demo Instana and Bank Loan/GUIDE.md`](Module-4-Custom%20Demo%20Instana%20and%20Bank%20Loan/GUIDE.md)

Two demos bundled together:

### 4a. Bank Loan App — Production-Ready Frontend with Bob
A 2.5-hour workshop where Bob performs systematic code review on a Node.js bank loan application frontend. Bob identifies security vulnerabilities, applies production-ready best practices, assists with QA testing, and generates a professional code review report.

**Components:** `bank-loan-app/` (Node.js backend + HTML/JS/CSS frontend), `bank-loan-app-FE/` (standalone frontend)

### 4b. Instana Autofix with Bob
An advanced integration combining IBM Instana monitoring, Bob, and GitLab for automated error detection and auto-remediation.

**Components:** `Instana aoutofix with Bob/Demo Apps/golang-error-simulator/` — a Go application that simulates various runtime errors (panics, nil pointer, divide-by-zero, business logic failures) to trigger Instana alerts, which Bob then analyzes and fixes via GitLab CI/CD.

---

## Module 5 — Deployment Platform

📄 [`Module-5-Deployment-Platform/DEMO-GUIDE.md`](Module-5-Deployment-Platform/DEMO-GUIDE.md)

A visual web-based deployment platform that allows developers to upload Python code and deploy it directly to an OpenShift cluster — without writing Kubernetes manifests by hand.

**Flow:**
1. Developer uploads Python code via Web UI (Flask + SocketIO)
2. Platform analyzes dependencies automatically
3. Generates Dockerfile, Kubernetes manifests, and Jenkins pipeline
4. Deploys to Production or Development namespace on OpenShift
5. Real-time deployment status via WebSocket

**Components:** `web-ui/` (Flask app + JS frontend), `k8s/` (RBAC + namespace manifests), `sample-app/` (demo Flask apps)

---

## Module 6 — Instana SRE

📄 [`Module-6-Instana-SRE/README.md`](Module-6-Instana-SRE/README.md)

> **Difficulty**: Beginner–Intermediate | **Duration**: ~30–45 min | **Mode**: Bob SRE Agent (`🔧 SRE`)

Use Bob as an AI Site Reliability Engineer to connect to the IBM Instana REST API, fetch live incidents, and generate a deep root cause analysis report.

**6 Steps:**
1. Clone & set up the Python environment
2. Configure Instana API credentials (`.env`)
3. Install dependencies (`pip install`)
4. Fetch incidents from Instana (`fetch_instana_incidents.py`)
5. Analyze incidents using Bob's SRE mode
6. Review the generated root cause analysis report

**What you learn:**
- Querying the Instana REST API for incident events
- Using Bob SRE mode for AI-driven root cause analysis
- Interpreting cascading failure patterns (Etcd, Kafka, ACE Integration Servers)
- SRE best practices: severity triage, blast radius, prioritized remediation

> 💡 No Instana account? Sample data files (`incidents.json`, `latest_5_open_incidents.json`) are included so you can still complete the analysis steps.

**Also includes:** `instana-mcp/` — instructions for connecting Bob directly to Instana via MCP server

---

## Module 7 — Service Desk Assistant

📄 [`Module-7-Service-Desk-Assistant/DEMO-GUIDE.md`](Module-7-Service-Desk-Assistant/DEMO-GUIDE.md)

An AI-powered multi-agent service desk that automates email processing, incident creation, risk assessment, and autonomous root-cause investigation.

**Stack:** IBM Watsonx Orchestrate · ServiceNow · GitHub Actions API · Elasticsearch

**Agent Architecture:**
- `service_desk_assistant` — Main orchestrator
- `incident_logging_agent` — Logs incidents to ServiceNow
- `risk_mapping_agent` — RAG over Elasticsearch risk knowledge base
- `root_cause_agent` — Queries GitHub Actions API + ServiceNow for investigation
- `synthesis_agent` — Structured JSON synthesis

**Quick Start:**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Fill in instructor-provided credentials
python test_connections.py
python ingestion/create_indices.py
python ingestion/ingest_risk_docs.py
python ingestion/ingest_resolution_notes.py
python ingestion/ingest_deployments.py
bash import_to_orchestrate.sh
# Then open Watsonx Orchestrate and say:
# "I need help processing service desk emails"
```

---

## 🔧 Supplementary: Watsonx Orchestrate ADK

📄 [`Wxo-Bob/wxo-adk.md`](Wxo-Bob/wxo-adk.md)

A complete reference guide for the **IBM Watsonx Orchestrate Agent Development Kit (ADK)** — covers the `orchestrate` CLI, `@tool` decorator, YAML agent specs, and deployment workflows. Useful companion for Module 7.

---

## ✅ Before You Start

| Requirement | Details |
|-------------|---------|
| IBM Bob | Installed and connected in your editor |
| Python | 3.8+ (3.11 recommended for Module 7) |
| Java / Maven | Required for Module 1 |
| Go | Required for Module 4b (Golang error simulator) |
| OpenShift access | Required for Module 5 |
| Instana API key | Required for Modules 4b & 6 (sample data available as fallback) |
| Watsonx Orchestrate | IBM TechZone instance provided by instructor (Module 7) |
| ServiceNow dev instance | Provided by instructor (Module 7) |

---

## 📁 Full File Structure

```
Bob-Workshop-IBM-Indonesia/
├── 📄 README.md
│
├── 📁 Module 0 - Bob Introduction/
│   └── 📄 IBM-bob-trial-tutorial.pdf
│
├── 📁 Module-1-Java-Modernization/
│   ├── 📁 Module-Java Application/          # ⭐ Full Spring Boot app
│   │   ├── 📄 DEMO-GUIDE.md
│   │   ├── pom.xml
│   │   ├── frontend/
│   │   └── src/
│   └── 📁 Module-Java Simple/               # Backup: side-by-side comparison
│
├── 📁 Module-2-RPG-COBOL-Modernization/
│   ├── 📁 Module - COBOL Application/       # ⭐ Full COBOL app
│   │   ├── 📄 DEMO-GUIDE.md
│   │   ├── programs/                        # .CBL COBOL programs
│   │   ├── copybooks/                       # .CPY copybooks
│   │   ├── database/                        # PostgreSQL setup scripts
│   │   └── frontend/                        # Python/Flask frontend
│   └── 📁 Module -COBOL Simple/             # Backup: legacy vs modern
│
├── 📁 Module-3-DataScientist and ML/
│   ├── 📄 readme.md
│   ├── 📁 Data/                             # CSV trade datasets
│   ├── 📁 Instructions Guide/
│   │   └── 📄 IMPLEMENTATION_GUIDE.md       # ⭐ Main ML demo guide
│   └── 📁 Lineage Local/                    # Pre-generated lineage files
│
├── 📁 Module-4-Custom Demo Instana and Bank Loan/
│   ├── 📄 GUIDE.md                          # ⭐ Frontend QA workshop guide
│   ├── 📄 README.md
│   ├── 📁 bank-loan-app/                    # Node.js bank loan backend
│   ├── 📁 bank-loan-app-FE/                 # Standalone frontend
│   └── 📁 Instana aoutofix with Bob/
│       ├── 📄 Instana-Bob-GitLab-Integration-Plan.md
│       └── 📁 Demo Apps/golang-error-simulator/  # Go error simulator
│
├── 📁 Module-5-Deployment-Platform/
│   ├── 📄 DEMO-GUIDE.md                     # ⭐ Deployment platform guide
│   ├── 📁 k8s/                              # Namespace & RBAC manifests
│   ├── 📁 sample-app/                       # Sample Flask apps
│   └── 📁 web-ui/                           # Flask + SocketIO deployment UI
│
├── 📁 Module-6-Instana-SRE/
│   ├── 📄 README.md                         # ⭐ SRE lab guide
│   ├── 📄 fetch_instana_incidents.py
│   ├── 📄 workshop.md
│   ├── 📁 instana-mcp/                      # MCP server setup for Instana
│   └── 📁 .bob/                             # Bob SRE custom mode config
│
├── 📁 Module-7-Service-Desk-Assistant/
│   ├── 📄 DEMO-GUIDE.md                     # ⭐ Workshop demo guide
│   ├── 📄 COMPLETE_GUIDE.md                 # Full implementation reference
│   ├── 📁 agents/                           # Agent YAML specs + Python tools
│   ├── 📁 connections/                      # WXO connection definitions
│   ├── 📁 data/                             # Sample JSON knowledge base
│   ├── 📁 ingestion/                        # Elasticsearch ingestion scripts
│   ├── 📁 guardrails/                       # Input/output guardrail scripts
│   └── 📁 lab_exports/                      # Pre-built agent exports for import
│
└── 📁 Wxo-Bob/
    └── 📄 wxo-adk.md                        # Watsonx Orchestrate ADK guide
```

---

**Total Modules: 8** | **Main Demo Guides: 8 files** | **Demo Time: 30 min – 2.5 hours per module**
