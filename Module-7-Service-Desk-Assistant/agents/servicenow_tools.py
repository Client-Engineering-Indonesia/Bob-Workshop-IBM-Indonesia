# agents/servicenow_tools.py
#
# ServiceNow ITSM tools for Watsonx Orchestrate.
#
# Tools:
#   create_servicenow_incident  — create a new incident record
#   get_servicenow_incident     — read an incident by ticket number OR sys_id
#   update_servicenow_incident  — update an incident; writes all root-cause AI fields
#                                 with idempotency pre-check on u_ai_root_cause_hypothesis
#
# All tools use the "servicenow-service-desk" Watsonx Orchestrate connection which
# supplies SNOW_INSTANCE_URL, SNOW_USERNAME, and SNOW_PASSWORD at runtime.

from typing import Optional
from datetime import datetime, timezone

import requests

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.run import connections
from pydantic.dataclasses import dataclass


SNOW_APP_ID = "servicenow-service-desk"
SNOW_TIMEOUT = 25  # seconds


# ── Dataclasses ───────────────────────────────────────────────────

@dataclass
class IncidentCreateResponse:
    """Response from create_servicenow_incident."""
    success: bool
    ticket_number: Optional[str] = None
    sys_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


@dataclass
class IncidentRecord:
    """A ServiceNow incident record (subset of fields)."""
    success: bool
    sys_id: Optional[str] = None
    number: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    urgency: Optional[str] = None
    category: Optional[str] = None
    caller_id: Optional[str] = None
    opened_at: Optional[str] = None
    assigned_to: Optional[str] = None
    work_notes: Optional[str] = None
    # Root-cause AI fields ──────────────────────────────────────
    u_ai_root_cause_hypothesis: Optional[str] = None
    u_ai_evidence_summary: Optional[str] = None
    u_ai_suspect_commit: Optional[str] = None
    u_ai_suspect_deployment: Optional[str] = None
    u_ai_confidence_score: Optional[str] = None
    u_ai_recommended_next_step: Optional[str] = None
    u_ai_evidence_gaps: Optional[str] = None
    u_ai_investigation_lock: Optional[str] = None
    u_ai_investigation_status: Optional[str] = None
    # ────────────────────────────────────────────────────────────
    url: Optional[str] = None
    error: Optional[str] = None


@dataclass
class IncidentUpdateResponse:
    """Response from update_servicenow_incident."""
    success: bool
    sys_id: Optional[str] = None
    number: Optional[str] = None
    skipped_hypothesis_write: bool = False   # True when idempotency check blocked the write
    error: Optional[str] = None


# ── HTTP helpers ──────────────────────────────────────────────────

def _snow_client(snow_creds: dict) -> tuple[Optional[str], Optional[requests.Session], Optional[str]]:
    """
    Build a requests.Session pre-configured for ServiceNow basic auth.
    Returns (base_url, session, error).
    """
    url      = snow_creds.get("SNOW_INSTANCE_URL", "").rstrip("/")
    username = snow_creds.get("SNOW_USERNAME", "")
    password = snow_creds.get("SNOW_PASSWORD", "")

    if not url or not username or not password:
        return None, None, "Missing ServiceNow credentials: SNOW_INSTANCE_URL, SNOW_USERNAME, SNOW_PASSWORD"

    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    return url, session, None


def _table_url(base_url: str, table: str, sys_id: Optional[str] = None) -> str:
    url = f"{base_url}/api/now/table/{table}"
    if sys_id:
        url += f"/{sys_id}"
    return url


# ── Tools ─────────────────────────────────────────────────────────

