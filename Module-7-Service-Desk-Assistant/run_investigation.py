#!/usr/bin/env python3
"""
run_investigation.py — Hybrid root-cause investigation runner.

Architecture:
  Steps 1, 2, 4 — Python (direct tool calls, deterministic)
  Step 5         — WXO agent (LLM synthesis from gathered evidence)
  Steps 6, 7     — Python (deterministic ServiceNow write + verify)

This bypasses the LLM token-budget issue where multi-step tool chaining
fails in a single agent response turn.

Usage:
    cd Service_desk_Assistant_T3
    python3 run_investigation.py [sys_id]

Default sys_id: set INVESTIGATION_DEFAULT_SYS_ID in .env, or pass as CLI arg
"""

import os
import sys
import json
import time
import types
import textwrap
from pathlib import Path
from datetime import datetime, timezone

# ── Load .env ────────────────────────────────────────────────────────────────
env_path = Path(__file__).parent / ".env"
for line in env_path.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

# Default sys_id comes from .env (INVESTIGATION_DEFAULT_SYS_ID) or CLI arg
_DEFAULT_SYS_ID = os.environ.get("INVESTIGATION_DEFAULT_SYS_ID", "")
SYS_ID = sys.argv[1] if len(sys.argv) > 1 else _DEFAULT_SYS_ID
if not SYS_ID:
    print("Error: provide a sys_id as an argument or set INVESTIGATION_DEFAULT_SYS_ID in .env")
    sys.exit(1)

# ── WXO SDK — import BEFORE stubs so real SDK is available ───────────────────
try:
    from ibm_watsonx_orchestrate.client.chat.run_client import RunClient as _RunClient
    from ibm_watsonx_orchestrate.client.utils import instantiate_client as _instantiate_client
    _WXO_RunClient = _RunClient
    _WXO_instantiate = _instantiate_client
    WXO_AVAILABLE = True
except Exception:
    _WXO_RunClient = None
    _WXO_instantiate = None
    WXO_AVAILABLE = False

# ── Monkey-patch WXO stubs so tool files import without ADK ──────────────────
def _make_stub(name):
    m = types.ModuleType(name)
    sys.modules[name] = m
    return m

_wxo = _make_stub("ibm_watsonx_orchestrate")
_ab  = _make_stub("ibm_watsonx_orchestrate.agent_builder")
_wxo.agent_builder = _ab

class _FakePerm:
    ADMIN = "admin"

def _tool(**kw):
    return lambda fn: fn

_tmod = _make_stub("ibm_watsonx_orchestrate.agent_builder.tools")
_tmod.tool = _tool
_tmod.ToolPermission = _FakePerm
_ab.tools = _tmod

class _CT:
    KEY_VALUE = "kv"

class _EC:
    def __init__(self, **kw): pass

_cmod = _make_stub("ibm_watsonx_orchestrate.agent_builder.connections")
_cmod.ConnectionType = _CT
_cmod.ExpectedCredentials = _EC
_ab.connections = _cmod

SNOW_CREDS = {
    "SNOW_INSTANCE_URL": os.environ.get("SNOW_INSTANCE_URL", ""),
    "SNOW_USERNAME":     os.environ.get("SNOW_USERNAME", ""),
    "SNOW_PASSWORD":     os.environ.get("SNOW_PASSWORD", ""),
}
GH_CREDS = {
    "GITHUB_TOKEN":      os.environ.get("GITHUB_TOKEN", ""),
    "GITHUB_REPO_OWNER": os.environ.get("GITHUB_REPO_OWNER", ""),
    "GITHUB_REPO_NAME":  os.environ.get("GITHUB_REPO_NAME", ""),
}

class _FakeConn:
    def key_value(self, app_id):
        if "servicenow" in app_id:
            return SNOW_CREDS
        if "github" in app_id:
            return GH_CREDS
        return {}

_run = _make_stub("ibm_watsonx_orchestrate.run")
_run.connections = _FakeConn()

# ── Import real tool functions ────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from agents.servicenow_tools import get_servicenow_incident, update_servicenow_incident
from agents.investigation_tools import query_recent_deployments, query_commit_changes

# ── Aliases for SDK functions (captured before stubs override modules) ────────
RunClient = _WXO_RunClient
instantiate_client = _WXO_instantiate


SYNTHESIS_AGENT_ID = os.environ.get("SYNTHESIS_AGENT_ID", "")


# ── Helpers ───────────────────────────────────────────────────────────────────
def sep(title=""):
    print(f"\n{'═'*60}")
    if title:
        print(f"  {title}")
        print(f"{'─'*60}")


def extract_text(run_status: dict) -> str:
    result = run_status.get("result", {})
    if isinstance(result, dict):
        content = result.get("data", {}).get("message", {}).get("content", [])
        if isinstance(content, list):
            parts = [item["text"] for item in content if isinstance(item, dict) and item.get("text")]
            if parts:
                return "\n".join(parts)
    return ""


