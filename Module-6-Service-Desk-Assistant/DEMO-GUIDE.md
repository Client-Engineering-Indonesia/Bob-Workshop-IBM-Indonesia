# Service Desk Assistant

> **AI-Powered Service Desk Automation with IBM Watsonx Orchestrate**

This project implements an intelligent service desk assistant that automates email processing, incident creation, risk assessment, and resolution recommendations using IBM Watsonx Orchestrate, Elasticsearch, and ServiceNow.

---

## Documentation

**[Complete Implementation Guide](./COMPLETE_GUIDE.md)** - Your one-stop guide for everything! It is an ADK-based solution.

**[Email to Incident UI Setup Guide](./Email_to_Incident_UI_Setup_Guide.md)** - UI-based setup for a no-code/low-code Email-to-Incident solution through Watsonx Orchestrate.

**[ServiceNow Dev Instance Setup](./service_now_dev_instance_setup.md)** - Guide for setting up a ServiceNow developer instance.

The complete guide includes:
- Solution Architecture
- Quick Start (15 minutes)
- Environment Setup
- ServiceNow Configuration
- Data Ingestion
- Tools & Agents Reference
- Import Instructions
- UI Test Scenarios
- Development Patterns
- Troubleshooting
- Production Deployment

---

## Quick Start

### Option A: Using `uv`

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Initialize project and create virtual environment
cd Service_desk_Assistant_T3
uv init
uv venv
source .venv/bin/activate

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Setup data
python test_connections.py
python ingestion/create_indices.py
python ingestion/ingest_risk_docs.py
python ingestion/ingest_resolution_notes.py

# 5. Import to Watsonx Orchestrate
chmod +x import_to_orchestrate.sh
bash import_to_orchestrate.sh

# 6. Test in UI
# Open Watsonx Orchestrate and say: "I need help processing service desk emails"
```

### Option B: Using `pip` + `venv`

```bash
# 1. Install dependencies
cd Service_desk_Assistant_T3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
# Create .env file with your credentials (see COMPLETE_GUIDE.md)

# 3. Setup data
python test_connections.py
python ingestion/create_indices.py
python ingestion/ingest_risk_docs.py
python ingestion/ingest_resolution_notes.py

# 4. Import to Watsonx Orchestrate
chmod +x import_to_orchestrate.sh
bash import_to_orchestrate.sh

# 5. Test in UI
# Open Watsonx Orchestrate and say: "I need help processing service desk emails"
```

---

## Connections Setup

The tools use two Watsonx Orchestrate connections for credentials. Import them before deploying the tools.

### 1. Import connection definitions

```bash
orchestrate connections import -f connections/elasticsearch-service-desk.yaml
orchestrate connections import -f connections/watsonx-ai-service-desk.yaml
```

### 2. Set credential values

**Elasticsearch** (`elasticsearch-service-desk`):

```bash
orchestrate connections set-credentials -a elasticsearch-service-desk \
  --env draft \
  -e 'ES_HOST=your-es-host' \
  -e 'ES_PORT=9200' \
  -e 'ES_USERNAME=your-username' \
  -e 'ES_PASSWORD=your-password' \
  -e 'ES_USE_SSL=true' \
  -e 'ES_VERIFY_CERTS=false' \
  -e 'ES_CERT_CONTENT=your-cert-content'
```

**WatsonX AI** (`watsonx-ai-service-desk`):

```bash
orchestrate connections set-credentials -a watsonx-ai-service-desk \
  --env draft \
  -e 'WATSONX_URL=https://us-south.ml.cloud.ibm.com' \
  -e 'WATSONX_APIKEY=your-ibm-cloud-api-key' \
  -e 'WATSONX_PROJECT_ID=your-project-id'
```

Connection YAML files are in the [`connections/`](./connections/) directory.

---

## Architecture

Two separate teams interact with the service desk assistant through distinct workflows:

```
IT Support Team                       Risk & Compliance Team
       │                                       │
       ▼                                       ▼
fetch_service_desk_emails          retrieve_risk_documents (RAG)
       │                                       │
       ▼                                       ▼
incident_logging_agent             risk_mapping_agent
       │                                       │
       ▼                                       ▼
create_servicenow_incident         Risk Category + Governance Docs
       │                                       │
       ▼                                       ▼
update_servicenow_incident         Elasticsearch Knowledge Base
  (risk + resolution fields)
       │
       ▼
