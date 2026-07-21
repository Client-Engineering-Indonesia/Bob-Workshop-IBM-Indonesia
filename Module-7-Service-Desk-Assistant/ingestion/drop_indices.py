# ingestion/drop_indices.py

from es_client import get_es_client
from create_indices import RISK_MAPPING_INDEX, RESOLUTION_NOTES_INDEX, RISK_PIPELINE_ID, RESOLUTION_PIPELINE_ID


def drop_indices():
    es = get_es_client()

    for index_name in [RISK_MAPPING_INDEX, RESOLUTION_NOTES_INDEX]:
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            print(f"[ES] Dropped index '{index_name}'.")
        else:
            print(f"[ES] Index '{index_name}' does not exist — skipping.")


def drop_pipelines():
    es = get_es_client()

    for pipeline_id in [RISK_PIPELINE_ID, RESOLUTION_PIPELINE_ID]:
        try:
            es.ingest.delete_pipeline(id=pipeline_id)
            print(f"[ES] Dropped pipeline '{pipeline_id}'.")
        except Exception:
            print(f"[ES] Pipeline '{pipeline_id}' does not exist — skipping.")


if __name__ == "__main__":
    drop_indices()
    drop_pipelines()
