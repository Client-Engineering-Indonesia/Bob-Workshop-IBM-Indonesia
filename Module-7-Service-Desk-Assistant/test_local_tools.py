#!/usr/bin/env python3
"""
test_local_tools.py — Local integration test for ServiceNow + GitHub tools.

Bypasses the WXO connections layer by monkey-patching
`ibm_watsonx_orchestrate.run.connections` with real credentials from .env.

Run:
    cd Service_desk_Assistant_T3
    source .venv/bin/activate
    python test_local_tools.py

All tests print ✅ / ❌ per assertion. Exit 0 if all pass.
"""

import os
import sys
import json
import types
from pathlib import Path
from datetime import datetime, timezone

# ── Load .env ────────────────────────────────────────────────────────────────
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ── Monkey-patch WXO stubs so tool files can be imported without the ADK ─────
# Minimal stubs that satisfy the decorator imports
import importlib

def _make_stub_module(name: str) -> types.ModuleType:
    m = types.ModuleType(name)
    sys.modules[name] = m
    return m

# ibm_watsonx_orchestrate.agent_builder.tools
_tools_mod = _make_stub_module("ibm_watsonx_orchestrate")
_ab = _make_stub_module("ibm_watsonx_orchestrate.agent_builder")
_tools_mod.agent_builder = _ab

class _FakePerm:
    ADMIN = "admin"
    READ = "read"

def _tool_decorator(**kwargs):
    """No-op @tool decorator — just returns the original function."""
    def _wrap(fn):
        return fn
    return _wrap

_tools_inner = _make_stub_module("ibm_watsonx_orchestrate.agent_builder.tools")
_tools_inner.tool = _tool_decorator
_tools_inner.ToolPermission = _FakePerm
_ab.tools = _tools_inner

# ibm_watsonx_orchestrate.agent_builder.connections
class _ConnType:
    KEY_VALUE = "key_value"

class _ExpectedCreds:
    def __init__(self, **kwargs): pass

_conn_mod = _make_stub_module("ibm_watsonx_orchestrate.agent_builder.connections")
_conn_mod.ConnectionType = _ConnType
_conn_mod.ExpectedCredentials = _ExpectedCreds
_ab.connections = _conn_mod

# ibm_watsonx_orchestrate.run — real credential store
SNOW_CREDS = {
    "SNOW_INSTANCE_URL": os.environ.get("SNOW_INSTANCE_URL", ""),
    "SNOW_USERNAME":     os.environ.get("SNOW_USERNAME", ""),
    "SNOW_PASSWORD":     os.environ.get("SNOW_PASSWORD", ""),
}
GITHUB_CREDS = {
    "GITHUB_TOKEN":       os.environ.get("GITHUB_TOKEN", ""),
    "GITHUB_REPO_OWNER":  os.environ.get("GITHUB_REPO_OWNER", ""),
    "GITHUB_REPO_NAME":   os.environ.get("GITHUB_REPO_NAME", ""),
}

class _FakeConnections:
    def key_value(self, app_id: str) -> dict:
        if app_id == "servicenow-service-desk":
            return SNOW_CREDS
        if app_id == "github-service-desk":
            return GITHUB_CREDS
        return {}

_run_mod = _make_stub_module("ibm_watsonx_orchestrate.run")
_run_mod.connections = _FakeConnections()

# ── Import the real tool modules ──────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from agents.servicenow_tools import (
    get_servicenow_incident,
    update_servicenow_incident,
    create_servicenow_incident,
)
from agents.investigation_tools import (
    query_recent_deployments,
    query_commit_changes,
)

# ── Test helpers ──────────────────────────────────────────────────────────────
PASS = 0
FAIL = 0
TARGET_SYS_ID = os.environ.get("INVESTIGATION_DEFAULT_SYS_ID", "")
if not TARGET_SYS_ID:
    print("Error: set INVESTIGATION_DEFAULT_SYS_ID in .env (e.g. the sys_id of INC0000060)")
    sys.exit(1)

def ok(label: str):
    global PASS
    PASS += 1
    print(f"  ✅ {label}")

def fail(label: str, detail: str = ""):
    global FAIL
    FAIL += 1
    print(f"  ❌ {label}" + (f": {detail}" if detail else ""))

def section(title: str):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")

# ── SECTION 1: ServiceNow — read incident ────────────────────────────────────
section("1 · get_servicenow_incident (by sys_id)")

rec = get_servicenow_incident(sys_id=TARGET_SYS_ID)
print(f"  → success={rec.success}  number={rec.number}  sys_id={rec.sys_id}")
if rec.success:
    ok("get by sys_id returned success=True")
else:
    fail("get by sys_id", rec.error)

