#!/usr/bin/env python3
"""
verify_servicenow_fields.py

Verifies all 9 custom AI fields exist and are writable via the REST API.
Reads credentials from .env — no Watsonx Orchestrate needed.

Usage:
    cd Service_desk_Assistant_T3
    python3 verify_servicenow_fields.py
"""
import os, sys, requests
from dotenv import load_dotenv

load_dotenv()

URL  = os.getenv("SNOW_INSTANCE_URL", "").rstrip("/")
USER = os.getenv("SNOW_USERNAME", "")
PASS = os.getenv("SNOW_PASSWORD", "")

FIELDS = [
    "u_ai_root_cause_hypothesis",
    "u_ai_evidence_summary",
    "u_ai_suspect_commit",
    "u_ai_suspect_deployment",
    "u_ai_confidence_score",
    "u_ai_recommended_next_step",
    "u_ai_evidence_gaps",
    "u_ai_investigation_lock",
    "u_ai_investigation_status",
]

PAYLOAD = {
    "u_ai_investigation_status":  "in_progress",
    "u_ai_investigation_lock":    "verify:2025-01-01T00:00:00Z",
    "u_ai_confidence_score":      "42",
    "u_ai_root_cause_hypothesis": "Verification write — safe to delete",
    "u_ai_evidence_summary":      "Verification write — safe to delete",
    "u_ai_suspect_commit":        "abc1234",
    "u_ai_suspect_deployment":    "987654321",
    "u_ai_recommended_next_step": "Verification write — safe to delete",
    "u_ai_evidence_gaps":         "[]",
}

if not URL or not USER or not PASS:
    print("❌  Missing .env values — set SNOW_INSTANCE_URL, SNOW_USERNAME, SNOW_PASSWORD")
    sys.exit(1)

print(f"\n{'='*56}\n  ServiceNow Field Verification\n  {URL}\n{'='*56}")

s = requests.Session()
s.auth    = (USER, PASS)
s.headers = {"Content-Type": "application/json", "Accept": "application/json"}

# Step 1 — create a scratch incident
print("\n→ Creating a temporary test incident ...")
r = s.post(f"{URL}/api/now/table/incident",
    json={"short_description": "[BOB VERIFY] delete me",
          "urgency": "4", "category": "Software"}, timeout=20)
if not r.ok:
    print(f"❌  Could not create incident — HTTP {r.status_code}: {r.text[:300]}")
    sys.exit(1)

# Detect hibernation: ServiceNow returns HTTP 200 with an HTML page when asleep
if not r.text.strip() or r.text.strip().startswith("<"):
    print("❌  Instance is HIBERNATING — ServiceNow returned an HTML page instead of JSON.")
    print(f"   Wake it up: open {URL} in your browser,")
    print(f"   wait for the login page to load fully, then re-run this script.")
    sys.exit(1)

res    = r.json()["result"]
sys_id = res["sys_id"]
number = res["number"]
print(f"   Created {number}  (sys_id: {sys_id})")

# Step 2 — write all 9 AI fields
print("\n→ Writing all 9 AI fields ...")
r = s.patch(f"{URL}/api/now/table/incident/{sys_id}", json=PAYLOAD, timeout=20)
if not r.ok:
    print(f"❌  PATCH failed — HTTP {r.status_code}: {r.text[:300]}")
    sys.exit(1)
written = r.json()["result"]

# Step 3 — verify each field returned
print()
ok, fail_list = 0, []
for field in FIELDS:
    val = written.get(field)
    if isinstance(val, dict): val = val.get("value", "")
    if val not in (None, ""):
        print(f"  ✅  {field}")
        ok += 1
    else:
        print(f"  ❌  {field}  ← not found in response")
        fail_list.append(field)

# Step 4 — clear test values
s.patch(f"{URL}/api/now/table/incident/{sys_id}",
        json={f: "" for f in FIELDS}, timeout=20)
print(f"\n→ Test values cleared on {number}")

# Summary
print(f"\n{'='*56}\n  Result: {ok}/9 fields verified\n{'='*56}")
if fail_list:
    print("\n⚠️  Missing fields — re-run setup_servicenow_fields.js for:")
    for f in fail_list: print(f"    • {f}")
    sys.exit(1)
else:
    print(f"\n🎉  All 9 fields present and writable.")
    print(f"   {URL}/nav_to.do?uri=incident.do?sys_id={sys_id}\n")