@tool(
    name="create_servicenow_incident",
    description=(
        "Creates a new ServiceNow incident record. Use this after extracting "
        "structured fields from a service desk email or user request."
    ),
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        ExpectedCredentials(app_id=SNOW_APP_ID, type=ConnectionType.KEY_VALUE),
    ],
)
def create_servicenow_incident(
    short_description: str,
    description: str,
    caller_email: str,
    urgency: str = "3",
    category: str = "Software",
    risk_category: Optional[str] = None,
    risk_severity: Optional[str] = None,
    resolution_recommendation: Optional[str] = None,
) -> IncidentCreateResponse:
    """
    Creates a ServiceNow incident.

    Args:
        short_description:         One-line summary (max 100 chars).
        description:               Full incident details.
        caller_email:              Reporting user's email.
        urgency:                   "1" Critical, "2" High, "3" Medium, "4" Low.
        category:                  Hardware | Software | Network | Access | Security | Other.
        risk_category:             Optional AI-mapped risk category.
        risk_severity:             Optional AI risk severity.
        resolution_recommendation: Optional AI resolution recommendation.
    """
    snow_creds = connections.key_value(SNOW_APP_ID)
    base_url, session, error = _snow_client(snow_creds)
    if error:
        return IncidentCreateResponse(success=False, error=error)

    payload: dict = {
        "short_description": short_description[:100],
        "description": description,
        "caller_id": caller_email,
        "urgency": urgency,
        "category": category,
        "contact_type": "email",
    }
    if risk_category:
        payload["u_ai_risk_category"] = risk_category
    if risk_severity:
        payload["u_ai_risk_severity"] = risk_severity
    if resolution_recommendation:
        payload["u_ai_resolution_recommendation"] = resolution_recommendation

    try:
        resp = session.post(
            _table_url(base_url, "incident"),
            json=payload,
            timeout=SNOW_TIMEOUT,
        )
    except requests.Timeout:
        return IncidentCreateResponse(success=False, error="ServiceNow API timed out")
    except requests.RequestException as exc:
        return IncidentCreateResponse(success=False, error=f"ServiceNow API error: {exc}")

    if not resp.ok:
        return IncidentCreateResponse(
            success=False,
            error=f"ServiceNow returned HTTP {resp.status_code}: {resp.text[:300]}"
        )

    result = resp.json().get("result", {})
    sys_id = result.get("sys_id", "")
    number = result.get("number", "")
    instance_url = snow_creds.get("SNOW_INSTANCE_URL", "").rstrip("/")

    return IncidentCreateResponse(
        success=True,
        ticket_number=number,
        sys_id=sys_id,
        url=f"{instance_url}/nav_to.do?uri=incident.do?sys_id={sys_id}",
    )


@tool(
    name="get_servicenow_incident",
    description=(
        "Retrieves a ServiceNow incident record. Accepts either a ticket number "
        "(e.g. INC0012345) or a sys_id. Returns all standard fields plus all "
        "u_ai_* root-cause investigation fields."
    ),
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        ExpectedCredentials(app_id=SNOW_APP_ID, type=ConnectionType.KEY_VALUE),
    ],
)
def get_servicenow_incident(
    ticket_number: Optional[str] = None,
    sys_id: Optional[str] = None,
) -> IncidentRecord:
    """
    Retrieves an incident by ticket number (e.g. INC0012345) or sys_id.
    At least one of ticket_number or sys_id must be provided.

    Args:
        ticket_number: ServiceNow incident number, e.g. "INC0012345".
        sys_id:        ServiceNow sys_id (32-char hex string).
    """
    if not ticket_number and not sys_id:
        return IncidentRecord(success=False, error="Provide ticket_number or sys_id")

    snow_creds = connections.key_value(SNOW_APP_ID)
    base_url, session, error = _snow_client(snow_creds)
    if error:
        return IncidentRecord(success=False, error=error)

    # Determine URL + params
    ai_fields = ",".join([
        "u_ai_root_cause_hypothesis",
        "u_ai_evidence_summary",
        "u_ai_suspect_commit",
        "u_ai_suspect_deployment",
        "u_ai_confidence_score",
        "u_ai_recommended_next_step",
        "u_ai_evidence_gaps",
        "u_ai_investigation_lock",
        "u_ai_investigation_status",
    ])
    base_fields = "sys_id,number,short_description,description,state,urgency,category,caller_id,opened_at,assigned_to,work_notes"
    sysparm_fields = f"{base_fields},{ai_fields}"

    try:
        if sys_id:
            resp = session.get(
                _table_url(base_url, "incident", sys_id),
                params={"sysparm_fields": sysparm_fields},
                timeout=SNOW_TIMEOUT,
            )
        else:
            resp = session.get(
                _table_url(base_url, "incident"),
                params={
                    "sysparm_query": f"number={ticket_number}",
                    "sysparm_fields": sysparm_fields,
                    "sysparm_limit": "1",
                },
                timeout=SNOW_TIMEOUT,
            )
    except requests.Timeout:
        return IncidentRecord(success=False, error="ServiceNow API timed out")
    except requests.RequestException as exc:
        return IncidentRecord(success=False, error=f"ServiceNow API error: {exc}")

    if resp.status_code == 404:
        return IncidentRecord(success=False, error=f"Incident not found: {ticket_number or sys_id}")
    if not resp.ok:
        return IncidentRecord(
            success=False,
            error=f"ServiceNow returned HTTP {resp.status_code}: {resp.text[:300]}"
        )

    data = resp.json()
    # list endpoint wraps in {"result": [...]}; record endpoint wraps in {"result": {...}}
    result = data.get("result")
    if isinstance(result, list):
        if not result:
            return IncidentRecord(success=False, error=f"Incident not found: {ticket_number}")
        result = result[0]

    def _val(field: str) -> Optional[str]:
        """Extract plain value from a ServiceNow field (may be str or {value:...} dict).
        Returns None for absent keys AND for empty-string values, so the LLM
        sees JSON null for all empty fields and can unambiguously distinguish
        'field is empty/not set' from 'field has a value'.
        """
        if field not in result:
            return None
        v = result[field]
        if isinstance(v, dict):
            v = v.get("value") or v.get("display_value") or ""
        # Normalise: empty string → None so JSON serialises as null
        return v if v else None

    record_sys_id = _val("sys_id")
    number = _val("number")
    instance_url = snow_creds.get("SNOW_INSTANCE_URL", "").rstrip("/")

    return IncidentRecord(
        success=True,
        sys_id=record_sys_id,
        number=number,
        short_description=_val("short_description"),
        description=_val("description"),
        state=_val("state"),
        urgency=_val("urgency"),
        category=_val("category"),
        caller_id=_val("caller_id"),
        opened_at=_val("opened_at"),
        assigned_to=_val("assigned_to"),
        work_notes=_val("work_notes"),
        u_ai_root_cause_hypothesis=_val("u_ai_root_cause_hypothesis"),
        u_ai_evidence_summary=_val("u_ai_evidence_summary"),
        u_ai_suspect_commit=_val("u_ai_suspect_commit"),
        u_ai_suspect_deployment=_val("u_ai_suspect_deployment"),
        u_ai_confidence_score=_val("u_ai_confidence_score"),
        u_ai_recommended_next_step=_val("u_ai_recommended_next_step"),
        u_ai_evidence_gaps=_val("u_ai_evidence_gaps"),
        u_ai_investigation_lock=_val("u_ai_investigation_lock"),
        u_ai_investigation_status=_val("u_ai_investigation_status"),
        url=f"{instance_url}/nav_to.do?uri=incident.do?sys_id={record_sys_id}",
    )