def call_synthesis_agent(evidence_prompt: str) -> str:
    """Ask root_cause_agent to synthesise a hypothesis from the gathered evidence."""
    if not WXO_AVAILABLE:
        return "WXO SDK not available — synthesis skipped."
    try:
        run_client = instantiate_client(RunClient)
        run_response = run_client.create_run(
            message=evidence_prompt,
            agent_id=SYNTHESIS_AGENT_ID,
        )
        run_id = run_response.get("run_id") or run_response.get("id")
        deadline = time.time() + 60
        while time.time() < deadline:
            rs = run_client.get_run_status(run_id)
            if rs.get("status", "").lower() in ("completed", "failed", "error"):
                return extract_text(rs)
            time.sleep(3)
        return "Synthesis timed out."
    except Exception as e:
        return f"Synthesis error: {e}"


# ── Main investigation ────────────────────────────────────────────────────────
def main():
    sep("🚀 ROOT-CAUSE INVESTIGATION")
    print(f"  Incident sys_id: {SYS_ID}")
    print(f"  Time:            {datetime.now(timezone.utc).isoformat()}")

    # ── STEP 1: Read incident ──────────────────────────────────────────────
    sep("STEP 1 — Read incident")
    inc = get_servicenow_incident(sys_id=SYS_ID)
    if not inc.success:
        print(f"  ❌ Cannot read incident: {inc.error}")
        sys.exit(1)
    print(f"  ✅ {inc.number} — {inc.short_description}")
    print(f"     Opened: {inc.opened_at}  Urgency: {inc.urgency}")

    # ── STEP 2: Acquire lock ───────────────────────────────────────────────
    sep("STEP 2 — Acquire investigation lock")
    lock_upd = update_servicenow_incident(
        sys_id=SYS_ID,
        u_ai_investigation_lock="root_cause_agent:LOCKED",
        u_ai_investigation_status="in_progress",
    )
    if not lock_upd.success:
        print(f"  ❌ Lock write failed: {lock_upd.error}")
        sys.exit(1)
    print("  ✅ Lock acquired: root_cause_agent:LOCKED")

    # ── STEP 3: Idempotency check (tool enforces it in Step 6) ────────────
    if inc.u_ai_root_cause_hypothesis:
        sep("STEP 3 — Already investigated")
        print(f"  ✅ Hypothesis already committed: {inc.u_ai_root_cause_hypothesis[:80]}")
        update_servicenow_incident(sys_id=SYS_ID, u_ai_investigation_lock="",
                                   u_ai_investigation_status="complete")
        sys.exit(0)
    print("  ✅ Hypothesis is empty — proceeding with investigation")

    # ── STEP 4: Gather evidence ────────────────────────────────────────────
    sep("STEP 4 — Gather evidence")
    evidence_gaps = []

    # 4a. GitHub deployments
    dep = query_recent_deployments(
        incident_time=inc.opened_at or datetime.now(timezone.utc).isoformat(),
        window_hours=2,
    )
    if dep.status == "ok":
        print(f"  ✅ Deployments: {dep.total_found} runs in ±2h window")
    else:
        print(f"  ⚠️  Deployments unavailable: {dep.error}")
        evidence_gaps.append("github_deployments")

    # 4b. Commit changes (if any deployment found)
    suspect_sha = ""
    commit_info = None
    if dep.status == "ok" and dep.runs:
        # find most recent failed or completed run
        for run in sorted(dep.runs, key=lambda r: r.updated_at, reverse=True):
            if run.conclusion in ("failure", "success", "completed") or run.status == "completed":
                suspect_sha = run.head_sha
                break
        if suspect_sha:
            commit_info = query_commit_changes(commit_sha=suspect_sha)
            if commit_info.status == "ok":
                print(f"  ✅ Commit {suspect_sha[:8]}: {commit_info.total_additions}+ {commit_info.total_deletions}-")
            else:
                print(f"  ⚠️  Commit query unavailable: {commit_info.error}")
                evidence_gaps.append("github_commit")
        else:
            print("  ⚠️  No suspect SHA found in deployment runs")
            evidence_gaps.append("no_suspect_sha")
    elif dep.status == "ok":
        print("  ⚠️  No deployment runs found in time window")
        evidence_gaps.append("no_suspect_sha")

    # 4c. Resolution notes (call directly without ES/watsonx — they're unavailable)
    # We skip retrieve_resolution_notes since ES credentials are placeholders
    resolution_context = ""
    print("  ⚠️  Resolution notes: ES not configured (placeholder creds) — skipping")
    evidence_gaps.append("elasticsearch")

    print(f"\n  Evidence gaps: {evidence_gaps or 'none'}")

    # ── STEP 5: Synthesise hypothesis (via LLM) ────────────────────────────
    sep("STEP 5 — Synthesise hypothesis (LLM)")

    evidence_prompt = f"""You are performing root-cause analysis on a ServiceNow incident.

INCIDENT:
  Number: {inc.number}
  Description: {inc.short_description}
  Details: {inc.description or 'No additional details'}
  Opened: {inc.opened_at}
  Urgency: {inc.urgency}

EVIDENCE GATHERED:
  GitHub deployments in ±2h window: {dep.total_found if dep.status == 'ok' else 'unavailable'}
  Suspect commit SHA: {suspect_sha or 'none found'}
  Commit details: {f"{commit_info.total_additions} additions, {commit_info.total_deletions} deletions in {len(commit_info.changed_files)} files" if commit_info and commit_info.status == 'ok' else 'unavailable'}
  Resolution notes: not available (Elasticsearch not configured)
  Evidence gaps: {json.dumps(evidence_gaps)}

Based on the evidence above, provide a root-cause hypothesis.
Respond with ONLY a JSON object with these exact keys (no markdown, no explanation):
{{
  "hypothesis": "2-4 sentence root-cause hypothesis",
  "evidence_summary": "bullet-point list of evidence used",
  "confidence_score": <integer 0-100>,
  "recommended_next_step": "one concrete next action for the engineer",
  "investigation_status": "complete" or "incomplete" or "no_evidence_found"
}}"""

    print("  → Calling synthesis agent...")
    synthesis_response = call_synthesis_agent(evidence_prompt)
    print(f"  Raw synthesis: {synthesis_response[:200]}...")

    # Parse synthesis response
    hypothesis = "No hypothesis available — synthesis failed or timed out."
    evidence_summary = "Evidence gathering completed."
    confidence_score = 10
    recommended_next_step = "Review incident details manually."
    investigation_status = "incomplete"

    try:
        # Try to extract JSON from the response
        text = synthesis_response.strip()
        # find JSON block
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            hypothesis            = data.get("hypothesis", hypothesis)
            evidence_summary      = data.get("evidence_summary", evidence_summary)
            confidence_score      = int(data.get("confidence_score", confidence_score))
            recommended_next_step = data.get("recommended_next_step", recommended_next_step)
            investigation_status  = data.get("investigation_status", investigation_status)
            print("  ✅ Hypothesis parsed from LLM response")
        else:
            # LLM returned plain text — use it as-is for hypothesis
            if len(text) > 20:
                hypothesis = text[:500]
                print("  ⚠️  LLM returned plain text (not JSON) — using as hypothesis")
    except Exception as e:
        print(f"  ⚠️  Synthesis parse error: {e} — using defaults")

    sep("🧠 HYPOTHESIS")
    print(f"  {hypothesis}")
    print(f"\n  Confidence: {confidence_score}/100")
    print(f"  Next step:  {recommended_next_step}")
    print(f"  Status:     {investigation_status}")
    print(f"  Gaps:       {evidence_gaps}")

    # ── STEP 6: Write to ServiceNow ────────────────────────────────────────
    sep("STEP 6 — Write to ServiceNow")
    write_upd = update_servicenow_incident(
        sys_id=SYS_ID,
        u_ai_root_cause_hypothesis=hypothesis,
        u_ai_evidence_summary=evidence_summary,
        u_ai_suspect_commit=suspect_sha or "",
        u_ai_suspect_deployment=str(dep.runs[0].run_id) if dep.status == "ok" and dep.runs else "",
        u_ai_confidence_score=confidence_score,
        u_ai_recommended_next_step=recommended_next_step,
        u_ai_evidence_gaps=json.dumps(evidence_gaps),
        u_ai_investigation_status=investigation_status,
        u_ai_investigation_lock="",   # release lock
    )
    if write_upd.success and not write_upd.skipped_hypothesis_write:
        print(f"  ✅ ServiceNow updated: {write_upd.number}")
    elif write_upd.skipped_hypothesis_write:
        print("  ⚠️  Hypothesis already committed (idempotency) — lock released")
    else:
        print(f"  ❌ ServiceNow write failed: {write_upd.error}")
        sys.exit(1)

    # ── STEP 7: Verify ────────────────────────────────────────────────────
    sep("STEP 7 — Verify ServiceNow fields")
    verify = get_servicenow_incident(sys_id=SYS_ID)
    written = 0
    ai_fields = [
        ("u_ai_root_cause_hypothesis",  verify.u_ai_root_cause_hypothesis),
        ("u_ai_evidence_summary",       verify.u_ai_evidence_summary),
        ("u_ai_confidence_score",       verify.u_ai_confidence_score),
        ("u_ai_recommended_next_step",  verify.u_ai_recommended_next_step),
        ("u_ai_evidence_gaps",          verify.u_ai_evidence_gaps),
        ("u_ai_investigation_status",   verify.u_ai_investigation_status),
        ("u_ai_investigation_lock",     verify.u_ai_investigation_lock),
    ]
    for name, val in ai_fields:
        if val:
            written += 1
            short = val[:65] + "…" if len(val) > 65 else val
            print(f"  ✅ {name}: {short}")
        else:
            print(f"  ⬜ {name}: (empty)")

    sep("✅ INVESTIGATION COMPLETE" if written >= 5 else "⚠️  INVESTIGATION PARTIAL")
    print(f"  {written}/7 AI fields confirmed written to ServiceNow")
    print(f"  Incident URL: {verify.url}")
    print()
    sys.exit(0 if written >= 5 else 1)


if __name__ == "__main__":
    main()
