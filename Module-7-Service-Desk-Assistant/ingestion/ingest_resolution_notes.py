# ingestion/ingest_resolution_notes.py

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from elasticsearch.helpers import bulk
from langchain_ibm import WatsonxEmbeddings

from es_client import get_es_client

INDEX_NAME = "resolution_notes_hybrid_index"
NOTES_DIR = Path("./data/resolution_notes")


def load_notes_from_json(file_path: Path) -> list[dict]:
    """
    Expected JSON format:
    [
      {
        "incident_number": "INC0010001",
        "short_description": "Cannot access email",
        "detailed_description": "...",
        "category": "Software",
        "subcategory": "Email",
        "priority": "2",
        "resolution_notes": "...",
        "resolution_steps": "1. Step one\n2. Step two...",
        "resolution_time_hours": 0.5,
        "resolved_by": "John Smith",
        "tags": ["outlook", "email"],
        "created_date": "2024-03-01T09:15:00Z",
        "resolved_date": "2024-03-01T09:45:00Z",
        "satisfaction_score": 5
      },
      ...
    ]
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_notes_from_csv(file_path: Path) -> list[dict]:
    """Alternative: load from CSV export."""
    import csv
    notes = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["tags"] = [t.strip() for t in row.get("tags", "").split(",")]
            row["satisfaction_score"] = int(row.get("satisfaction_score", 3))
            row["resolution_time_hours"] = float(row.get("resolution_time_hours", 1.0))
            notes.append(row)
    return notes


def generate_note_documents(
    notes: list[dict],
    embedder: WatsonxEmbeddings,
):
    for note in notes:
        # Combine relevant fields for embedding
        text_to_embed = (
            f"Category: {note.get('category', '')} - {note.get('subcategory', '')}. "
            f"Issue: {note.get('short_description', '')}. "
            f"Details: {note.get('detailed_description', '')}. "
            f"Resolution: {note.get('resolution_notes', '')}. "
            f"Steps: {note.get('resolution_steps', '')}"
        )
        embedding = embedder.embed_query(text_to_embed)
        
        # Calculate success rate from satisfaction score (1-5 scale to 0-1)
        satisfaction = note.get("satisfaction_score", 3)
        success_rate = satisfaction / 5.0 if satisfaction else 0.6

        yield {
            "_index": INDEX_NAME,
            "_id": str(uuid.uuid4()),
            "_source": {
                "note_id": note.get("incident_number", str(uuid.uuid4())),
                "incident_type": note.get("short_description"),
                "resolution_steps": note.get("resolution_steps"),
                "resolution_vector": embedding,
                "category": note.get("category"),
                "subcategory": note.get("subcategory"),
                "tags": note.get("tags", []),
                "success_rate": success_rate,
                "resolution_notes": note.get("resolution_notes"),
                "detailed_description": note.get("detailed_description"),
                "priority": note.get("priority"),
                "resolution_time_hours": note.get("resolution_time_hours"),
                "resolved_by": note.get("resolved_by"),
                "satisfaction_score": satisfaction,
                "created_at": note.get("created_date", datetime.now(timezone.utc).isoformat()),
            }
        }


def run_ingestion():
    es = get_es_client()
    embedder = WatsonxEmbeddings(
        model_id="intfloat/multilingual-e5-large",
        url=os.environ["WATSONX_URL"],
        apikey=os.environ["WATSONX_APIKEY"],
        project_id=os.environ["WATSONX_PROJECT_ID"],
    )

    all_notes = []
    for json_file in NOTES_DIR.glob("*.json"):
        all_notes.extend(load_notes_from_json(json_file))
    for csv_file in NOTES_DIR.glob("*.csv"):
        all_notes.extend(load_notes_from_csv(csv_file))

    print(f"[Ingest] Loaded {len(all_notes)} resolution notes.")

    successes, errors = bulk(
        es,
        generate_note_documents(all_notes, embedder),
        chunk_size=50,
        raise_on_error=False,
    )
    print(f"[Ingest] ✅ Ingested {successes} notes.")
    if errors:
        print(f"[Ingest] ⚠️  Errors: {errors}")


if __name__ == "__main__":
    run_ingestion()

# Made with Bob