@tool(
    name="update_servicenow_incident",
    description=(
        "Updates a ServiceNow incident. Supports standard fields (work_notes, state) "
        "and all nine u_ai_* root-cause investigation fields. "
        "Enforces idempotency: if u_ai_root_cause_hypothesis is already set on the "
        "record, the hypothesis write is silently skipped and skipped_hypothesis_write "
        "is returned as True."
    ),
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        ExpectedCredentials(app_id=SNOW_APP_ID, type=ConnectionType.KEY_VALUE),
    ],
)
def update_servicenow_incident(
    sys_id: str,
    # Standard fields
    work_notes: Optional[str] = None,
    state: Optional[str] = None,
    resolution_notes: Optional[str] = None,
    # Root-cause AI fields
    u_ai_root_cause_hypothesis: Optional[str] = None,
    u_ai_evidence_summary: Optional[str] = None,
    u_ai_suspect_commit: Optional[str] = None,
    u_ai_suspect_deployment: Optional[str] = None,
    u_ai_confidence_score: Optional[int] = None,
    u_ai_recommended_next_step: Optional[str] = None,
    u_ai_evidence_gaps: Optional[str] = None,
    u_ai_investigation_lock: Optional[str] = None,
    u_ai_investigation_status: Optional[str] = None,
) -> IncidentUpdateResponse:
    """
    Updates a ServiceNow incident by sys_id.

    Idempotency rule for u_ai_root_cause_hypothesis:
      Before writing, this tool reads the current value of u_ai_root_cause_hypothesis.
      If it is already non-empty, the hypothesis (and related AI fields) are NOT
      overwritten. skipped_hypothesis_write = True is returned so the caller knows
      a prior investigation already committed a hypothesis.

    The investigation lock (u_ai_investigation_lock) and status
    (u_ai_investigation_status) are always written regardless of the hypothesis
    check, so the lock can always be acquired and released.

    Args:
        sys_id:                       ServiceNow sys_id of the incident to update.
        work_notes:                   Notes to append to the work notes field.
        state:                        Incident state: "1" New, "2" In Progress,
                                      "6" Resolved, "7" Closed.
        resolution_notes:             Resolution description.
        u_ai_root_cause_hypothesis:   LLM root-cause hypothesis (write-once).
        u_ai_evidence_summary:        Bullet-list evidence chain.
        u_ai_suspect_commit:          GitHub commit SHA flagged as suspect.
        u_ai_suspect_deployment:      GitHub Actions run ID flagged as suspect.
        u_ai_confidence_score:        Integer 0–100 agent confidence.
        u_ai_recommended_next_step:   Concrete next action for the L2/L3 engineer.
        u_ai_evidence_gaps:           JSON array of unavailable source names.
        u_ai_investigation_lock:      "{agent_id}:{timestamp}" or "" to release.
        u_ai_investigation_status:    in_progress | complete | incomplete |
                                      no_evidence_found | investigation_failed.
    """
    if not sys_id:
        return IncidentUpdateResponse(success=False, error="sys_id is required")

    snow_creds = connections.key_value(SNOW_APP_ID)
    base_url, session, error = _snow_client(snow_creds)
    if error:
        return IncidentUpdateResponse(success=False, error=error)

    # ── Idempotency pre-check ────────────────────────────────────────
    # Only run the pre-check when the caller is attempting to write a hypothesis.
    skipped_hypothesis_write = False
    hypothesis_fields_requested = u_ai_root_cause_hypothesis is not None

    if hypothesis_fields_requested:
        try:
            check_resp = session.get(
                _table_url(base_url, "incident", sys_id),
                params={"sysparm_fields": "sys_id,number,u_ai_root_cause_hypothesis"},
                timeout=SNOW_TIMEOUT,
            )
        except requests.RequestException as exc:
            return IncidentUpdateResponse(
                success=False,
                sys_id=sys_id,
                error=f"Pre-check read failed: {exc}"
            )

        if not check_resp.ok:
            return IncidentUpdateResponse(
                success=False,
                sys_id=sys_id,
                error=f"Pre-check returned HTTP {check_resp.status_code}: {check_resp.text[:200]}"
            )

        current = check_resp.json().get("result", {})
        existing_hypothesis = current.get("u_ai_root_cause_hypothesis")
        if isinstance(existing_hypothesis, dict):
            existing_hypothesis = existing_hypothesis.get("value", "")

        if existing_hypothesis:
            # Hypothesis already committed — skip all AI content fields.
            # Still allow lock and status fields through (they must always be writable).
            skipped_hypothesis_write = True
            u_ai_root_cause_hypothesis    = None
            u_ai_evidence_summary         = None
            u_ai_suspect_commit           = None
            u_ai_suspect_deployment       = None
            u_ai_confidence_score         = None
            u_ai_recommended_next_step    = None
            u_ai_evidence_gaps            = None
            # u_ai_investigation_lock and u_ai_investigation_status pass through

    # ── Build patch payload ──────────────────────────────────────────
    payload: dict = {}

    if work_notes is not None:
        payload["work_notes"] = work_notes
    if state is not None:
        payload["state"] = state
    if resolution_notes is not None:
        payload["close_notes"] = resolution_notes

    # AI fields — only include keys the caller set (and weren't cleared by idempotency)
    ai_fields = {
        "u_ai_root_cause_hypothesis":  u_ai_root_cause_hypothesis,
        "u_ai_evidence_summary":       u_ai_evidence_summary,
        "u_ai_suspect_commit":         u_ai_suspect_commit,
        "u_ai_suspect_deployment":     u_ai_suspect_deployment,
        "u_ai_confidence_score":       str(u_ai_confidence_score) if u_ai_confidence_score is not None else None,
        "u_ai_recommended_next_step":  u_ai_recommended_next_step,
        "u_ai_evidence_gaps":          u_ai_evidence_gaps,
        "u_ai_investigation_lock":     u_ai_investigation_lock,
        "u_ai_investigation_status":   u_ai_investigation_status,
    }
    for field, value in ai_fields.items():
        if value is not None:
            payload[field] = value

    if not payload:
        # Nothing to write — treat as success (all fields either skipped or not provided)
        return IncidentUpdateResponse(
            success=True,
            sys_id=sys_id,
            skipped_hypothesis_write=skipped_hypothesis_write,
        )

    # ── PATCH ────────────────────────────────────────────────────────
    try:
        resp = session.patch(
            _table_url(base_url, "incident", sys_id),
            json=payload,
            timeout=SNOW_TIMEOUT,
        )
    except requests.Timeout:
        return IncidentUpdateResponse(success=False, sys_id=sys_id, error="ServiceNow API timed out")
    except requests.RequestException as exc:
        return IncidentUpdateResponse(success=False, sys_id=sys_id, error=f"ServiceNow API error: {exc}")

    if not resp.ok:
        return IncidentUpdateResponse(
            success=False,
            sys_id=sys_id,
            error=f"ServiceNow returned HTTP {resp.status_code}: {resp.text[:300]}"
        )

    result = resp.json().get("result", {})
    return IncidentUpdateResponse(
        success=True,
        sys_id=result.get("sys_id", sys_id),
        number=result.get("number"),
        skipped_hypothesis_write=skipped_hypothesis_write,
    )


# Made with Bob
