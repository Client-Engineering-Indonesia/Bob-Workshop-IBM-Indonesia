# Root-Cause Investigation — System Design & Distributed Architecture

This document captures the product direction and distributed system design for extending
[`Service Desk Assistant`](README.md) toward the use case of **Autonomous Root-Cause
Investigation Across GitHub Deployments, Historical Incidents, and ServiceNow Context**.

The primary technologies are **IBM Watsonx Orchestrate, GitHub, Elasticsearch, and
ServiceNow**. The document has been extended to reason rigorously about distributed
systems properties, failure models, coordination algorithms, and correctness guarantees —
not only application orchestration.

---

## 1. Recommended Primary Use Case

### Use Case #1 — Autonomous Root-Cause Investigation

This is the strongest next-step use case to build from the current
[`Service_desk_Assistant_T3`](README.md) foundation, and also the one that most naturally
surfaces distributed systems challenges.

### Why not lead with Ticket-to-PR?

Use case #2 (Ticket-to-PR) is well-covered by developer-facing tools (GitHub Copilot,
Cursor, Devin, Amazon Q Developer). It does not differentiate an IT Service Desk product.

Root-cause investigation is harder and more defensible: it requires an agent to reason
across multiple independent, asynchronous, failure-prone systems under real-time constraints —
which is precisely the domain of distributed algorithms.

---

## 2. Why Use Case #1 Wins in the 2026 Market

### 2.1 MTTR is the clearest enterprise metric

Mean Time to Resolve (MTTR) is measurable, SLA-linked, and board-visible. A solution that
reduces investigation time from 45 minutes to 90 seconds carries a dollar figure in every
sales conversation.

### 2.2 The competitive moat requires distributed reasoning

Competing products attack L1 deflection. Root-cause investigation requires:
- concurrent access to multiple independent systems (GitHub, Elasticsearch, ServiceNow)
- temporal reasoning: *what changed in the two hours before this incident?*
- evidence synthesis across asynchronous, partial, possibly stale or conflicting data sources

These are distributed systems problems, not chatbot problems. The stack behind
[`Service_desk_Assistant_T3`](README.md) — Watsonx Orchestrate, Elasticsearch, ServiceNow —
naturally maps onto a distributed investigation pipeline.

### 2.3 The foundation is already partially built

| Existing capability | Distributed relevance |
|---|---|
| Elasticsearch hybrid RAG ([`agents/risk_tools.py`](agents/risk_tools.py)) | Replicated, queryable shared state for historical incidents |
| ServiceNow incident tools | Authoritative shared record with write-once commit semantics |
| Multi-agent Watsonx Orchestrate architecture | Logical group of concurrent investigation processes |
| Tool-based `@tool` extension pattern | Well-defined interface for adding new distributed data sources |

The project does **not** need a redesign. It needs a distributed systems overlay.

---

## 3. Revised Project Description

**Bob for Service Desk** is a fault-tolerant, event-driven investigation system that, upon
detection of a production incident, autonomously coordinates a set of distributed
investigation agents to gather evidence from GitHub (deployment and commit history) and
Elasticsearch (historical incident knowledge base), synthesizes a root-cause hypothesis
using a language model, and commits that hypothesis — under exactly-once semantics — back
to ServiceNow as a structured, human-reviewable diagnostic record.

The system must produce correct results in the presence of partial failures, message
duplication, network latency variance, and temporary unavailability of any single
external data source.

---

## 4. System Architecture

### 4.1 Distributed Components

| Component | Role | State |
|---|---|---|
| **Orchestrator Agent** (Watsonx Orchestrate) | Coordinates the investigation workflow; acts as group coordinator | Stateless between invocations; incident `sys_id` is the coordination key |
| **GitHub Investigation Tool** (`investigation_tools.py`) | Queries GitHub Actions and Commits APIs | Stateless; reads external system |
| **Elasticsearch RAG Tool** ([`agents/risk_tools.py`](agents/risk_tools.py)) | Searches historical incident resolutions | Reads from replicated Elasticsearch cluster |
| **ServiceNow Incident Store** | Authoritative record; single source of truth for incident state | Persistent, append-friendly, write-gated by field idempotency check |
| **Email Notification Channel** | Delivers L2/L3 handoff brief | Async, at-least-once delivery |
| **Guardrails Layer** ([`guardrails/`](guardrails/)) | Pre/post-invoke PII scan | Synchronous inline filter |

### 4.2 Communication Model

