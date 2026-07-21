# agents/investigation_tools.py
#
# Root-Cause Investigation tools — GitHub data sources.
#
# Tools:
#   query_recent_deployments  — GitHub Actions runs within ±N hours of an incident
#   query_commit_changes      — Changed files + diff summary for a suspect commit SHA
#
# Both tools follow the project's graceful-degradation contract:
#   return {"status": "ok"|"unavailable", "data": ...}
#   NEVER raise on external failure.

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta

import requests

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.run import connections
from pydantic.dataclasses import dataclass


GITHUB_APP_ID = "github-service-desk"

GITHUB_API_BASE = "https://api.github.com"
TOOL_TIMEOUT_SECONDS = 28  # stays under the 30 s per-tool platform timeout


# ── Dataclasses ───────────────────────────────────────────────────

@dataclass
class WorkflowRun:
    """A single GitHub Actions workflow run."""
    run_id: int
    name: str
    status: str                    # queued | in_progress | completed
    conclusion: Optional[str]      # success | failure | cancelled | None
    html_url: str
    head_sha: str
    head_branch: str
    created_at: str
    updated_at: str
    triggering_actor: Optional[str] = None


@dataclass
class DeploymentQueryResponse:
    """Response envelope for query_recent_deployments."""
    status: str                    # "ok" | "unavailable"
    incident_time: Optional[str]
    window_hours: int
    runs: List[WorkflowRun]
    total_found: int
    error: Optional[str] = None


@dataclass
class ChangedFile:
    """A single file changed in a commit."""
    filename: str
    status: str                    # added | modified | removed | renamed
    additions: int
    deletions: int
    patch_summary: Optional[str]   # first 300 chars of the raw diff patch


@dataclass
class CommitChangesResponse:
    """Response envelope for query_commit_changes."""
    status: str                    # "ok" | "unavailable"
    sha: str
    author: Optional[str]
    author_email: Optional[str]
    committed_at: Optional[str]
    message: Optional[str]
    changed_files: List[ChangedFile]
    total_additions: int
    total_deletions: int
    compare_url: Optional[str]
    error: Optional[str] = None


# ── GitHub HTTP helpers ───────────────────────────────────────────

def _github_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get(url: str, token: str, params: Optional[Dict] = None) -> requests.Response:
    """Single GET with a hard timeout. Raises requests.RequestException on failure."""
    return requests.get(
        url,
        headers=_github_headers(token),
        params=params or {},
        timeout=TOOL_TIMEOUT_SECONDS,
    )


def _unavailable_deployment(
    incident_time: Optional[str], window_hours: int, reason: str
) -> DeploymentQueryResponse:
    return DeploymentQueryResponse(
        status="unavailable",
        incident_time=incident_time,
        window_hours=window_hours,
        runs=[],
        total_found=0,
        error=reason,
    )


def _unavailable_commit(sha: str, reason: str) -> CommitChangesResponse:
    return CommitChangesResponse(
        status="unavailable",
        sha=sha,
        author=None,
        author_email=None,
        committed_at=None,
        message=None,
        changed_files=[],
        total_additions=0,
        total_deletions=0,
        compare_url=None,
        error=reason,
    )


# ── Tools ─────────────────────────────────────────────────────────

@tool(
    name="query_recent_deployments",
    description=(
        "Fetches GitHub Actions workflow runs within a time window around an incident. "
        "Use this to find deployments that may have caused a production incident. "
        "Returns run IDs, commit SHAs, statuses, and actors for further investigation."
    ),
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        ExpectedCredentials(app_id=GITHUB_APP_ID, type=ConnectionType.KEY_VALUE),
    ],
)
def query_recent_deployments(
    incident_time: str,
    window_hours: int = 2,
    max_results: int = 10,
) -> DeploymentQueryResponse:
    """
    Lists GitHub Actions runs that completed within ±window_hours of the incident timestamp.

    Args:
        incident_time (str): ISO-8601 timestamp of the incident (e.g. "2025-07-15T14:00:00Z").
                             If empty, uses the current UTC time.
        window_hours (int):  Hours either side of incident_time to search (default: 2).
        max_results (int):   Maximum number of runs to return (default: 10, max: 100).
    """
    gh_creds = connections.key_value(GITHUB_APP_ID)
    token = gh_creds.get("GITHUB_TOKEN", "")
    owner = gh_creds.get("GITHUB_REPO_OWNER", "")
    repo  = gh_creds.get("GITHUB_REPO_NAME", "")

    if not token or not owner or not repo:
        return _unavailable_deployment(
            incident_time, window_hours,
            "Missing GitHub credentials: GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME"
        )

    # Parse incident time
    try:
        if incident_time:
            inc_dt = datetime.fromisoformat(incident_time.replace("Z", "+00:00"))
        else:
            inc_dt = datetime.now(timezone.utc)
    except ValueError as exc:
        return _unavailable_deployment(
            incident_time, window_hours,
            f"Could not parse incident_time '{incident_time}': {exc}"
        )

    window_start = inc_dt - timedelta(hours=window_hours)
    window_end   = inc_dt + timedelta(hours=window_hours)

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs"
    params: Dict[str, Any] = {
        "per_page": min(max_results, 100),
        "created": f"{window_start.strftime('%Y-%m-%dT%H:%M:%SZ')}..{window_end.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "exclude_pull_requests": "true",
    }

    try:
        resp = _get(url, token, params)
    except requests.Timeout:
        return _unavailable_deployment(incident_time, window_hours, "GitHub API timed out")
    except requests.RequestException as exc:
        return _unavailable_deployment(incident_time, window_hours, f"GitHub API error: {exc}")

    if resp.status_code == 401:
        return _unavailable_deployment(incident_time, window_hours, "GitHub token is invalid or expired")
    if resp.status_code == 404:
        return _unavailable_deployment(incident_time, window_hours, f"Repository '{owner}/{repo}' not found")
    if not resp.ok:
        return _unavailable_deployment(
            incident_time, window_hours,
            f"GitHub API returned HTTP {resp.status_code}: {resp.text[:200]}"
        )

    payload = resp.json()
    raw_runs: List[Dict] = payload.get("workflow_runs", [])

    runs = [
        WorkflowRun(
            run_id=r["id"],
            name=r.get("name", ""),
            status=r.get("status", ""),
            conclusion=r.get("conclusion"),
            html_url=r.get("html_url", ""),
            head_sha=r.get("head_sha", ""),
            head_branch=r.get("head_branch", ""),
            created_at=r.get("created_at", ""),
            updated_at=r.get("updated_at", ""),
            triggering_actor=r.get("triggering_actor", {}).get("login") if r.get("triggering_actor") else None,
        )
        for r in raw_runs
    ]

    return DeploymentQueryResponse(
        status="ok",
        incident_time=inc_dt.isoformat(),
        window_hours=window_hours,
        runs=runs,
        total_found=len(runs),
    )


