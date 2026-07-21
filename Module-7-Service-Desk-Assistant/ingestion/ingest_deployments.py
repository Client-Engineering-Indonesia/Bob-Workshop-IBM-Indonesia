# ingestion/ingest_deployments.py
#
# Indexes GitHub Actions deployment records into Elasticsearch.
# Source file: data/deployments/sample_deployments.json
# Target index: deployments_index
#
# Does NOT require watsonx.ai embeddings — deployment records are
# searched by keyword/date range, not by semantic similarity.
#
# Usage (from ingestion/ directory):
#     python3 ingest_deployments.py

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from elasticsearch.helpers import bulk

from es_client import get_es_client

INDEX_NAME    = "deployments_index"
DEPLOYMENTS_DIR = Path("../data/deployments")


def load_deployments(file_path: Path) -> list[dict]:
    """Load deployment records from JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_deployment_docs(deployments: list[dict]):
    """Yield Elasticsearch bulk-index actions for each deployment record."""
    for d in deployments:
        yield {
            "_index": INDEX_NAME,
            "_id":    str(d.get("run_id", uuid.uuid4())),
            "_source": {
                "run_id":               d.get("run_id"),
                "repo":                 d.get("repo"),
                "workflow_name":        d.get("workflow_name"),
                "workflow_file":        d.get("workflow_file"),
                "head_sha":             d.get("head_sha"),
                "head_branch":          d.get("head_branch"),
                "status":               d.get("status"),
                "conclusion":           d.get("conclusion"),          # success | failure | cancelled
                "triggered_by":         d.get("triggered_by"),
                "created_at":           d.get("created_at"),
                "updated_at":           d.get("updated_at"),
                "run_duration_seconds": d.get("run_duration_seconds"),
                "html_url":             d.get("html_url"),
                "environment":          d.get("environment"),
                "services_deployed":    d.get("services_deployed", []),
                "commit_message":       d.get("commit_message"),
                "pr_number":            d.get("pr_number"),
                "pr_title":             d.get("pr_title"),
                "failure_step":         d.get("failure_step"),
                "failure_log_snippet":  d.get("failure_log_snippet"),
                "ingested_at":          datetime.now(timezone.utc).isoformat(),
            },
        }


def run_ingestion() -> None:
    es = get_es_client()

    # Ensure index exists
    if not es.indices.exists(index=INDEX_NAME):
        print(f"[Ingest] Index '{INDEX_NAME}' not found — run create_indices.py first.")
        return

    all_deployments: list[dict] = []
    for json_file in DEPLOYMENTS_DIR.glob("*.json"):
        records = load_deployments(json_file)
        all_deployments.extend(records)
        print(f"[Ingest] Loaded {len(records)} records from {json_file.name}")

    if not all_deployments:
        print("[Ingest] No deployment files found in data/deployments/")
        return

    print(f"[Ingest] Indexing {len(all_deployments)} deployment records into '{INDEX_NAME}'...")
    successes, errors = bulk(
        es,
        generate_deployment_docs(all_deployments),
        chunk_size=100,
        raise_on_error=False,
    )
    print(f"[Ingest] ✅ Indexed {successes} records.")
    if errors:
        print(f"[Ingest] ⚠️  Errors: {errors}")


if __name__ == "__main__":
    run_ingestion()

# Made with Bob