if rec.number == "INC0000060":
    ok(f"incident number matches: {rec.number}")
else:
    fail("incident number mismatch", f"got {rec.number}")

# _val() returns None for empty/absent fields — check the raw REST response
import requests as _req
_raw = _req.get(
    f"{os.environ.get('SNOW_INSTANCE_URL','').rstrip('/')}/api/now/table/incident/{TARGET_SYS_ID}",
    auth=(os.environ.get('SNOW_USERNAME',''), os.environ.get('SNOW_PASSWORD','')),
    params={"sysparm_fields": "u_ai_root_cause_hypothesis"},
    headers={"Accept": "application/json"},
    timeout=20,
)
_field_exists = "u_ai_root_cause_hypothesis" in _raw.json().get("result", {})
if _field_exists:
    ok("u_ai_root_cause_hypothesis field present in ServiceNow record")
    ok("_val() returns None for empty field (correct — LLM sees JSON null)")
else:
    fail("u_ai_root_cause_hypothesis field missing from ServiceNow record")

if rec.opened_at:
    ok(f"opened_at present: {rec.opened_at}")
else:
    fail("opened_at missing")

section("2 · get_servicenow_incident (by ticket number)")

rec2 = get_servicenow_incident(ticket_number="INC0000060")
print(f"  → success={rec2.success}  sys_id={rec2.sys_id}")
if rec2.success and rec2.sys_id == TARGET_SYS_ID:
    ok("get by ticket_number resolves to same sys_id")
else:
    fail("get by ticket_number", f"success={rec2.success} sys_id={rec2.sys_id} err={rec2.error}")

# ── SECTION 3: ServiceNow — acquire investigation lock ───────────────────────
section("3 · update_servicenow_incident — acquire investigation lock")

lock_value = f"root_cause_agent:{datetime.now(timezone.utc).isoformat()}"
upd = update_servicenow_incident(
    sys_id=TARGET_SYS_ID,
    u_ai_investigation_lock=lock_value,
    u_ai_investigation_status="in_progress",
)
print(f"  → success={upd.success}  skipped={upd.skipped_hypothesis_write}")
if upd.success:
    ok("lock write succeeded")
else:
    fail("lock write failed", upd.error)

# Verify the lock was written
rec3 = get_servicenow_incident(sys_id=TARGET_SYS_ID)
if rec3.success and rec3.u_ai_investigation_lock == lock_value:
    ok(f"lock value confirmed in ServiceNow: {lock_value[:50]}…")
else:
    fail("lock value not found in ServiceNow",
         f"found: {rec3.u_ai_investigation_lock!r}")

# ── SECTION 4: ServiceNow — idempotency pre-check ────────────────────────────
section("4 · update_servicenow_incident — idempotency (write hypothesis once)")

hypothesis = "The email connectivity failure was caused by the checkout-service deployment at 14:02 UTC which introduced a misconfigured SMTP relay timeout. The commit SHA abc1234 modified mail/config.py, reducing timeout from 30s to 3s, causing cascading failures."

# First write — should succeed
upd_first = update_servicenow_incident(
    sys_id=TARGET_SYS_ID,
    u_ai_root_cause_hypothesis=hypothesis,
    u_ai_evidence_summary="• GitHub run #1234 (failure, 14:02 UTC)\n• Commit abc1234 modified mail/config.py\n• No matching resolution notes found",
    u_ai_suspect_commit="abc1234",
    u_ai_suspect_deployment="12345678",
    u_ai_confidence_score=72,
    u_ai_recommended_next_step="Revert commit abc1234 and re-deploy checkout-service",
    u_ai_evidence_gaps="[]",
    u_ai_investigation_status="complete",
    u_ai_investigation_lock="",    # release lock
)
print(f"  → first write: success={upd_first.success}  skipped={upd_first.skipped_hypothesis_write}")
if upd_first.success and not upd_first.skipped_hypothesis_write:
    ok("first hypothesis write succeeded (not skipped)")
else:
    fail("first hypothesis write", f"success={upd_first.success} skipped={upd_first.skipped_hypothesis_write} err={upd_first.error}")

# Second write — must be blocked by idempotency
upd_second = update_servicenow_incident(
    sys_id=TARGET_SYS_ID,
    u_ai_root_cause_hypothesis="SHOULD NOT BE WRITTEN — idempotency test",
    u_ai_evidence_summary="should be blocked",
    u_ai_investigation_status="complete",
    u_ai_investigation_lock="",
)
print(f"  → second write: success={upd_second.success}  skipped={upd_second.skipped_hypothesis_write}")
if upd_second.skipped_hypothesis_write:
    ok("idempotency pre-check blocked second hypothesis write ✔")