All communication between the Orchestrator and external systems is **request/response
over HTTPS** (point-to-point, synchronous from the agent's perspective). Internally,
tool invocations within a Watsonx Orchestrate agent are **sequential by default** and can
be made concurrent via parallel tool calls.

The system uses an **event-driven entry point**: an incident creation event in ServiceNow
(or an inbound email intake) triggers the investigation pipeline. This decouples the
trigger from the investigation logic.

```
Trigger source                   Orchestrator                   External services
─────────────                    ────────────                   ─────────────────
ServiceNow incident   ─────────► Watsonx Agent  ──────────────► GitHub API
  (event / polling)              (coordinator)  ──────────────► Elasticsearch
                                                ──────────────► ServiceNow (write)
                                                ──────────────► Email SMTP
```

### 4.3 Revised Architecture Diagram

```text
┌───────────────────────────────────────────────────────────────────┐
│                       IBM Watsonx Orchestrate                     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │          Root-Cause Orchestrator (Coordinator)              │  │
│  │                                                             │  │
│  │  1. Receive incident event (incident_id, service, time)     │  │
│  │  2. Acquire investigation lock on incident_id               │  │
│  │  3. Fan out to investigation tools (concurrent)             │  │
│  │  4. Collect partial results with timeout                    │  │
│  │  5. Synthesize hypothesis from available evidence           │  │
│  │  6. Commit to ServiceNow (idempotent write)                 │  │
│  │  7. Broadcast notification (reliable, at-least-once)        │  │
│  │  8. Release investigation lock                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│        │               │                │                         │
│        ▼               ▼                ▼                         │
│  ┌──────────┐   ┌────────────┐   ┌───────────────┐               │
│  │ GitHub   │   │Elasticsearch│  │  ServiceNow   │               │
│  │ Tools    │   │ RAG Tools  │   │  Incident     │               │
│  │ (read)   │   │  (read)    │   │  Store (r/w)  │               │
│  └──────────┘   └────────────┘   └───────────────┘               │
│        │               │                │                         │
└────────┼───────────────┼────────────────┼─────────────────────────┘
         │               │                │
         ▼               ▼                ▼
   GitHub API    Elasticsearch      ServiceNow REST
  (Actions/      (hybrid index)      (Table API)
   Commits)

Failure paths:
  GitHub unavailable  ──► skip deployment evidence, flag incomplete
  Elasticsearch down  ──► skip historical correlation, flag incomplete
  ServiceNow write fails ──► retry with idempotency key, do not duplicate
  Agent crash ──────────► incident lock expires, re-triggerable
```

---

## 5. Distributed Systems Design

### 5.1 System Model

**Assumptions:**

- All communication is asynchronous. External API calls (GitHub, Elasticsearch,
  ServiceNow) may be delayed arbitrarily within a bounded timeout window.
- The system operates in a **partial synchrony** model: message delivery is not
  guaranteed within a fixed time, but eventually occurs unless the remote system is
  permanently down.
- Any external service (GitHub, Elasticsearch, ServiceNow) may fail independently.
  Failures are **crash-stop or crash-recover** (not Byzantine).
- The Watsonx Orchestrate agent is a single logical process per investigation invocation.
  Multiple invocations of the same incident are possible (e.g. duplicate events).
- ServiceNow is the authoritative shared state. Elasticsearch is read-only from this
  system's perspective. GitHub is read-only.
- Network partitions between the Orchestrator and any single external service are
  possible. Partitions are transient.

**Timing model:**

- Tool call timeout: 30 seconds per tool invocation (configurable).
- Investigation timeout: 120 seconds total before partial synthesis is triggered.
- Lock TTL on `investigation_lock` field: 180 seconds.
- Email delivery: asynchronous, not on the critical path of incident update.

### 5.2 Distributed State

The system manages state across three locations:

| State | Location | Consistency requirement |
|---|---|---|
| Incident record | ServiceNow | Strong consistency for final write; read-your-writes for status check |
| Investigation lock | ServiceNow custom field `u_ai_investigation_lock` | Compare-and-swap semantics; prevents duplicate concurrent investigations |
| Historical incident knowledge | Elasticsearch | Eventual consistency acceptable; reads are informational, not authoritative |
| Deployment + commit data | GitHub | Authoritative external source; read-only; no local state |
| In-progress evidence | Orchestrator memory (transient) | Not persisted; lost on agent crash; re-investigation is idempotent |

### 5.3 Idempotency and Exactly-Once Semantics

The single most important distributed correctness property in this system is:

> **An incident must be enriched with a root-cause hypothesis at most once.**

This is enforced as follows:

**Write gate (ServiceNow):**
Before writing any AI fields to a ServiceNow incident, the `update_servicenow_incident`
tool must perform a conditional check:
- If `u_ai_root_cause_hypothesis` is already non-empty → skip write, return existing value.
- If empty → write atomically.

This implements **at-most-once write** semantics at the application layer. ServiceNow's
REST API does not natively provide compare-and-swap, so the tool implements an
optimistic read-then-write with a re-check. In practice, concurrent investigations of
the same incident are blocked by the investigation lock (see §5.5), making the write
gate a safety backstop rather than the primary mechanism.

**Idempotency key:**
Each investigation is keyed on the ServiceNow `sys_id`. Re-running the investigation
on the same `sys_id` after a partial failure must produce the same final state.

**Email notification:**
Email is **at-least-once**: the SMTP call may be retried on transient failure. The
notification content is deterministic given the same hypothesis, so duplicate delivery
is acceptable (the recipient sees the same message twice). This is a conscious trade-off:
availability of the notification is prioritised over exactly-once delivery.

### 5.4 Event-Driven Entry and Failure Detection

**Entry point:**
The investigation pipeline is triggered by an incident event. In the current T3
architecture, the entry is email-driven (`fetch_service_desk_emails`). For the root-cause
extension, the trigger can be:
- a ServiceNow Business Rule firing on incident creation (webhook / outbound REST message)
- a polling loop in the Orchestrator that checks for new incidents with
  `u_ai_investigation_lock = null`

**Failure detection:**
The Orchestrator detects downstream component failures through **timeout-based
failure detection**. This is a crash-recovery model: if a tool call does not return
within the configured timeout, the component is assumed to have failed for this
invocation. The investigation continues with whatever evidence is available (partial
synthesis). This is an **eventually perfect failure detector** in practice: it may
temporarily suspect a healthy component under high latency, but will not permanently
suspect a recovered one.

**Investigation lock as a heartbeat:**
The `u_ai_investigation_lock` field in ServiceNow doubles as a liveness indicator.
If a lock is held but the agent crashes before releasing it, the lock TTL ensures
eventual release. A monitoring process (or the Orchestrator itself on the next trigger)
can detect stale locks and re-trigger the investigation. This is analogous to a
**lease-based failure detection** pattern.

### 5.5 Leader Election and the Investigation Lock

When multiple invocations of the root-cause investigation are triggered for the same
incident (e.g. due to duplicate webhook delivery or a retry after a crash), only one
should proceed to the evidence-gathering and write phase.

**Algorithm (optimistic locking on ServiceNow):**

```
1. Read current value of u_ai_investigation_lock for incident_id.
2. If lock is set AND lock_timestamp is within TTL:
       → Abort: another agent is already investigating.
3. If lock is unset OR lock has expired:
       → Attempt write: set u_ai_investigation_lock = {agent_id, timestamp}.
4. Re-read u_ai_investigation_lock.
5. If the written value matches our agent_id:
       → We hold the lock. Proceed with investigation.
6. If the value was overwritten by another agent:
       → Abort: we lost the election.
7. On investigation completion (success or partial):
       → Clear u_ai_investigation_lock.
```

This is a **single-writer leader election** using ServiceNow as the shared register.
It is not a Byzantine-fault-tolerant protocol (we trust ServiceNow to be the authority),
but it is sufficient for crash-stop failures and duplicate event delivery.

**Why not a distributed consensus protocol (Paxos/Raft)?**
A full consensus protocol is not needed here because:
- There is only one authoritative state store (ServiceNow).
- The lock contention scenario is rare (triggered by duplicate events, not by a
  permanently competing cluster of agents).
- The cost of a false abort (letting the second agent wait and retry) is low.
- Implementing Paxos over ServiceNow's REST API would add complexity without
  meaningful correctness benefit.

### 5.6 Group Communication and Parallel Investigation

The Orchestrator coordinates a **logical group** of investigation sub-tasks:
- `query_recent_deployments` (GitHub)
- `query_commit_changes` (GitHub)
- `retrieve_resolution_notes` (Elasticsearch)

These sub-tasks are **logically independent** — they query different systems and do not
communicate with each other. The Orchestrator collects their results in a **scatter-gather
pattern** with a global timeout.

**Group membership:**
The group is static for a given investigation: the same three tools are always invoked.
Dynamic membership (e.g. adding a metric-anomaly tool when Datadog becomes available)
is handled at configuration time, not at runtime. This simplifies membership management:
there is no join/leave protocol required.

**Coordinator selection:**
The Orchestrator (Watsonx agent) is always the coordinator. There is no need for
coordinator election within a single investigation because:
- Each investigation is a single, bounded workflow.
- The coordinator is stateless between invocations.
- If the coordinator crashes, the investigation is re-triggered by the failure detection
  mechanism (stale lock expiry), not by a coordinator handover.

**Partial results and view synchrony:**
If one sub-task fails (e.g. GitHub is unavailable), the Orchestrator proceeds with
the results from the remaining sub-tasks. The hypothesis is marked as **incomplete**
with a `u_ai_evidence_gaps` field listing which sources were unavailable. This is
analogous to a **view change** in group communication: the system continues with a
reduced view of evidence rather than blocking on a full quorum.

Full **view synchrony** — the property that all agents in a group observe the same
sequence of view changes — is not required here because sub-tasks do not communicate
with each other and do not need a consistent view of group membership.

### 5.7 Consensus on the Final Hypothesis

**When is consensus needed?**
In the single-agent design (one Orchestrator per investigation), there is no competing
hypothesis from another agent — the LLM synthesis step produces one hypothesis
deterministically (given the same evidence). Consensus is therefore not required for
the base design.

**When would consensus become relevant?**
If the architecture is extended to run **multiple independent investigation agents in
parallel** (e.g. a deployment-focused agent and a code-quality-focused agent generating
separate hypotheses), a consensus step would be needed to select or merge the final
hypothesis before committing to ServiceNow.

A **lightweight agreement protocol** for this scenario:
1. Each agent produces a `(hypothesis, confidence_score)` tuple.
2. The Orchestrator collects all tuples within a timeout window.
3. Selection rule: take the hypothesis with the highest confidence score. If scores
   are within 5% of each other, merge evidence summaries and flag as "ambiguous".
4. Commit the selected hypothesis under the same idempotency rules as §5.3.

This is a **coordinator-based agreement** protocol (not Paxos/Raft) — adequate because
there is a trusted coordinator and failures are crash-stop.

### 5.8 Reliable Broadcast of Investigation Results

The notification to the L2/L3 engineer is a **reliable broadcast** to a group of
one or more recipients (the assigned team or on-call rotation).

**Properties required:**
- **Validity**: if the Orchestrator sends the notification, at least one recipient
  eventually receives it.
- **No duplication of action**: receiving the same notification twice should not cause
  the engineer to take duplicate action. This is enforced by including the incident
  number and a `u_ai_investigation_version` counter in the notification body.

**Implementation:**
Email via SMTP with retry-on-failure. The notification is generated after the ServiceNow
write is confirmed, so a retried notification always carries the committed hypothesis.

### 5.9 Replication and Fault Tolerance of the Knowledge Base

Elasticsearch is deployed as a **replicated cluster** (typically 1 primary + N replicas
per shard). From the perspective of this system:
- Reads (`retrieve_resolution_notes`) are served by any available replica.
- Writes (data ingestion via [`ingestion/`](ingestion/)) are primary-acknowledged.
- If the primary shard is unavailable, reads may return stale data from a replica.
  This is acceptable: historical incident data is informational context, not a
  transaction-critical source.

The system explicitly tolerates Elasticsearch unavailability: if all replicas are
unreachable, the investigation continues without historical context and the hypothesis
is marked as `u_ai_evidence_gaps: ["elasticsearch"]`.

### 5.10 Recovery After Partial Failures

**Stabilisation behaviour:**
The system is designed to **self-heal** after partial failures without manual
intervention.

| Failure | Detection | Recovery |
|---|---|---|
| GitHub API unavailable | Tool call timeout (30s) | Skip, mark gap, continue with remaining evidence |
| Elasticsearch unavailable | Tool call timeout (30s) | Skip, mark gap, continue |
| ServiceNow write fails (transient) | HTTP 5xx or timeout | Retry up to 3× with exponential backoff; if still failing, write to work_notes as fallback |
| ServiceNow write fails (conflict) | HTTP 409 or duplicate check | Read existing hypothesis, return without overwrite |
| Agent crash during investigation | Lock TTL expires (180s) | Next trigger re-acquires lock, re-runs investigation from scratch (idempotent) |
| Duplicate incident event | Investigation lock held | Second agent detects lock, aborts cleanly |
| Network partition (partial) | Timeout on affected tool | Same as tool-unavailable recovery |

**Exactly-once vs at-least-once trade-off:**
- ServiceNow incident write: **exactly-once** (enforced by lock + idempotency check)
- Email notification: **at-least-once** (retry on failure; idempotent content)
- Elasticsearch reads: **best-effort** (no retry required; failure is handled by gap flag)

---

## 6. Correctness Properties

### 6.1 Safety Properties

These properties must hold under all executions, including failure scenarios:

**S1 — Single-write hypothesis:**
A ServiceNow incident is enriched with a root-cause hypothesis at most once. If
`u_ai_root_cause_hypothesis` is already set, no subsequent investigation may overwrite
it without explicit human reset.

*Enforcement:* Investigation lock (§5.5) prevents concurrent writes. Idempotency check
(§5.3) prevents overwrite in case the lock check is bypassed.

**S2 — No conflicting concurrent commits:**
Two investigation agents cannot commit conflicting hypotheses to the same incident
simultaneously.

*Enforcement:* Single-writer lock; only the lock-holder may write.

**S3 — Evidence integrity:**
The hypothesis written to ServiceNow must be derivable from the evidence collected
during the investigation. An agent may not fabricate a hypothesis without any
supporting tool results.

*Enforcement:* The synthesise step in the Orchestrator receives the raw tool outputs
as input and must reference at least one piece of evidence. If all tools returned
empty results, the agent writes a `u_ai_investigation_status = "no_evidence_found"`
record rather than a hypothesis.

**S4 — No PII leakage:**
Evidence summaries and hypotheses written to ServiceNow and transmitted via email
must not contain PII.

*Enforcement:* [`guardrails/guardrails_output.py`](guardrails/guardrails_output.py)
scans all agent output before it reaches ServiceNow or the email channel.

### 6.2 Liveness Properties

These properties must eventually hold as long as the system is not permanently down:

**L1 — Every incident eventually reaches a terminal state:**
Either `u_ai_root_cause_hypothesis` is set (investigation completed), or
`u_ai_investigation_status` is set to `"no_evidence_found"` or `"investigation_failed"`.
An incident is never permanently stuck in the in-progress state.

*Enforcement:* Lock TTL ensures a crashed investigation is eventually retried.
The synthesis step always produces a terminal record even with zero evidence.

**L2 — Every investigation eventually produces output:**
Given that at least one tool returns a result within the timeout window, the
investigation always produces a hypothesis (possibly marked incomplete). If all
tools fail, it produces a `no_evidence_found` record. It never blocks indefinitely.

*Enforcement:* Global investigation timeout (120s) + per-tool timeout (30s).

**L3 — Temporary failures do not permanently block:**
If GitHub or Elasticsearch is temporarily unavailable, the investigation completes
with reduced evidence. When services recover, the next triggered investigation
(e.g. for a new incident) runs with full evidence. There is no permanent blockage.

*Enforcement:* Timeout-based failure detection + partial synthesis fallback.

---

## 7. Failure Scenarios

### 7.1 GitHub API Unavailable

| Aspect | Detail |
|---|---|
| Detection | `query_recent_deployments` or `query_commit_changes` times out after 30s |
| Recovery | Orchestrator marks `evidence_gaps = ["github"]`; proceeds to Elasticsearch query and synthesis without deployment evidence |
| Consistency impact | Hypothesis is weaker (no deployment correlation); labelled `incomplete` in `u_ai_evidence_gaps` |
| Availability impact | Investigation completes; incident is updated; engineer is notified with caveat |

### 7.2 Elasticsearch Unavailable

| Aspect | Detail |
|---|---|
| Detection | `retrieve_resolution_notes` times out after 30s |
| Recovery | Orchestrator marks `evidence_gaps = ["elasticsearch"]`; proceeds with GitHub evidence only |
| Consistency impact | No historical correlation; hypothesis lacks similar-incident context |
| Availability impact | Investigation completes with reduced evidence |

### 7.3 ServiceNow Temporarily Unreachable

| Aspect | Detail |
|---|---|
| Detection | `update_servicenow_incident` returns 5xx or connection error |
| Recovery | Retry up to 3× with exponential backoff (2s, 4s, 8s). If still failing, buffer the hypothesis result and log to orchestrator output. Incident remains in un-enriched state until the next trigger or manual re-run. |
| Consistency impact | Investigation result is computed but not yet committed; no partial write occurs |
| Availability impact | Incident is not updated; engineer notification is withheld until write succeeds |

### 7.4 Watsonx Agent Crashes Mid-Investigation

| Aspect | Detail |
|---|---|
| Detection | `u_ai_investigation_lock` remains set past TTL (180s) |
| Recovery | On next trigger (new incident event or polling), the stale lock is detected and cleared; investigation is re-run from scratch |
| Consistency impact | None — no write was committed before the crash |
| Availability impact | MTTR extended by up to one lock TTL period |

### 7.5 Duplicate Incident Events

| Aspect | Detail |
|---|---|
| Detection | Second invocation finds `u_ai_investigation_lock` already held or `u_ai_root_cause_hypothesis` already set |
| Recovery | Second invocation aborts cleanly without any write |
| Consistency impact | None — exactly-once write is preserved |
| Availability impact | None |

### 7.6 Network Partition (Partial)

| Aspect | Detail |
|---|---|
| Detection | Tool calls to partitioned service time out |
| Recovery | Same as service unavailability (§7.1–7.2): investigation continues with available sources |
| Consistency impact | Partition from ServiceNow is the highest-risk scenario: investigation completes but result cannot be committed. Result is buffered; retry loop re-attempts write when partition heals. |
| Availability impact | Investigation result is delayed until partition heals (for ServiceNow write). Evidence gathering degrades gracefully for read-only sources. |

---

## 8. Proposed Workflow

### 8.1 Current workflow in T3

[`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md):
`Email → Fetch → Extract Fields → Create Incident → Risk Assessment → Find Resolutions → Update Incident`

### 8.2 Extended workflow with distributed properties

```
Incident Event
(ServiceNow webhook / email intake)
      │
      ▼
[Acquire investigation lock on sys_id]
  ├─ Lock held by another agent ──► Abort (duplicate suppression)
  └─ Lock acquired ──────────────► Continue
      │
      ▼
[Parse incident context]
  service name · timeframe · severity · error keywords
      │
      ├──────────────────────────────────────────┐
      ▼                                          ▼
[query_recent_deployments]           [retrieve_resolution_notes]
  GitHub Actions API                  Elasticsearch hybrid search
  ± N hours of incident               similar past incidents
      │                                          │
      ▼                                          │
[query_commit_changes]                           │
  GitHub commits + compare API                   │
  diff for suspect SHA                           │
      │                                          │
      └──────────────┬───────────────────────────┘
                     ▼
      [Collect results with global timeout 120s]
       · Mark evidence_gaps for any timed-out source
                     │
                     ▼
      [Synthesize root-cause hypothesis]
       · Reference at least one piece of evidence
       · Assign confidence score (0–100)
       · Produce u_ai_recommended_next_step
                     │
                     ▼
      [Idempotency check on ServiceNow]
       · If hypothesis already set ──► skip write
       · If empty ──────────────────► write atomically
                     │
                     ▼
      [Update ServiceNow incident]
       u_ai_root_cause_hypothesis
       u_ai_evidence_summary
       u_ai_suspect_commit
       u_ai_suspect_deployment
       u_ai_confidence_score
       u_ai_recommended_next_step
       u_ai_evidence_gaps
                     │
                     ▼
      [Release investigation lock]
                     │
                     ▼
      [Reliable broadcast: notify L2/L3]
       Email with incident number + hypothesis brief
       · At-least-once delivery with retry
       · Idempotent content (same message on retry)
```

---

## 9. ServiceNow Incident Enrichment Fields

| Field | Type | Description |
|---|---|---|
| `u_ai_root_cause_hypothesis` | String | LLM-generated hypothesis text |
| `u_ai_evidence_summary` | Long text | Supporting evidence chain |
| `u_ai_suspect_commit` | String | GitHub commit SHA identified as suspect |
| `u_ai_suspect_deployment` | String | GitHub Actions run ID identified as suspect |
| `u_ai_confidence_score` | Integer (0–100) | Agent confidence in the hypothesis |
| `u_ai_recommended_next_step` | String | Suggested diagnostic or remediation action |
| `u_ai_evidence_gaps` | String (JSON array) | Sources that were unavailable during investigation |
| `u_ai_investigation_lock` | String | `{agent_id}:{timestamp}` — cleared on completion |
| `u_ai_investigation_status` | String | `in_progress`, `complete`, `incomplete`, `no_evidence_found`, `investigation_failed` |

---

## 10. Suggested New Tools

This project uses **Watsonx Orchestrate and GitHub only** for the first milestone.
Observability platforms (Datadog, Splunk, ELK) are deferred to a future phase.

### Minimum tool set

1. **`query_recent_deployments`**
   - GitHub Actions `/repos/{owner}/{repo}/actions/runs` API
   - Returns: list of workflow runs within ±N hours of the incident timestamp
   - Failure handling: returns `{"status": "unavailable", "reason": "timeout"}` on failure

2. **`query_commit_changes`**
   - GitHub Commits and Compare APIs
   - Returns: changed files, diff summary, author, timestamp for a suspect SHA
   - Failure handling: same as above

3. **`retrieve_resolution_notes`** — already exists in [`agents/risk_tools.py`](agents/risk_tools.py)
   - Reused as-is; accessible from the new root-cause agent

4. **`synthesize_root_cause`** — implemented as agent orchestration logic in YAML,
   not as a separate external tool call

### Optional future tools

- `query_observability_logs` *(when an observability platform is available)*
- `query_metric_anomalies` *(when an observability platform is available)*
- `query_change_records`
- `query_feature_flags`
- `query_kubernetes_events`
- `query_runbook_matches`

---

## 11. Development Strategy

### Phase 1 — Core investigation tools and agent

- Preserve the existing incident creation and risk-mapping workflow
- Add [`agents/investigation_tools.py`](agents/investigation_tools.py) with
  `query_recent_deployments` and `query_commit_changes`
- Create `agents/root_cause_agent.yml`
- Wire the orchestrator to call the root-cause agent after incident creation

### Phase 2 — Distributed correctness layer

- Implement investigation lock on ServiceNow (`u_ai_investigation_lock`)
- Implement idempotency check before every ServiceNow write
- Add `u_ai_evidence_gaps` field population
- Add per-tool timeout enforcement and partial-synthesis fallback

### Phase 3 — Observability and future roadmap

- Add observability integrations (Datadog, ELK, Splunk)
- Ticket-to-PR remediation
- Proactive problem management (incident clustering)
- Vendor outage correlation

---

## 12. Revised TODO List (GitHub + WXO only)

### What already exists — keep as-is

| File | Role |
|---|---|
| [`agents/incident_logging_agent.yml`](agents/incident_logging_agent.yml) | Email intake — no changes needed |
| [`agents/risk_mapping_agent.yml`](agents/risk_mapping_agent.yml) | Risk assessment — no changes needed |
| [`agents/risk_tools.py`](agents/risk_tools.py) | RAG tools — reused by new agent |
| [`ingestion/`](ingestion/) | Index scripts — extend with deployment data |
| [`data/resolution_notes/`](data/resolution_notes/) | Sample data — no changes needed |
| [`connections/elasticsearch-service-desk.yaml`](connections/elasticsearch-service-desk.yaml) | Keep |
| [`connections/watsonx-ai-service-desk.yaml`](connections/watsonx-ai-service-desk.yaml) | Keep |
| [`guardrails/`](guardrails/) | PII guardrails — keep |

### Phase 0 — Environment & Config

- [ ] Add to [`.env.example`](.env.example): `GITHUB_TOKEN`, `GITHUB_REPO_OWNER`, `GITHUB_REPO_NAME`
- [ ] Create `connections/github-service-desk.yaml`
- [ ] Register GitHub connection in Watsonx Orchestrate
- [ ] Add `PyGithub` (or `requests`) to [`requirements.txt`](requirements.txt)

### Phase 1 — New Tools

- [ ] Create `agents/investigation_tools.py`:
  - [ ] `query_recent_deployments` — GitHub Actions runs API, ±N hours window
  - [ ] `query_commit_changes` — GitHub commits + compare API, diff for suspect SHA
  - [ ] Both tools: return structured `{"status": "ok"|"unavailable", "data": ...}` — never raise on external failure
- [ ] Verify `retrieve_resolution_notes` from [`agents/risk_tools.py`](agents/risk_tools.py) is accessible from new agent

### Phase 2 — New Root-Cause Agent

- [ ] Create `agents/root_cause_agent.yml`:
  - Tools: `query_recent_deployments`, `query_commit_changes`, `retrieve_resolution_notes`, `get_servicenow_incident`, `update_servicenow_incident`
  - Instructions include: lock acquisition, gap detection, partial synthesis, idempotency check before write, lock release

### Phase 3 — ServiceNow Custom Fields

- [ ] Add fields per [`service_now_dev_instance_setup.md`](service_now_dev_instance_setup.md):
  `u_ai_root_cause_hypothesis`, `u_ai_evidence_summary`, `u_ai_suspect_commit`,
  `u_ai_suspect_deployment`, `u_ai_confidence_score`, `u_ai_recommended_next_step`,
  `u_ai_evidence_gaps`, `u_ai_investigation_lock`, `u_ai_investigation_status`
- [ ] Update `update_servicenow_incident` tool to write all new fields with idempotency check

### Phase 4 — Sample Data

- [ ] Create `data/deployments/sample_deployments.json` with realistic GitHub Actions records
- [ ] Create `ingestion/ingest_deployments.py` — index into `deployments_index`
- [ ] Update [`ingestion/create_indices.py`](ingestion/create_indices.py) to include `deployments_index`

### Phase 5 — Testing

- [ ] Extend [`test_connections.py`](test_connections.py) with GitHub connection test
- [ ] Test: lock acquisition and release under normal flow
- [ ] Test: duplicate event → second agent aborts without write
- [ ] Test: GitHub timeout → investigation completes with `evidence_gaps = ["github"]`
- [ ] Test: Elasticsearch timeout → investigation completes with `evidence_gaps = ["elasticsearch"]`
- [ ] Test: end-to-end scenario "Checkout 500s since 14:00" → enriched ServiceNow incident + notification

### Phase 6 — Import & Deployment

- [ ] Update [`import_to_orchestrate.sh`](import_to_orchestrate.sh) for new files
- [ ] Add `lab_exports/root_cause_agent/` once stable

### Phase 7 — Documentation

- [ ] Update [`README.md`](README.md) with new agent and tools
- [ ] Update [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md) with root-cause section and all new ServiceNow fields

### Net-new files: 4

| File | Purpose |
|---|---|
| `agents/investigation_tools.py` | `query_recent_deployments` + `query_commit_changes` |
| `agents/root_cause_agent.yml` | Orchestrating agent with distributed correctness instructions |
| `connections/github-service-desk.yaml` | GitHub connection definition |
| `data/deployments/sample_deployments.json` | Sample deployment data |

---

## 13. Distributed Systems Concept Map

This section explicitly maps the project to distributed systems concepts.

| Concept | Where it appears in this project |
|---|---|
| **Event-driven programming** | Investigation triggered by incident creation event (ServiceNow webhook or email intake); async entry point decouples trigger from processing |
| **Failure models** | Crash-stop / crash-recover assumed for all components; Byzantine failures not considered |
| **Timing models** | Partial synchrony: bounded timeouts enforced per-tool (30s) and globally (120s); no assumption of synchronous delivery |
| **Failure detection** | Timeout-based (eventually perfect detector); stale investigation lock as a secondary heartbeat mechanism |
| **Service health monitoring** | `u_ai_investigation_status` and `u_ai_evidence_gaps` fields in ServiceNow provide a persistent health record of each investigation; lock TTL monitors agent liveness |
| **Leader election** | Investigation lock on ServiceNow `sys_id` implements single-writer election; lock-holder is the sole coordinator for that incident |
| **Reliable broadcast** | Email notification uses at-least-once retry with idempotent message content; validity guaranteed by retry loop |
| **Group communication** | Three investigation sub-tasks (GitHub deploys, GitHub commits, Elasticsearch) form a logical group coordinated by the Orchestrator in a scatter-gather pattern |
| **View synchrony** | Not enforced between sub-tasks (they are independent); partial view (reduced evidence set) is handled by the gap flag rather than blocking on full-group response |
| **Consensus / agreement** | Not required in single-agent design; lightweight coordinator-based agreement protocol specified for the future multi-agent extension (§5.7) |
| **Shared state management** | ServiceNow incident record is the shared state; all agents read and write through the same REST API; lock controls concurrent access |
| **Replication** | Elasticsearch cluster provides replicated read access to historical incident knowledge; reads tolerate replica staleness |
| **Fault tolerance** | Graceful degradation: investigation completes with reduced evidence when any source is unavailable; no single point of failure blocks incident update |
| **Recovery after partial failures** | Lock TTL ensures re-triggering after agent crash; tool-level timeout ensures partial synthesis after source failure; retry-with-backoff for ServiceNow write failures |
| **Distributed coordination** | Investigation lock on ServiceNow coordinates concurrent agents; scatter-gather coordinates parallel tool calls; email channel is coordinated post-write |
| **Idempotency** | Every ServiceNow write is preceded by a read-check; re-running the investigation on the same `sys_id` always produces the same committed state |
| **Exactly-once vs at-least-once** | ServiceNow write: exactly-once (lock + idempotency check); email: at-least-once (retry with idempotent content) |
| **Stabilization / self-healing** | Stale lock expiry enables self-healing after agent crash; partial synthesis ensures the system never blocks permanently on source unavailability |

---

## 14. Demo Narrative

### Elevator pitch

> When a checkout service goes down at 2pm on a Friday, an L2 engineer usually spends
> 45 minutes opening GitHub, deployment history, and ServiceNow to figure out what
> changed. This solution does that in 90 seconds. It reads the incident, finds the
> deployment that happened in the suspect window, inspects the related code changes,
> cross-references similar past incidents, and writes a structured root-cause brief
> directly into the ticket — exactly once, even if the trigger fires twice. The engineer
> reviews and acts instead of spending their first 45 minutes investigating.

### Why the distributed design makes this story stronger

The demo does not just show an agent calling APIs. It demonstrates:
- **Fault tolerance**: the investigation completes even if GitHub is slow.
- **Exactly-once guarantees**: the incident is not updated twice even under retries.
- **Self-healing**: a crashed investigation re-runs automatically without human intervention.

These are properties that production operations teams care about and that no generic
chatbot can credibly claim.

---

## 15. Risks and Limitations

| Risk | Mitigation |
|---|---|
| ServiceNow does not provide native atomic compare-and-swap | Optimistic locking (read-write-verify) is a best-effort workaround; under very high concurrency, two agents could both pass the lock check in the same millisecond. Mitigation: add a unique constraint on `u_ai_investigation_lock` at the ServiceNow table level. |
| Lock TTL too short under slow GitHub/Elasticsearch responses | Set TTL generously (≥180s). Make investigation timeout (120s) strictly shorter than TTL. |
| LLM produces non-deterministic hypotheses across retries | The synthesised hypothesis may differ slightly between a first run and a re-run. This is acceptable: the first committed hypothesis is preserved by the idempotency check (S1). |
| Email SMTP is a single point of failure for notification | Notification failure does not block incident update. Implement a dead-letter queue or secondary notification channel (Slack/Teams webhook) in a future phase. |
| GitHub rate limiting (5000 req/hr for authenticated tokens) | For high-volume incident environments, use a service account token and implement exponential backoff with jitter on rate-limit responses (HTTP 429). |
| Elasticsearch replica lag may return stale resolution notes | Acceptable for this use case: historical incident data is informational context. Staleness window is typically sub-second in a healthy cluster. |

---

## 16. Bottom Line

This project evolves from its current email-to-incident and risk-assessment workflow
toward **autonomous root-cause investigation with fault-tolerant, distributed correctness
guarantees**. It becomes a demonstrably more sophisticated system than API orchestration:
it reasons about partial failures, enforces exactly-once write semantics, coordinates
concurrent agents through a leader election mechanism, and self-heals after crashes.

The strongest path forward:
1. Keep the current T3 architecture as the foundation.
2. Add GitHub-first root-cause investigation tools with structured failure responses.
3. Layer distributed correctness properties (lock, idempotency, gap detection) onto the
   investigation workflow.
4. Position the solution around MTTR reduction, fault tolerance, and L2/L3 acceleration.

**Observability integrations (Datadog, ELK, Splunk) are deferred to a future phase.**
The GitHub deployment + commit correlation story, backed by a formally-reasoned
distributed design, is already a strong and differentiated first milestone.
