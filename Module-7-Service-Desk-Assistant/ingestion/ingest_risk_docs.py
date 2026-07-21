# ingestion/ingest_risk_docs.py

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from elasticsearch.helpers import bulk
from langchain_ibm import WatsonxEmbeddings

from es_client import get_es_client

# ── Config ────────────────────────────────────────────────────────
INDEX_NAME = "risk_mapping_hybrid_index"
DOCS_DIR = Path("./data/risk_docs")

# Risk categories — validate against these during ingestion
VALID_CATEGORIES = [
    "Operational Risk",
    "Security Risk",
    "Compliance Risk",
    "Infrastructure Risk",
    "Data Privacy Risk",
    "Third-Party Risk",
    "Business Continuity Risk",
]


def load_risk_documents_from_json(file_path: Path) -> list[dict]:
    """
    Load risk documents from JSON file.
    Expected format:
    [
      {
        "risk_id": "RISK-001",
        "risk_category": "Operational Risk",
        "risk_subcategory": "System Availability",
        "risk_description": "...",
        "severity_level": "High",
        "keywords": [...],
        "related_incidents": [...],
        "mitigation_strategies": "...",
        "compliance_requirements": "...",
        "created_date": "2024-01-15T10:00:00Z",
        "updated_date": "2024-03-10T14:30:00Z"
      },
      ...
    ]
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_documents(
    embedder: WatsonxEmbeddings,
) -> Generator[dict, None, None]:
    """Yield Elasticsearch bulk action dicts for all risk documents from JSON files."""
    json_files = list(DOCS_DIR.glob("*.json"))
    print(f"[Ingest] Found {len(json_files)} JSON files in {DOCS_DIR}")

    for json_path in json_files:
        print(f"[Ingest] Processing: {json_path.name}")
        risk_docs = load_risk_documents_from_json(json_path)
        
        for doc in risk_docs:
            # Combine all text fields for embedding
            content_text = (
                f"Risk Category: {doc.get('risk_category', '')}. "
                f"Subcategory: {doc.get('risk_subcategory', '')}. "
                f"Description: {doc.get('risk_description', '')}. "
                f"Mitigation: {doc.get('mitigation_strategies', '')}. "
                f"Keywords: {', '.join(doc.get('keywords', []))}. "
                f"Related Incidents: {', '.join(doc.get('related_incidents', []))}."
            )
            
            # Generate embedding
            embedding = embedder.embed_query(content_text)
            
            yield {
                "_index": INDEX_NAME,
                "_id": str(uuid.uuid4()),
                "_source": {
                    "doc_id": doc.get("risk_id"),
                    "title": f"{doc.get('risk_category')} - {doc.get('risk_subcategory')}",
                    "category": doc.get("risk_category"),
                    "risk_level": doc.get("severity_level"),
                    "content": content_text,
                    "content_vector": embedding,
                    "source_file": json_path.name,
                    "risk_subcategory": doc.get("risk_subcategory"),
                    "keywords": doc.get("keywords", []),
                    "related_incidents": doc.get("related_incidents", []),
                    "mitigation_strategies": doc.get("mitigation_strategies"),
                    "compliance_requirements": doc.get("compliance_requirements"),
                    "chunk_index": 0,  # Single document, no chunking
                    "created_at": doc.get("created_date", datetime.now(timezone.utc).isoformat()),
                }
            }


def run_ingestion():
    es = get_es_client()
    print("[Ingest] Initializing WatsonX embeddings client")
    embedder = WatsonxEmbeddings(
        model_id="intfloat/multilingual-e5-large",
        url=os.environ["WATSONX_URL"],
        apikey=os.environ["WATSONX_APIKEY"],
        project_id=os.environ["WATSONX_PROJECT_ID"],
    )

    successes, errors = bulk(
        es,
        generate_documents(embedder),
        chunk_size=100,
        raise_on_error=False,
        stats_only=False,
    )

    print(f"[Ingest] ✅ Ingested {successes} chunks successfully.")
    if errors:
        print(f"[Ingest] ⚠️  {len(errors)} errors occurred:")
        for err in errors[:5]:
            print(f"   {err}")


if __name__ == "__main__":
    run_ingestion()

# Made with Bob