@tool(
    name="query_commit_changes",
    description=(
        "Fetches the changed files, diff summary, author, and timestamp for a specific "
        "GitHub commit SHA. Use this after query_recent_deployments identifies a suspect "
        "deployment to understand exactly what code changed."
    ),
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        ExpectedCredentials(app_id=GITHUB_APP_ID, type=ConnectionType.KEY_VALUE),
    ],
)
def query_commit_changes(
    commit_sha: str,
    patch_preview_chars: int = 300,
) -> CommitChangesResponse:
    """
    Returns changed files and diff details for a suspect commit SHA.

    Args:
        commit_sha (str):           Full or short (≥7 char) GitHub commit SHA.
        patch_preview_chars (int):  How many characters of the raw patch to include per file
                                    (default: 300; set to 0 to omit patches).
    """
    gh_creds = connections.key_value(GITHUB_APP_ID)
    token = gh_creds.get("GITHUB_TOKEN", "")
    owner = gh_creds.get("GITHUB_REPO_OWNER", "")
    repo  = gh_creds.get("GITHUB_REPO_NAME", "")

    if not token or not owner or not repo:
        return _unavailable_commit(
            commit_sha,
            "Missing GitHub credentials: GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME"
        )

    if not commit_sha or len(commit_sha) < 7:
        return _unavailable_commit(commit_sha, "commit_sha must be at least 7 characters")

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits/{commit_sha}"

    try:
        resp = _get(url, token)
    except requests.Timeout:
        return _unavailable_commit(commit_sha, "GitHub API timed out")
    except requests.RequestException as exc:
        return _unavailable_commit(commit_sha, f"GitHub API error: {exc}")

    if resp.status_code == 401:
        return _unavailable_commit(commit_sha, "GitHub token is invalid or expired")
    if resp.status_code == 422:
        return _unavailable_commit(commit_sha, f"Commit SHA '{commit_sha}' is ambiguous or invalid")
    if resp.status_code == 404:
        return _unavailable_commit(commit_sha, f"Commit '{commit_sha}' not found in '{owner}/{repo}'")
    if not resp.ok:
        return _unavailable_commit(
            commit_sha,
            f"GitHub API returned HTTP {resp.status_code}: {resp.text[:200]}"
        )

    data = resp.json()
    commit_obj  = data.get("commit", {})
    author_obj  = commit_obj.get("author", {})
    committer   = data.get("author") or {}         # GitHub user object (may be None)
    stats       = data.get("stats", {})
    raw_files   = data.get("files", [])

    changed_files = [
        ChangedFile(
            filename=f.get("filename", ""),
            status=f.get("status", ""),
            additions=f.get("additions", 0),
            deletions=f.get("deletions", 0),
            patch_summary=(f.get("patch", "")[:patch_preview_chars] if patch_preview_chars > 0 else None),
        )
        for f in raw_files
    ]

    return CommitChangesResponse(
        status="ok",
        sha=data.get("sha", commit_sha),
        author=author_obj.get("name") or committer.get("login"),
        author_email=author_obj.get("email"),
        committed_at=author_obj.get("date"),
        message=commit_obj.get("message", ""),
        changed_files=changed_files,
        total_additions=stats.get("additions", 0),
        total_deletions=stats.get("deletions", 0),
        compare_url=data.get("html_url"),
    )


# Made with Bob
