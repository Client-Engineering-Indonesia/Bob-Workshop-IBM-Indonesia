# ServiceNow Custom Fields — Root-Cause Investigation

This guide walks through adding the 9 custom AI fields required by the
root-cause investigation agent to the ServiceNow Incident table.

---

## Overview

The root-cause agent writes structured investigation results back to ServiceNow.
These fields must exist on the `incident` table before the agent can write to them.

| Field | Type | Max Length | Purpose |
|---|---|---|---|
| `u_ai_root_cause_hypothesis` | String | 1000 | LLM hypothesis — write-once |
| `u_ai_evidence_summary` | Long text | 4000 | Bullet-list evidence chain |
| `u_ai_suspect_commit` | String | 100 | GitHub commit SHA flagged as suspect |
| `u_ai_suspect_deployment` | String | 100 | GitHub Actions run ID flagged as suspect |
| `u_ai_confidence_score` | Integer | — | Agent confidence 0–100 |
| `u_ai_recommended_next_step` | String | 500 | Concrete next action for L2/L3 engineer |
| `u_ai_evidence_gaps` | String | 500 | JSON array of unavailable source names |
| `u_ai_investigation_lock` | String | 200 | `{agent_id}:{timestamp}` leader-election register |
| `u_ai_investigation_status` | String | 50 | `in_progress \| complete \| incomplete \| no_evidence_found \| investigation_failed` |

---

## Step 1 — Open the Incident Table Dictionary

1. Log in to your ServiceNow developer instance as **admin**.
2. In the filter navigator, type:

   ```
   sys_dictionary.list
   ```

3. In the **Table** filter column, type `incident` and press Enter.
   You will see the existing field definitions for the Incident table.

---

## Step 2 — Add Each Custom Field

Repeat the following sub-steps for every field in the table above.

### 2.1 Open the New Record Form

Click **New** (top-left of the dictionary list).

### 2.2 Fill in the field form

Use the values from the table below for each field.

---

### Field 1 — `u_ai_root_cause_hypothesis`

| Setting | Value |
|---|---|
| Table | `incident` |
| Type | `String` |
| Column name | `u_ai_root_cause_hypothesis` |
| Column label | `AI Root Cause Hypothesis` |
| Max length | `1000` |
| Active | ✅ checked |
| Read only | ❌ unchecked |
| Mandatory | ❌ unchecked |
| Default value | *(leave blank)* |

Click **Submit**.

---

### Field 2 — `u_ai_evidence_summary`

| Setting | Value |
|---|---|
| Table | `incident` |
| Type | `String` (choose **Large** or set max length ≥ 4000) |
| Column name | `u_ai_evidence_summary` |
| Column label | `AI Evidence Summary` |
| Max length | `4000` |
| Active | ✅ checked |

Click **Submit**.

---

### Field 3 — `u_ai_suspect_commit`

| Setting | Value |
|---|---|
| Table | `incident` |
| Type | `String` |
| Column name | `u_ai_suspect_commit` |
| Column label | `AI Suspect Commit` |
| Max length | `100` |
| Active | ✅ checked |

Click **Submit**.

---

### Field 4 — `u_ai_suspect_deployment`

| Setting | Value |
|---|---|
| Table | `incident` |
| Type | `String` |
| Column name | `u_ai_suspect_deployment` |
| Column label | `AI Suspect Deployment` |
| Max length | `100` |
| Active | ✅ checked |

Click **Submit**.

---

### Field 5 — `u_ai_confidence_score`

| Setting | Value |
|---|---|
| Table | `incident` |
| Type | `Integer` |
| Column name | `u_ai_confidence_score` |
| Column label | `AI Confidence Score` |
| Min value | `0` |
| Max value | `100` |
| Active | ✅ checked |

Click **Submit**.

---

### Field 6 — `u_ai_recommended_next_step`

| Setting | Value |
|---|---|
| Table | `incident` |
| Type | `String` |
| Column name | `u_ai_recommended_next_step` |
| Column label | `AI Recommended Next Step` |
| Max length | `500` |
| Active | ✅ checked |

Click **Submit**.

---

### Field 7 — `u_ai_evidence_gaps`

| Setting | Value |
|---|---|
| Table | `incident` |
| Type | `String` |
| Column name | `u_ai_evidence_gaps` |
| Column label | `AI Evidence Gaps` |
| Max length | `500` |
| Active | ✅ checked |

> Stores a JSON array, e.g. `["github"]` or `[]`. Treated as a plain string.

Click **Submit**.

---

### Field 8 — `u_ai_investigation_lock`

| Setting | Value |
|---|---|
| Table | `incident` |
| Type | `String` |
| Column name | `u_ai_investigation_lock` |
| Column label | `AI Investigation Lock` |
| Max length | `200` |
| Active | ✅ checked |