retrieve_resolution_notes (RAG)
```

**7 Tools:**
- ServiceNow: `create_servicenow_incident`, `get_servicenow_incident`, `update_servicenow_incident`
- Email: `fetch_service_desk_emails`, `send_incident_notification_email`
- RAG: `retrieve_risk_documents`, `retrieve_resolution_notes`

**3 Agents:**
- `incident_logging_agent` — processes emails and creates ServiceNow incidents
- `risk_mapping_agent` — maps incidents to risk categories using RAG
- `service_desk_assistant` — main orchestrator coordinating the full workflow

---

## Project Structure

```
Service_desk_Assistant_T3/
├── .env                           # Environment variables (create from template)
├── .gitignore                     # Git ignore patterns
├── requirements.txt               # Python dependencies
├── requirements_tools.txt         # Minimal tool dependencies for deployment
├── COMPLETE_GUIDE.md              # Complete implementation guide
├── Email_to_Incident_UI_Setup_Guide.md  # No-code UI setup guide
├── service_now_dev_instance_setup.md    # ServiceNow dev instance guide
├── README.md                      # This file
├── import_to_orchestrate.sh       # Import script
├── test_connections.py            # Connection tester
│
├── agents/                        # Agent definitions and tools
│   ├── risk_tools.py             # RAG tools: retrieve_risk_documents, retrieve_resolution_notes
│   ├── incident_logging_agent.yml # Incident creation agent
│   ├── risk_mapping_agent.yml    # Risk assessment agent
│   └── service_desk_assistant.yml # Main orchestrator agent
│
├── connections/                   # Watsonx Orchestrate connection definitions
│   ├── elasticsearch-service-desk.yaml
│   └── watsonx-ai-service-desk.yaml
│
├── ingestion/                     # Data ingestion scripts
│   ├── es_client.py              # Elasticsearch client wrapper
│   ├── create_indices.py         # Create Elasticsearch indices
│   ├── ingest_risk_docs.py       # Ingest risk governance documents
│   ├── ingest_resolution_notes.py # Ingest past incident resolutions
│   └── search.py                 # Search utilities
│
├── data/                          # Sample data (JSON format)
│   ├── risk_docs/                # Risk governance documents
│   │   └── sample_risk_documents.json
│   └── resolution_notes/         # Past incident resolutions
│       └── sample_servicedesk_notes.json
│
├── guardrails/                    # PII guardrails (input + output)
│   ├── guardrails_input.py       # Pre-invoke PII enforcement (IBM OpenScale)
│   ├── guardrails_output.py      # Post-invoke PII enforcement (IBM OpenScale)
│   └── test_texts.py             # 10 PII + 10 non-PII test cases
│
└── lab_exports/                   # Pre-built Watsonx Orchestrate export packages
    ├── Service_Desk_Agent_Example/ # Full service desk agent export
    └── risk_mapping_agent/        # Risk mapping agent export
```

### Key Files

**Configuration:**
- `.env` - Environment variables (credentials, endpoints)
- `requirements.txt` - Full Python dependencies
- `requirements_tools.txt` - Minimal dependencies for deployment

**Deployment:**
- `import_to_orchestrate.sh` - Import script
- `test_connections.py` - Verify all connections before deployment

**Tools (7 total):**
- `agents/risk_tools.py` - `retrieve_risk_documents`, `retrieve_resolution_notes`
- ServiceNow tools (`create_servicenow_incident`, `get_servicenow_incident`, `update_servicenow_incident`) and email tools (`fetch_service_desk_emails`, `send_incident_notification_email`) are imported via `lab_exports/`

**Agents (3 total):**
- `agents/incident_logging_agent.yml` - Processes emails, creates incidents
- `agents/risk_mapping_agent.yml` - Assesses risk using RAG
- `agents/service_desk_assistant.yml` - Main orchestrator

**Data Ingestion:**
- `ingestion/create_indices.py` - Creates Elasticsearch indices
- `ingestion/ingest_risk_docs.py` - Loads risk documents
- `ingestion/ingest_resolution_notes.py` - Loads resolution history

---

## Technology Stack

| Component | Technology |
|---|---|
| **Orchestration** | IBM Watsonx Orchestrate |
| **LLM** | groq/openai/gpt-oss-120b |
| **Knowledge Base** | Elasticsearch 8.x |
| **Dense Embeddings** | WatsonxEmbeddings (`intfloat/multilingual-e5-large`) |
| **Sparse Embeddings** | ELSER (`.elser_model_2_linux-x86_64`) |
| **ITSM** | ServiceNow |
| **Email** | Gmail IMAP |

---

## Key Features

- **Automated Email Processing** - Fetches and processes service desk emails
- **Intelligent Incident Creation** - Extracts structured data from emails and logs to ServiceNow
- **Risk Assessment** - Maps incidents to risk categories using RAG over Elasticsearch
- **Resolution Recommendations** - Finds similar past incidents with resolution steps
- **ServiceNow Integration** - Creates and updates incidents with AI-generated insights
- **Natural Language Interface** - Conversational UI in Watsonx Orchestrate
- **Guardrails** - PII detection, validation, escalation rules

---

## Troubleshooting

See the [Troubleshooting section](./COMPLETE_GUIDE.md#11-troubleshooting) in the Complete Guide for solutions to common issues.

---

## Guardrails

The `guardrails/` directory contains PII enforcement scripts that call the IBM Watson OpenScale Guardrails API. They can be used standalone for testing or deployed as **Watsonx Orchestrate plugins** to automatically intercept agent input/output.

### Standalone usage

```bash
cd guardrails
python guardrails_input.py    # Test input PII detection
python guardrails_output.py   # Test output PII detection
python test_texts.py          # Run 20 test cases (10 PII + 10 clean)
```

Requires `WATSONX_APIKEY` in `.env` — a bearer token is fetched automatically.

### As Watsonx Orchestrate plugins

Plugins run automatically in the agent processing flow without the agent needing to call them:

- `guardrails_input.py` → **pre-invoke plugin** (screens user input before agent runs)
- `guardrails_output.py` → **post-invoke plugin** (screens agent response before returning to user)

> **Note:** `guardrails_plugin.py` is not included in this repo. To deploy as a plugin, adapt the guardrail scripts using the plugin decorator pattern. See [WxGov_plugin.py](https://github.ibm.com/jerome-joubert/WxO-Plugins/blob/main/WxGov_plugin.py) for a reference implementation.

Import and register:

```bash
orchestrate tools import -k python -f guardrails/guardrails_plugin.py
```

Then add to your agent YAML under `plugins.agent_pre_invoke` or `plugins.agent_post_invoke`.

**References:**
- [Plugin documentation](https://developer.watson-orchestrate.ibm.com/plugins/plugins)
- [Plugin reference examples](https://github.ibm.com/jerome-joubert/WxO-Plugins)

---

## Security

- Never commit `.env` file
- Use OAuth for ServiceNow in production
- Enable all guardrails in production
- Set `ES_VERIFY_CERTS=true` for production
