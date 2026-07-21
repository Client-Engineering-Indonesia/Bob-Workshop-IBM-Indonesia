# ingestion/create_indices.py

from es_client import get_es_client

RISK_MAPPING_INDEX    = "risk_mapping_hybrid_index"
RESOLUTION_NOTES_INDEX = "resolution_notes_hybrid_index"
DEPLOYMENTS_INDEX     = "deployments_index"

RISK_PIPELINE_ID = "risk_mapping_elser_pipeline"
RESOLUTION_PIPELINE_ID = "resolution_notes_elser_pipeline"

ELSER_MODEL_NAME = ".elser_model_2_linux-x86_64"

RISK_MAPPING_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "default_pipeline": RISK_PIPELINE_ID,
        "analysis": {
            "analyzer": {
                "english_analyzer": {
                    "type": "english"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "doc_id":       {"type": "keyword"},
            "title":        {"type": "text", "analyzer": "english_analyzer"},
            "category":     {"type": "keyword"},
            "risk_level":   {"type": "keyword"},   # Low / Medium / High / Critical
            "content":      {"type": "text", "analyzer": "english_analyzer"},
            "content_vector": {
                "type": "dense_vector",
                "dims": 1024,
                "index": True,
                "similarity": "cosine"             # Enable kNN search
            },
            "content_sparse":   {"type": "sparse_vector"},  # ELSER sparse embedding
            "source_file":  {"type": "keyword"},
            "page_number":  {"type": "integer"},
            "chunk_index":  {"type": "integer"},
            "created_at":   {"type": "date"}
        }
    }
}

RESOLUTION_NOTES_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "default_pipeline": RESOLUTION_PIPELINE_ID,
    },
    "mappings": {
        "properties": {
            "note_id":          {"type": "keyword"},
            "incident_type":    {"type": "keyword"},
            "resolution_steps": {"type": "text"},
            "resolution_vector": {
                "type": "dense_vector",
                "dims": 1024,
                "index": True,
                "similarity": "cosine"
            },
            "resolution_sparse":    {"type": "sparse_vector"},  # ELSER sparse embedding
            "category":         {"type": "keyword"},
            "tags":             {"type": "keyword"},
            "success_rate":     {"type": "float"},
            "created_at":       {"type": "date"}
        }
    }
}


def create_pipelines(es):
    es.ingest.put_pipeline(
        id=RISK_PIPELINE_ID,
        description="ELSER sparse encoding for risk mapping documents",
        processors=[
            {
                "inference": {
                    "model_id": ELSER_MODEL_NAME,
                    "input_output": [
                        {"input_field": "content", "output_field": "content_sparse"}
                    ],
                }
            }
        ],
    )
    print(f"[ES] Created pipeline '{RISK_PIPELINE_ID}'.")

    es.ingest.put_pipeline(
        id=RESOLUTION_PIPELINE_ID,
        description="ELSER sparse encoding for resolution notes",
        processors=[
            {
                "inference": {
                    "model_id": ELSER_MODEL_NAME,
                    "input_output": [
                        {"input_field": "resolution_steps", "output_field": "resolution_sparse"}
                    ],
                }
            }
        ],
    )
    print(f"[ES] Created pipeline '{RESOLUTION_PIPELINE_ID}'.")


# ── Deployments index mapping ─────────────────────────────────────
# Plain keyword/date index — no ML pipeline needed.
DEPLOYMENTS_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
    },
    "mappings": {
        "properties": {
            "run_id":               {"type": "long"},
            "repo":                 {"type": "keyword"},
            "workflow_name":        {"type": "keyword"},
            "workflow_file":        {"type": "keyword"},
            "head_sha":             {"type": "keyword"},
            "head_branch":          {"type": "keyword"},
            "status":               {"type": "keyword"},
            "conclusion":           {"type": "keyword"},
            "triggered_by":         {"type": "keyword"},
            "created_at":           {"type": "date"},
            "updated_at":           {"type": "date"},
            "run_duration_seconds": {"type": "integer"},
            "html_url":             {"type": "keyword"},
            "environment":          {"type": "keyword"},
            "services_deployed":    {"type": "keyword"},
            "commit_message":       {"type": "text"},
            "pr_number":            {"type": "integer"},
            "pr_title":             {"type": "text"},
            "failure_step":         {"type": "keyword"},
            "failure_log_snippet":  {"type": "text"},
            "ingested_at":          {"type": "date"},
        }
    },
}


def create_indices():
    es = get_es_client()

    create_pipelines(es)

    for index_name, settings in [
        (RISK_MAPPING_INDEX,    RISK_MAPPING_SETTINGS),
        (RESOLUTION_NOTES_INDEX, RESOLUTION_NOTES_SETTINGS),
        (DEPLOYMENTS_INDEX,     DEPLOYMENTS_SETTINGS),
    ]:
        if es.indices.exists(index=index_name):
            print(f"[ES] Index '{index_name}' already exists — skipping.")
        else:
            es.indices.create(index=index_name, body=settings)
            print(f"[ES] Created index '{index_name}'.")


if __name__ == "__main__":
    create_indices()

# Made with Bob