> Stores `{agent_id}:{ISO-timestamp}`, e.g. `root_cause_agent:2025-07-15T14:02:33Z`.
> Cleared (set to empty string) when the investigation completes.

Click **Submit**.

---

### Field 9 — `u_ai_investigation_status`

| Setting | Value |
|---|---|
| Table | `incident` |
| Type | `String` |
| Column name | `u_ai_investigation_status` |
| Column label | `AI Investigation Status` |
| Max length | `50` |
| Active | ✅ checked |

> Valid values: `in_progress`, `complete`, `incomplete`, `no_evidence_found`, `investigation_failed`.

Click **Submit**.

---

## Step 3 — Add an AI Fields Section to the Incident Form

Surfacing the fields in the Incident form lets L2/L3 engineers review the
hypothesis without opening the record in JSON or via the API.

1. Open any existing incident record.
2. Click the **gear icon** (⚙️) → **Form Layout** (or right-click the form header → **Configure → Form Layout**).
3. In the **Form Layout** editor:
   - Click **New Section**.
   - Name it: `AI Root-Cause Investigation`.
4. Drag the following fields into the new section (in order):

   ```
   AI Investigation Status         (u_ai_investigation_status)
   AI Root Cause Hypothesis        (u_ai_root_cause_hypothesis)
   AI Confidence Score             (u_ai_confidence_score)
   AI Recommended Next Step        (u_ai_recommended_next_step)
   AI Suspect Commit               (u_ai_suspect_commit)
   AI Suspect Deployment           (u_ai_suspect_deployment)
   AI Evidence Summary             (u_ai_evidence_summary)
   AI Evidence Gaps                (u_ai_evidence_gaps)
   AI Investigation Lock           (u_ai_investigation_lock)
   ```

5. Click **Save**.

---

## Step 4 — Verify via REST API

After adding all fields, confirm they are writable via the Table API:

```bash
# Replace with your instance URL and credentials
SNOW_URL="https://devXXXXX.service-now.com"
SNOW_USER="admin"
SNOW_PASS="your-password"
INCIDENT_SYS_ID="your-test-incident-sys-id"

curl -s -X PATCH \
  "${SNOW_URL}/api/now/table/incident/${INCIDENT_SYS_ID}" \
  -u "${SNOW_USER}:${SNOW_PASS}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "u_ai_investigation_status": "in_progress",
    "u_ai_investigation_lock": "test_agent:2025-07-15T14:00:00Z"
  }' | python3 -m json.tool
```

Expected response includes:
```json
{
  "result": {
    "u_ai_investigation_status": "in_progress",
    "u_ai_investigation_lock": "test_agent:2025-07-15T14:00:00Z"
  }
}
```

If you see `"Invalid field"` errors, the field was not saved correctly — repeat Step 2 for that field.

---

## Step 5 — Add SNOW credentials to `.env`

Make sure your `.env` file contains:

```ini
SNOW_INSTANCE_URL=https://devXXXXX.service-now.com
SNOW_USERNAME=svc_servicedesk_ai
SNOW_PASSWORD=your-service-account-password
```

Then re-run the connection credential set:

```bash
orchestrate connections set-credentials -a servicenow-service-desk \
  --env draft \
  -e "SNOW_INSTANCE_URL=${SNOW_INSTANCE_URL}" \
  -e "SNOW_USERNAME=${SNOW_USERNAME}" \
  -e "SNOW_PASSWORD=${SNOW_PASSWORD}"
```

---

## Step 6 — Import the ServiceNow tools

```bash
orchestrate tools import \
  -k python \
  -f agents/servicenow_tools.py \
  -r requirements_tools.txt \
  -a servicenow-service-desk
```

Or run the full import script which handles this automatically:

```bash
bash import_to_orchestrate.sh
```

---

## Idempotency Guarantee

The `update_servicenow_incident` tool in `agents/servicenow_tools.py` enforces
**write-once** semantics on `u_ai_root_cause_hypothesis`:

1. Before any write that includes `u_ai_root_cause_hypothesis`, the tool
   performs a **GET** on the incident to read the current value.
2. If `u_ai_root_cause_hypothesis` is **already non-empty**, all hypothesis-related
   fields (`u_ai_root_cause_hypothesis`, `u_ai_evidence_summary`,
   `u_ai_suspect_commit`, `u_ai_suspect_deployment`, `u_ai_confidence_score`,
   `u_ai_recommended_next_step`, `u_ai_evidence_gaps`) are **dropped from the
   PATCH payload**.
3. `u_ai_investigation_lock` and `u_ai_investigation_status` are **always written**
   regardless, so the lock can always be acquired and released.
4. The response includes `skipped_hypothesis_write: true` so the calling agent
   knows a prior investigation already committed the hypothesis.

This ensures an incident is enriched with a root-cause hypothesis **at most once**,
even if the investigation pipeline is triggered multiple times for the same incident.
