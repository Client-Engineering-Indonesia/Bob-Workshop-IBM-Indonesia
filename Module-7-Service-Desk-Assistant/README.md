# Service Desk Assistant

> **AI-Powered Service Desk Automation with IBM Watsonx Orchestrate**

This project implements an intelligent service desk assistant that automates email processing, incident creation, risk assessment, and autonomous root-cause investigation using IBM Watsonx Orchestrate, Elasticsearch, ServiceNow, and GitHub.

---

## Start Here

**[DEMO-GUIDE.md](./DEMO-GUIDE.md)** — Workshop guide with step-by-step setup, exercises, and useful commands. Start here for the workshop.

**[COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md)** — Full implementation reference including ServiceNow configuration, tools and agents deep-dive, troubleshooting, and production deployment.

---

## Quick Start

> IBM TechZone instances (Watsonx Orchestrate, Watsonx Discovery) and a ServiceNow developer instance will be provided by your instructor. You only need to fill in the credentials they share with you.

```bash
# 1. Clone and enter the project
cd Service_desk_Assistant_T3

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure credentials
cp .env.example .env
# Open .env and fill in all values using the credentials from your instructor

# 5. Verify connections
python test_connections.py

# 6. Ingest sample data into Elasticsearch
python ingestion/create_indices.py
python ingestion/ingest_risk_docs.py
python ingestion/ingest_resolution_notes.py
python ingestion/ingest_deployments.py

# 7. Import everything to Watsonx Orchestrate
chmod +x import_to_orchestrate.sh
bash import_to_orchestrate.sh

# 8. Open Watsonx Orchestrate and say:
#    "I need help processing service desk emails"
```

---

## Architecture

The assistant routes between three workflows from a single conversational entry point:

```
User (Watsonx Orchestrate chat)
        |
        v
service_desk_assistant  (main orchestrator)
        |
        +-- Workflow A --> incident_logging_agent  --> ServiceNow
        |
        +-- Workflow B --> risk_mapping_agent      --> Elasticsearch (RAG)
        |
        +-- Workflow C --> root_cause_agent        --> GitHub + Elasticsearch + ServiceNow
```

| Workflow | Trigger | Output |
|---|---|---|
| A — Incident Logging | Service desk email content | ServiceNow incident ticket |
| B — Risk Mapping | Incident ID or description | Risk category + governance docs |
| C — Root-Cause Investigation | ServiceNow incident `sys_id` | 9 AI-enriched fields written to the ticket |

---

## Project Structure

```
Service_desk_Assistant_T3/
├── .env.example                   # Template for all required credentials
├── .gitignore
├── requirements.txt               # Full Python dependencies
├── requirements_tools.txt         # Minimal dependencies for WXO tool deployment
├── import_to_orchestrate.sh       # One-shot import: connections + tools + agents
├── run_investigation.py           # Hybrid Python runner for root-cause investigation
├── test_connections.py            # Verify external connections before deployment
├── test_local_tools.py            # Integration tests (no WXO needed)
├── verify_servicenow_fields.py    # Confirm all 9 AI fields exist in ServiceNow
│
├── agents/                        # Agent YAML definitions and Python tools
│   ├── service_desk_assistant.yml
│   ├── incident_logging_agent.yml
│   ├── risk_mapping_agent.yml
│   ├── root_cause_agent.yml
│   ├── synthesis_agent.yml
│   ├── servicenow_tools.py
│   ├── investigation_tools.py
│   └── risk_tools.py
│
├── connections/                   # Watsonx Orchestrate connection definitions
│   ├── servicenow-service-desk.yaml
│   ├── github-service-desk.yaml
│   ├── elasticsearch-service-desk.yaml
│   └── watsonx-ai-service-desk.yaml
│
├── ingestion/                     # Data ingestion scripts
│   ├── create_indices.py
│   ├── ingest_risk_docs.py
│   ├── ingest_resolution_notes.py
│   ├── ingest_deployments.py
│   └── es_client.py
│
├── data/                          # Sample data
│   ├── risk_docs/sample_risk_documents.json
│   ├── resolution_notes/sample_servicedesk_notes.json
│   └── deployments/sample_deployments.json
│
├── guardrails/                    # PII detection plugins
│   ├── guardrails_input.py
│   ├── guardrails_output.py
│   └── test_texts.py
│
└── lab_exports/                   # Pre-built Watsonx Orchestrate export packages
    ├── Service_Desk_Agent_Example/
    ├── risk_mapping_agent/
    └── root_cause_agent/
```

---

## Tools and Agents

**10 Tools:**

| Tool | File | Description |
|---|---|---|
| `create_servicenow_incident` | `servicenow_tools.py` | Create a new incident record |
| `get_servicenow_incident` | `servicenow_tools.py` | Read an incident by number or `sys_id` |
| `update_servicenow_incident` | `servicenow_tools.py` | Update an incident with idempotency guard |
| `retrieve_risk_documents` | `risk_tools.py` | Hybrid RAG search over governance documents |
| `retrieve_resolution_notes` | `risk_tools.py` | Hybrid RAG search over past resolutions |
| `query_recent_deployments` | `investigation_tools.py` | GitHub Actions runs near an incident timestamp |
| `query_commit_changes` | `investigation_tools.py` | Changed files and diff for a suspect commit |

**5 Agents:**

| Agent | Role |
|---|---|
| `service_desk_assistant` | Main orchestrator — routes between the three workflows |
| `incident_logging_agent` | Workflow A: processes emails, creates ServiceNow tickets |
| `risk_mapping_agent` | Workflow B: maps incidents to risk categories using RAG |
| `root_cause_agent` | Workflow C: 7-step autonomous investigation protocol |
| `synthesis_agent` | Step 5 only: JSON-only LLM hypothesis from evidence |

---

## Technology Stack

| Component | Technology |
|---|---|
| Orchestration | IBM Watsonx Orchestrate (ADK) |
| LLM | `gpt-oss-120b` via Watsonx |
| Knowledge Base | Elasticsearch 8.x (Watsonx Discovery) |
| Dense Embeddings | `intfloat/multilingual-e5-large` |
| Sparse Embeddings | ELSER (`.elser_model_2_linux-x86_64`) |
| ITSM | ServiceNow |
| CI/CD Source | GitHub Actions API |
| Guardrails | IBM Watson OpenScale |

---

## Security

- Never commit the `.env` file — it is already listed in `.gitignore`
- Use OAuth for ServiceNow in production
- Set `ES_VERIFY_CERTS=true` with a valid certificate in production
- Enable guardrails in production environments
