# Service Desk Assistant — Complete Workflow Guide

> **Stack:** IBM Watsonx Orchestrate · ServiceNow · GitHub · Elasticsearch (optional)  
> **Approach:** Multi-agent orchestration with autonomous root-cause investigation

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Agents](#3-agents)
4. [Tools](#4-tools)
5. [Connections](#5-connections)
6. [Workflow A — Email to Incident](#6-workflow-a--email-to-incident)
7. [Workflow B — Risk Mapping](#7-workflow-b--risk-mapping)
8. [Workflow C — Root-Cause Investigation](#8-workflow-c--root-cause-investigation)
9. [Investigation Pipeline in Detail](#9-investigation-pipeline-in-detail)
10. [Distributed Correctness Properties](#10-distributed-correctness-properties)
11. [ServiceNow AI Fields](#11-servicenow-ai-fields)
12. [Running the Investigation](#12-running-the-investigation)
13. [Graceful Degradation](#13-graceful-degradation)
14. [File Map](#14-file-map)

---

## 1. System Overview

The Service Desk Assistant automates three IT workflows that previously required human triage:

| Workflow | Trigger | Output |
|---|---|---|
| **A — Incident Logging** | Unread email in service desk inbox | ServiceNow incident ticket |
| **B — Risk Mapping** | Existing incident ID or description | Risk category + governance docs |
| **C — Root-Cause Investigation** | ServiceNow incident `sys_id` (Critical or High) | 9 AI-enriched fields written to the ticket |

A single conversational entry point — `service_desk_assistant` — routes users to the right workflow.

---

## 2. Architecture

### High-level system map

```mermaid
graph TB
    User([👤 User / Automation])

    subgraph WXO["IBM Watsonx Orchestrate"]
        SDA[service_desk_assistant<br/>Main Orchestrator]
        ILA[incident_logging_agent<br/>Team 1 · IT Support]
        RMA[risk_mapping_agent<br/>Team 2 · Risk & Compliance]
        RCA[root_cause_agent<br/>Team 3 · L2/L3 Engineering]
        SA[synthesis_agent<br/>JSON-only LLM]
    end

    subgraph Tools["Tools (Python)"]
        SNT["servicenow_tools.py<br/>create · get · update"]
        RT["risk_tools.py<br/>retrieve_risk_documents<br/>retrieve_resolution_notes"]
        IT["investigation_tools.py<br/>query_recent_deployments<br/>query_commit_changes"]
    end

    subgraph External["External Systems"]
        SNOW[(ServiceNow<br/>your-instance)]
        GH[(GitHub<br/>Actions API)]
        ES[(Elasticsearch<br/>RAG indices)]
    end

    subgraph Script["Local Runner"]
        RUN[run_investigation.py<br/>Hybrid Python driver]
    end

    User --> SDA
    User --> RUN

    SDA --> ILA
    SDA --> RMA
    SDA --> RCA

    ILA --> SNT
    RMA --> RT
    RCA --> IT
    RCA --> SNT
    RCA --> RT

    RUN --> SNT
    RUN --> IT
    RUN --> SA
    SA -.->|JSON hypothesis| RUN

    SNT --> SNOW
    RT --> ES
    IT --> GH
```

### Multi-agent routing

```mermaid
flowchart LR
    U([User]) --> SDA{service_desk_assistant}
    SDA -->|Workflow A| ILA[incident_logging_agent]
    SDA -->|Workflow B| RMA[risk_mapping_agent]
    SDA -->|Workflow C| RCA[root_cause_agent]
    ILA -->|New Critical/High incident| SDA
    SDA -->|Auto-suggest RCA| RCA
```

---

## 3. Agents

### `service_desk_assistant`
**Role:** Main orchestrator and conversational entry point.  
**Collaborators:** `incident_logging_agent`, `risk_mapping_agent`, `root_cause_agent`  
**Tools:** `get_servicenow_incident`

Routes users to one of three workflows. After `incident_logging_agent` creates a Critical (1) or High (2) urgency incident, it proactively offers to launch a root-cause investigation.

---

### `incident_logging_agent`
**Role:** Processes service desk emails and creates structured ServiceNow tickets.  
**Tools:** `create_servicenow_incident`

Extracts `short_description`, `description`, `caller_email`, `urgency` (1–4), and `category` from free-text email content. Validates all fields before writing. Never creates a ticket for invalid input.

---

### `risk_mapping_agent`
**Role:** Maps an incident to a risk category using RAG over governance documents.  
**Tools:** `retrieve_risk_documents`, `retrieve_resolution_notes`

Performs hybrid dense + sparse Elasticsearch search to surface relevant governance docs and past resolutions. Returns a risk category, severity, and recommended resolution.

---

### `root_cause_agent`
**Role:** Autonomous 7-step investigation agent. Given a `sys_id`, gathers evidence from GitHub and Elasticsearch, synthesises a hypothesis, and writes it to ServiceNow exactly once.  
**Tools:** `query_recent_deployments`, `query_commit_changes`, `retrieve_resolution_notes`, `get_servicenow_incident`, `update_servicenow_incident`

> **Note:** In practice, the cloud LLM (`gpt-oss-120b`) hits a per-turn tool-call budget before completing all 7 steps. The hybrid runner `run_investigation.py` is the production-grade way to run a complete investigation — it drives Steps 1, 2, 4, 6, and 7 in Python and delegates only Step 5 (synthesis) to `synthesis_agent`.

---

### `synthesis_agent`
**Role:** Single-purpose JSON-only LLM agent. Receives a structured evidence block and returns a strict JSON hypothesis object.  
**Tools:** _(none)_

No multi-step protocol. Responds with exactly one JSON object — no markdown, no preamble, no tool calls. Consumed programmatically by `run_investigation.py`.

---

## 4. Tools

### ServiceNow tools — `agents/servicenow_tools.py`

| Tool | Description |
|---|---|
| `create_servicenow_incident` | Creates a new incident record with standard + AI fields |
| `get_servicenow_incident` | Reads an incident by `ticket_number` OR `sys_id`; returns all 9 `u_ai_*` fields |
| `update_servicenow_incident` | PATCHes an incident; enforces **idempotency** on `u_ai_root_cause_hypothesis` (will not overwrite if already set) |

**Connection:** `servicenow-service-desk` (key-value: `SNOW_INSTANCE_URL`, `SNOW_USERNAME`, `SNOW_PASSWORD`)

---

### Risk & RAG tools — `agents/risk_tools.py`

| Tool | Description |
|---|---|
| `retrieve_risk_documents` | Hybrid semantic + sparse (ELSER) search over `risk_mapping_hybrid_index` |
| `retrieve_resolution_notes` | Hybrid search over `resolution_notes_hybrid_index` for past resolutions |

**Connection:** `elasticsearch-service-desk` + `watsonx-ai-service-desk`  
**Embeddings:** `intfloat/multilingual-e5-large` (dense) + `.elser_model_2_linux-x86_64` (sparse)

---

### GitHub investigation tools — `agents/investigation_tools.py`

| Tool | Description |
|---|---|
| `query_recent_deployments` | Lists GitHub Actions runs within ±N hours of an incident timestamp |
| `query_commit_changes` | Returns changed files, diff summary, author, and timestamp for a commit SHA |

Both tools follow the **graceful-degradation contract**: always return `{"status": "ok"|"unavailable", ...}` — never raise on external failure.

**Connection:** `github-service-desk` (key-value: `GITHUB_TOKEN`, `GITHUB_REPO_OWNER`, `GITHUB_REPO_NAME`)

---

## 5. Connections

| Connection name | Type | Variables | Used by |
|---|---|---|---|
| `servicenow-service-desk` | key_value | `SNOW_INSTANCE_URL`, `SNOW_USERNAME`, `SNOW_PASSWORD` | servicenow_tools |
| `github-service-desk` | key_value | `GITHUB_TOKEN`, `GITHUB_REPO_OWNER`, `GITHUB_REPO_NAME` | investigation_tools |
| `elasticsearch-service-desk` | key_value | `ES_HOST`, `ES_PORT`, `ES_USERNAME`, `ES_PASSWORD`, `ES_USE_SSL`, `ES_VERIFY_CERTS`, `ES_CERT_CONTENT` | risk_tools |
| `watsonx-ai-service-desk` | key_value | `WATSONX_URL`, `WATSONX_APIKEY`, `WATSONX_PROJECT_ID` | risk_tools (embeddings) |

All connections are registered in Watsonx Orchestrate for both `draft` and `live` environments via `import_to_orchestrate.sh`.

---

## 6. Workflow A — Email to Incident

```mermaid
sequenceDiagram
    actor User as IT Support
    participant SDA as service_desk_assistant
    participant ILA as incident_logging_agent
    participant SNOW as ServiceNow

    User->>SDA: "Process service desk emails"
    SDA->>ILA: delegate with instruction
    ILA->>ILA: Extract fields from email content
    Note over ILA: short_description, urgency,<br/>category, caller_email
    ILA->>SNOW: create_servicenow_incident(fields)
    SNOW-->>ILA: {number: INC0010023, sys_id: ...}
    ILA-->>SDA: Incident created ✅
    SDA-->>User: Display result

    alt urgency is Critical(1) or High(2)
        SDA->>User: "Launch root-cause investigation?"
        User->>SDA: "Yes"
        SDA->>SDA: Trigger Workflow C with sys_id
    end
```

**Entry point:** `service_desk_assistant` → delegates to `incident_logging_agent`  
**Output:** ServiceNow ticket with number, URL, extracted fields  
**Auto-trigger:** If urgency ≤ 2, orchestrator offers to start root-cause investigation

---

## 7. Workflow B — Risk Mapping

```mermaid
sequenceDiagram
    actor User as Risk & Compliance
    participant SDA as service_desk_assistant
    participant RMA as risk_mapping_agent
    participant ES as Elasticsearch

    User->>SDA: "Map INC0010023 to a risk category"
    SDA->>RMA: delegate with incident description
    RMA->>ES: retrieve_risk_documents(query)
    ES-->>RMA: Top-k governance docs (hybrid search)
    RMA->>ES: retrieve_resolution_notes(query)
    ES-->>RMA: Top-k past resolutions
    RMA->>RMA: Map to risk category + severity
    RMA-->>SDA: Risk category, docs, resolution steps
    SDA-->>User: Display risk assessment
```

**Entry point:** `service_desk_assistant` → delegates to `risk_mapping_agent`  
**Output:** Risk category, relevant governance documents, recommended resolution

---

## 8. Workflow C — Root-Cause Investigation

```mermaid
sequenceDiagram
    actor User as L2/L3 Engineer
    participant RUN as run_investigation.py
    participant SNOW as ServiceNow
    participant GH as GitHub Actions API
    participant SA as synthesis_agent (LLM)

    User->>RUN: python3 run_investigation.py [sys_id]

    Note over RUN,SNOW: STEP 1 — Read incident
    RUN->>SNOW: get_servicenow_incident(sys_id)
    SNOW-->>RUN: {number, description, opened_at, u_ai_*: null}

    Note over RUN,SNOW: STEP 2 — Acquire lock
    RUN->>SNOW: update_servicenow_incident(lock="root_cause_agent:LOCKED", status="in_progress")
    SNOW-->>RUN: success=True

    Note over RUN: STEP 3 — Idempotency check
    RUN->>RUN: if hypothesis already set → stop

    Note over RUN,GH: STEP 4 — Gather evidence
    RUN->>GH: query_recent_deployments(incident_time, window_hours=2)
    GH-->>RUN: {runs: [...], total_found: N}
    RUN->>GH: query_commit_changes(suspect_sha)
    GH-->>RUN: {changed_files, additions, deletions}
    Note over RUN: ES resolution notes skipped<br/>(placeholder creds)

    Note over RUN,SA: STEP 5 — Synthesise hypothesis
    RUN->>SA: evidence JSON prompt
    SA-->>RUN: {"hypothesis":"...", "confidence_score":N, ...}

    Note over RUN,SNOW: STEP 6 — Write to ServiceNow
    RUN->>SNOW: update_servicenow_incident(all 9 u_ai_* fields)
    SNOW-->>RUN: success=True, skipped_hypothesis_write=False

    Note over RUN,SNOW: STEP 7 — Verify
    RUN->>SNOW: get_servicenow_incident(sys_id)
    SNOW-->>RUN: all u_ai_* fields confirmed
    RUN-->>User: ✅ 6/7 fields written · URL: https://your-instance.service-now.com/...
```

---

## 9. Investigation Pipeline in Detail

The investigation is a **hybrid Python + LLM pipeline**. Python handles all deterministic steps; the LLM only reasons over pre-gathered, pre-formatted evidence.

```mermaid
flowchart TD
    START([python3 run_investigation.py sys_id]) --> S1

    S1["📥 STEP 1\nget_servicenow_incident\n→ read incident record"]
    S1 --> S2

    S2["🔒 STEP 2\nupdate_servicenow_incident\n→ write investigation lock\nlock = 'root_cause_agent:LOCKED'\nstatus = 'in_progress'"]
    S2 --> S3

    S3{Hypothesis\nalready set?}
    S3 -->|Yes| STOP1[Release lock\nExit — already investigated]
    S3 -->|No| S4

    S4["📡 STEP 4\nScatter-gather evidence\n① query_recent_deployments ±2h\n② query_commit_changes on suspect SHA\n③ retrieve_resolution_notes (if ES available)"]
    S4 --> GAPS{Evidence\ngaps?}
    GAPS -->|All unavailable| S5b["status = no_evidence_found\nconfidence = 0"]
    GAPS -->|Some available| S5a["status = incomplete | complete\nconfidence = 10–100"]
    S5a --> S5
    S5b --> S5

    S5["🧠 STEP 5\nsynthesis_agent call\n→ send evidence JSON prompt\n→ receive strict JSON hypothesis\n{hypothesis, evidence_summary,\nconfidence_score, next_step, status}"]
    S5 --> S6

    S6["✅ STEP 6\nupdate_servicenow_incident\n→ write all 9 u_ai_* fields\n→ release lock (lock = '')"]
    S6 --> IDEM{skipped_hypothesis\n_write?}
    IDEM -->|True| STOP2[Another agent committed\nLock released · Exit]
    IDEM -->|False| S7

    S7["🔍 STEP 7\nget_servicenow_incident\n→ verify all fields written\n→ print confirmation + URL"]
    S7 --> END([✅ Investigation complete])
```

### Step responsibilities

| Step | Who | What |
|---|---|---|
| 1 | Python | Read incident from ServiceNow |
| 2 | Python | Write investigation lock (idempotent, always succeeds) |
| 3 | Python | Check if hypothesis already set — exit if yes |
| 4 | Python | Call GitHub Actions API + commit API directly |
| 5 | **LLM** (`synthesis_agent`) | Reason over evidence → return JSON hypothesis |
| 6 | Python | PATCH all 9 `u_ai_*` fields + release lock |
| 7 | Python | Read-back verify + print URL |

---

## 10. Distributed Correctness Properties

### Investigation lock (leader election)

Before gathering evidence, the runner writes `u_ai_investigation_lock = "root_cause_agent:LOCKED"` to the ServiceNow incident. This prevents two concurrent runners from both writing a hypothesis.

```mermaid
sequenceDiagram
    participant R1 as Runner 1
    participant SNOW as ServiceNow
    participant R2 as Runner 2

    R1->>SNOW: PATCH lock="root_cause_agent:LOCKED"
    R2->>SNOW: PATCH lock="root_cause_agent:LOCKED"
    Note over SNOW: Both writes succeed (last-writer wins)<br/>Only one proceeds to Step 6

    R1->>SNOW: PATCH hypothesis + lock=""
    Note over R1: success=True, skipped=False ✅

    R2->>SNOW: PATCH hypothesis (idempotency check)
    SNOW-->>R2: skipped_hypothesis_write=True
    Note over R2: Hypothesis already set — skip write ✅
```

### Idempotency (exactly-once write)

`update_servicenow_incident` reads the current value of `u_ai_root_cause_hypothesis` before every hypothesis write. If it is already non-empty, the tool:
- Returns `skipped_hypothesis_write = True`
- Skips all 7 content fields
- Still allows lock and status fields through

This guarantees the hypothesis is written **at most once**, even if the runner is called multiple times for the same incident.

### Graceful degradation

Every tool returns `{"status": "ok" | "unavailable", ...}` and never raises. If a source is down:

| Source unavailable | Effect |
|---|---|
| GitHub API | `evidence_gaps = ["github_deployments"]` — investigation continues with ES only |
| Elasticsearch | `evidence_gaps = ["elasticsearch"]` — investigation continues with GitHub only |
| Both | `investigation_status = "no_evidence_found"`, `confidence_score = 0` — still writes to ServiceNow |
| ServiceNow write fails | Retry up to 3× — lock left in place if all retries fail |

---

## 11. ServiceNow AI Fields

All 9 fields are on the `incident` table, created via REST API (`sys_dictionary`):

| Field name | Type | Purpose |
|---|---|---|
| `u_ai_root_cause_hypothesis` | `string` | 2–4 sentence plain-English root cause |
| `u_ai_evidence_summary` | `string` | Bullet list of every evidence source used |
| `u_ai_suspect_commit` | `string` | GitHub commit SHA implicated in the incident |
| `u_ai_suspect_deployment` | `string` | GitHub Actions run ID implicated |
| `u_ai_confidence_score` | `string` | Integer 0–100; 0–30 weak, 31–60 moderate, 61–100 strong |
| `u_ai_recommended_next_step` | `string` | One concrete action for the L2/L3 engineer |
| `u_ai_evidence_gaps` | `string` | JSON array of unavailable source names |
| `u_ai_investigation_lock` | `string` | `"root_cause_agent:LOCKED"` when active, `""` when released |
| `u_ai_investigation_status` | `string` | `in_progress` → `complete` / `incomplete` / `no_evidence_found` |

### Field lifecycle

```mermaid
stateDiagram-v2
    [*] --> empty : Incident created
    empty --> in_progress : Runner acquires lock\nwrites u_ai_investigation_status
    in_progress --> complete : All evidence sources available\nconfidence ≥ 61
    in_progress --> incomplete : Some sources unavailable\n(evidence_gaps non-empty)
    in_progress --> no_evidence_found : All sources unavailable
    complete --> [*] : Lock released (u_ai_investigation_lock = "")
    incomplete --> [*] : Lock released
    no_evidence_found --> [*] : Lock released
```

---

## 12. Running the Investigation

### Prerequisites

```bash
# 1. Activate Watsonx Orchestrate environment (once per ~1 hour session)
WXO_APIKEY=$(grep "^WXO_APIKEY=" .env | cut -d'=' -f2-)
orchestrate env activate servicedesk_assistant --api-key "$WXO_APIKEY"
```

### Run on default incident (INC0000060)

```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 run_investigation.py
```

### Run on a specific incident

```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 run_investigation.py <sys_id>

# Example (replace with your incident sys_id from ServiceNow):
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 run_investigation.py <your-incident-sys-id>
```

### Expected output

```
════════════════════════════════════════════════════════════
  🚀 ROOT-CAUSE INVESTIGATION
────────────────────────────────────────────────────────────
  Incident sys_id: 1c741bd70b2322007518478d83673af3
  Time:            2026-07-09T13:29:24Z

════════════════════════════════════════════════════════════
  STEP 1 — Read incident
────────────────────────────────────────────────────────────
  ✅ INC0000060 — Unable to connect to email
     Opened: 2016-12-12 15:19:57  Urgency: 2

════════════════════════════════════════════════════════════
  STEP 2 — Acquire investigation lock
────────────────────────────────────────────────────────────
  ✅ Lock acquired: root_cause_agent:LOCKED

════════════════════════════════════════════════════════════
  STEP 4 — Gather evidence
────────────────────────────────────────────────────────────
  ✅ Deployments: 0 runs in ±2h window
  ⚠️  No deployment runs found in time window
  ⚠️  Resolution notes: ES not configured — skipping
  Evidence gaps: ['no_suspect_sha', 'elasticsearch']

════════════════════════════════════════════════════════════
  STEP 5 — Synthesise hypothesis (LLM)
────────────────────────────────────────────────────────────
  → Calling synthesis_agent...
  ✅ Hypothesis parsed from LLM response

════════════════════════════════════════════════════════════
  🧠 HYPOTHESIS
  The email connectivity issue likely stems from an
  external factor such as the email server being down
  or network problems, as no recent code changes were found.
  Confidence: 10/100  Status: no_evidence_found

════════════════════════════════════════════════════════════
  STEP 6 — Write to ServiceNow
────────────────────────────────────────────────────────────
  ✅ ServiceNow updated: INC0000060

════════════════════════════════════════════════════════════
  STEP 7 — Verify ServiceNow fields
────────────────────────────────────────────────────────────
  ✅ u_ai_root_cause_hypothesis
  ✅ u_ai_evidence_summary
  ✅ u_ai_confidence_score
  ✅ u_ai_recommended_next_step
  ✅ u_ai_evidence_gaps
  ✅ u_ai_investigation_status
  ⬜ u_ai_investigation_lock: (empty — lock released)

════════════════════════════════════════════════════════════
  ✅ INVESTIGATION COMPLETE  6/7 fields written
  Incident URL: https://your-instance.service-now.com/...
```

### Local unit tests

```bash
# Run all tool-level tests (21 assertions, ~15s)
source .venv/bin/activate
python3 test_local_tools.py
```

### Import all agents and tools to WXO

```bash
bash import_to_orchestrate.sh
```

---

## 13. Graceful Degradation

```mermaid
flowchart TD
    S4[STEP 4: Gather evidence]

    S4 --> D1{GitHub API\navailable?}
    D1 -->|Yes| D1Y[query_recent_deployments\nquery_commit_changes]
    D1 -->|No| D1N["evidence_gaps += ['github_deployments']\nevidence_gaps += ['no_suspect_sha']"]

    S4 --> D2{Elasticsearch\navailable?}
    D2 -->|Yes| D2Y[retrieve_resolution_notes]
    D2 -->|No| D2N["evidence_gaps += ['elasticsearch']"]

    D1Y --> MERGE[Merge all available evidence]
    D1N --> MERGE
    D2Y --> MERGE
    D2N --> MERGE

    MERGE --> D3{Any evidence\ncollected?}
    D3 -->|Yes| HYP["synthesis_agent\n→ hypothesis with gaps noted\nstatus = incomplete"]
    D3 -->|No| NOHYP["status = no_evidence_found\nconfidence = 0\nstill writes to ServiceNow"]

    HYP --> WRITE[STEP 6: Write to ServiceNow]
    NOHYP --> WRITE
```

The pipeline **always completes** — it never crashes on external failure. In the worst case (all sources down), it writes `status = no_evidence_found` with `confidence_score = 0` so the engineer knows the investigation ran but found nothing.

---

## 14. File Map

```
Service_desk_Assistant_T3/
│
├── .env                          # Real credentials (git-ignored)
├── .env.example                  # Template with all required keys
├── import_to_orchestrate.sh      # One-shot: connections + tools + agents → WXO
├── run_investigation.py          # Hybrid runner: Python steps 1,2,4,6,7 + LLM step 5
├── test_local_tools.py           # 21 integration assertions (no WXO needed)
├── test_connections.py           # Original connection + scenario tests
├── requirements.txt              # Full Python deps
├── requirements_tools.txt        # Minimal deps for WXO tool deployment
│
├── agents/
│   ├── service_desk_assistant.yml  # Main orchestrator (3 teams, auto-trigger)
│   ├── incident_logging_agent.yml  # Workflow A: email → incident
│   ├── risk_mapping_agent.yml      # Workflow B: incident → risk category
│   ├── root_cause_agent.yml        # Workflow C: 7-step investigation protocol
│   ├── synthesis_agent.yml         # Step 5 only: JSON-only LLM hypothesis
│   ├── servicenow_tools.py         # create / get / update + idempotency
│   ├── investigation_tools.py      # GitHub Actions + Commits APIs
│   └── risk_tools.py               # ES hybrid RAG tools
│
├── connections/
│   ├── servicenow-service-desk.yaml
│   ├── github-service-desk.yaml
│   ├── elasticsearch-service-desk.yaml
│   └── watsonx-ai-service-desk.yaml
│
├── ingestion/
│   ├── create_indices.py           # Create ES indices (risk, resolution, deployments)
│   ├── ingest_risk_docs.py
│   ├── ingest_resolution_notes.py
│   └── ingest_deployments.py       # Index GitHub Actions sample data
│
├── data/
│   ├── risk_docs/sample_risk_documents.json
│   ├── resolution_notes/sample_servicedesk_notes.json
│   └── deployments/sample_deployments.json   # 8 GitHub Actions run records
│
├── guardrails/
│   ├── guardrails_input.py         # Pre-invoke PII detection
│   ├── guardrails_output.py        # Post-invoke PII detection
│   └── test_texts.py
│
└── lab_exports/
    ├── Service_Desk_Agent_Example/ # Original T3 WXO export
    ├── risk_mapping_agent/
    └── root_cause_agent/           # Full export package (agent + tools + connections)
```