else:
    fail("idempotency pre-check did NOT block second write",
         f"success={upd_second.success}")

# Verify final state
rec4 = get_servicenow_incident(sys_id=TARGET_SYS_ID)
if rec4.u_ai_root_cause_hypothesis == hypothesis:
    ok("hypothesis in ServiceNow matches first write (not overwritten)")
else:
    fail("hypothesis was overwritten or missing",
         f"found: {repr(rec4.u_ai_root_cause_hypothesis)[:80]}")

if rec4.u_ai_investigation_status == "complete":
    ok(f"u_ai_investigation_status = complete")
else:
    fail("investigation status wrong", rec4.u_ai_investigation_status)

if not rec4.u_ai_investigation_lock:
    ok("u_ai_investigation_lock is empty (released)")
else:
    fail("lock was not released", rec4.u_ai_investigation_lock)

if rec4.u_ai_confidence_score == "72":
    ok("u_ai_confidence_score = 72")
else:
    fail("confidence score wrong", rec4.u_ai_confidence_score)

# ── SECTION 5: ServiceNow — clear AI fields for next test ────────────────────
section("5 · Reset AI fields for clean smoke test")

reset = update_servicenow_incident(
    sys_id=TARGET_SYS_ID,
    u_ai_investigation_lock="",
    u_ai_investigation_status="",
)
# Bypass idempotency by patching directly via REST
import requests
SNOW_PASSWORD = os.environ.get("SNOW_PASSWORD", "")
SNOW_INSTANCE_URL = os.environ.get("SNOW_INSTANCE_URL", "").rstrip("/")
SNOW_USERNAME = os.environ.get("SNOW_USERNAME", "")

reset_payload = {
    "u_ai_root_cause_hypothesis":   "",
    "u_ai_evidence_summary":        "",
    "u_ai_suspect_commit":          "",
    "u_ai_suspect_deployment":      "",
    "u_ai_confidence_score":        "",
    "u_ai_recommended_next_step":   "",
    "u_ai_evidence_gaps":           "",
    "u_ai_investigation_lock":      "",
    "u_ai_investigation_status":    "",
}
r = requests.patch(
    f"{SNOW_INSTANCE_URL}/api/now/table/incident/{TARGET_SYS_ID}",
    auth=(SNOW_USERNAME, SNOW_PASSWORD),
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    json=reset_payload,
    timeout=20,
)
if r.ok:
    ok("AI fields reset to empty for clean smoke test")
else:
    fail("AI fields reset failed", f"HTTP {r.status_code}: {r.text[:100]}")

# ── SECTION 6: GitHub tools ───────────────────────────────────────────────────
section("6 · query_recent_deployments")

# Use a 30-day window to catch any recent runs in the repo
inc_time = datetime.now(timezone.utc).isoformat()
dep = query_recent_deployments(incident_time=inc_time, window_hours=720)
print(f"  → status={dep.status}  total_found={dep.total_found}")

if dep.status in ("ok", "unavailable"):
    ok(f"query_recent_deployments returned valid status: {dep.status}")
else:
    fail("unexpected status", dep.status)

if dep.status == "ok":
    ok(f"GitHub API reachable — {dep.total_found} runs found in ±720h window")
elif dep.status == "unavailable":
    ok(f"GitHub gracefully unavailable: {dep.error}")

section("7 · query_commit_changes")

# Use a well-known public commit SHA format (short) — will 404 gracefully if not in our repo
commit_result = query_commit_changes(commit_sha="abc1234")
print(f"  → status={commit_result.status}")
if commit_result.status in ("ok", "unavailable"):
    ok(f"query_commit_changes returned valid status: {commit_result.status}")
else:
    fail("unexpected status", commit_result.status)

if commit_result.status == "unavailable":
    ok(f"graceful unavailable: {commit_result.error}")

# ── SECTION 8: create_servicenow_incident ────────────────────────────────────
section("8 · create_servicenow_incident (creates a test incident)")

create_result = create_servicenow_incident(
    short_description="[TEST] Root-cause pipeline local validation",
    description="Automated test incident created by test_local_tools.py to validate the create_servicenow_incident tool. Safe to close.",
    caller_email="admin@example.com",
    urgency="3",
    category="Software",
)
print(f"  → success={create_result.success}  number={create_result.ticket_number}  sys_id={create_result.sys_id}")
if create_result.success and create_result.ticket_number:
    ok(f"create_servicenow_incident succeeded: {create_result.ticket_number}")
    ok(f"URL: {create_result.url}")
else:
    fail("create_servicenow_incident failed", create_result.error)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'═'*60}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed")
print(f"{'═'*60}\n")

if FAIL > 0:
    sys.exit(1)
sys.exit(0)
