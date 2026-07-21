# agents/risk_tools.py

from typing import List, Optional, Dict
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.run import connections
from pydantic.dataclasses import dataclass
from elasticsearch import Elasticsearch
from langchain_ibm import WatsonxEmbeddings


ES_APP_ID = "elasticsearch-service-desk"
WATSONX_APP_ID = "watsonx-ai-service-desk"

ELSER_MODEL_NAME = ".elser_model_2_linux-x86_64"
DENSE_MODEL_NAME = "intfloat/multilingual-e5-large"

RISK_INDEX = "risk_mapping_hybrid_index"
RESOLUTION_INDEX = "resolution_notes_hybrid_index"


# ── Dataclasses ───────────────────────────────────────────────────

@dataclass
class RiskDocument:
    """A single risk or governance document result."""
    content: str
    title: Optional[str] = None
    category: Optional[str] = None
    risk_level: Optional[str] = None
    source_file: Optional[str] = None
    relevance_score: Optional[float] = None


@dataclass
class RiskSearchResponse:
    """Response from risk document search."""
    documents: List[RiskDocument]
    total_retrieved: int
    error: Optional[str] = None


@dataclass
class ResolutionNote:
    """A single past incident resolution result."""
    incident_type: Optional[str] = None
    detailed_description: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolution_steps: Optional[str] = None
    resolution_time_hours: Optional[float] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    relevance_score: Optional[float] = None


@dataclass
class ResolutionSearchResponse:
    """Response from resolution notes search."""
    resolutions: List[ResolutionNote]
    total_retrieved: int
    error: Optional[str] = None


# ── ES client ─────────────────────────────────────────────────────

def get_es_client(es_creds: Dict) -> tuple[Optional[Elasticsearch], Optional[str]]:
    """Create an Elasticsearch client from credentials dict."""
    import tempfile

    host = es_creds.get("ES_HOST", "").replace("https://", "").replace("http://", "").strip()
    port = int(es_creds.get("ES_PORT", 9200))
    username = es_creds.get("ES_USERNAME", "")
    password = es_creds.get("ES_PASSWORD", "")
    cert_content = es_creds.get("ES_CERT_CONTENT", "")
    use_ssl = str(es_creds.get("ES_USE_SSL", "true")).lower() == "true"
    verify_certs = str(es_creds.get("ES_VERIFY_CERTS", "false")).lower() == "true"

    if not all([host, username, password]):
        return None, "Missing required ES credentials: ES_HOST, ES_USERNAME, ES_PASSWORD"

    es_params = {
        "hosts": [{"host": host, "port": port, "scheme": "https" if use_ssl else "http"}],
        "basic_auth": (username, password),
        "verify_certs": verify_certs,
        "ssl_show_warn": not verify_certs,
        "request_timeout": 10,
        "retry_on_timeout": False,
        "max_retries": 1,
        "http_compress": True,
    }

    if verify_certs and cert_content:
        cert_file = tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False)
        cert_file.write(cert_content)
        cert_file.flush()
        es_params["ca_certs"] = cert_file.name
        cert_file.close()

    try:
        return Elasticsearch(**es_params), None
    except Exception as e:
        return None, f"Failed to create ES client: {str(e)}"


# ── Embeddings ────────────────────────────────────────────────────

def get_watsonx_embeddings(text: str, watsonx_creds: Dict) -> tuple[Optional[List[float]], Optional[str]]:
    """Convert text to embeddings using WatsonX."""
    try:
        url = watsonx_creds.get("WATSONX_URL")
        apikey = watsonx_creds.get("WATSONX_APIKEY")
        project_id = watsonx_creds.get("WATSONX_PROJECT_ID")

        if not url or not apikey or not project_id:
            return None, "Missing required WatsonX credentials"

        embeddings = WatsonxEmbeddings(
            model_id=DENSE_MODEL_NAME,
            url=url,
            apikey=apikey,
            project_id=project_id,
        )
        return embeddings.embed_query(text), None

    except Exception as e:
        return None, f"Error generating embeddings: {str(e)}"


# ── Hybrid search ─────────────────────────────────────────────────

def hybrid_search(
    es: Elasticsearch,
    index: str,
    query_text: str,
    query_vector: List[float],
    vector_field: str,
    sparse_field: str,
    top_k: int,
) -> tuple[Optional[List[dict]], Optional[str]]:
    """Hybrid search combining ELSER sparse (text_expansion) and kNN dense vector."""
    try:
        response = es.search(
            index=index,
            body={
                "size": top_k,
                "query": {
                    "bool": {
                        "should": [
                            {
                                "text_expansion": {
                                    sparse_field: {
                                        "model_id": ELSER_MODEL_NAME,
                                        "model_text": query_text,
                                    }
                                }
                            },
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": f"cosineSimilarity(params.query_vector, '{vector_field}') + 1.0",
                                        "params": {"query_vector": query_vector},
                                    },
                                    "boost": 2.0,
                                }
                            },
                        ]
                    }
                },
                "_source": {"excludes": [vector_field, sparse_field]},
            },
        )
        return response["hits"]["hits"], None
    except Exception as e:
        return None, f"Search error: {str(e)}"


# ── Tools ─────────────────────────────────────────────────────────

@tool(
    name="retrieve_risk_documents",
    description="Searches risk and governance documents using hybrid semantic and sparse search.",
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        ExpectedCredentials(app_id=ES_APP_ID, type=ConnectionType.KEY_VALUE),
        ExpectedCredentials(app_id=WATSONX_APP_ID, type=ConnectionType.KEY_VALUE),
    ],
)
def retrieve_risk_documents(
    incident_description: str,
    top_k: int = 3,
) -> RiskSearchResponse:
    """
    Performs hybrid search on risk_mapping_hybrid_index to retrieve relevant governance documents.

    Args:
        incident_description: The incident text to search against the risk knowledge base
        top_k: Number of documents to retrieve (default: 3)
    """
    es_creds = connections.key_value(ES_APP_ID)
    watsonx_creds = connections.key_value(WATSONX_APP_ID)

    es, error = get_es_client(es_creds)
    if error:
        return RiskSearchResponse(documents=[], total_retrieved=0, error=error)

    query_vector, error = get_watsonx_embeddings(incident_description, watsonx_creds)
    if error:
        return RiskSearchResponse(documents=[], total_retrieved=0, error=error)

    hits, error = hybrid_search(
        es=es,
        index=RISK_INDEX,
        query_text=incident_description,
        query_vector=query_vector,
        vector_field="content_vector",
        sparse_field="content_sparse",
        top_k=top_k,
    )
    if error:
        return RiskSearchResponse(documents=[], total_retrieved=0, error=error)

    documents = [
        RiskDocument(
            content=hit["_source"].get("content", ""),
            title=hit["_source"].get("title"),
            category=hit["_source"].get("category"),
            risk_level=hit["_source"].get("risk_level"),
            source_file=hit["_source"].get("source_file"),
            relevance_score=round(hit["_score"], 4),
        )
        for hit in hits
    ]
    return RiskSearchResponse(documents=documents, total_retrieved=len(documents))


@tool(
    name="retrieve_resolution_notes",
    description="Retrieves similar past incident resolutions using hybrid semantic and sparse search.",
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        ExpectedCredentials(app_id=ES_APP_ID, type=ConnectionType.KEY_VALUE),
        ExpectedCredentials(app_id=WATSONX_APP_ID, type=ConnectionType.KEY_VALUE),
    ],
)
def retrieve_resolution_notes(
    incident_description: str,
    top_k: int = 2,
) -> ResolutionSearchResponse:
    """
    Performs hybrid search on resolution_notes_hybrid_index to find similar past incidents.

    Args:
        incident_description: The incident text to search for similar past resolutions
        top_k: Number of resolutions to retrieve (default: 2)
    """
    es_creds = connections.key_value(ES_APP_ID)
    watsonx_creds = connections.key_value(WATSONX_APP_ID)

    es, error = get_es_client(es_creds)
    if error:
        return ResolutionSearchResponse(resolutions=[], total_retrieved=0, error=error)

    query_vector, error = get_watsonx_embeddings(incident_description, watsonx_creds)
    if error:
        return ResolutionSearchResponse(resolutions=[], total_retrieved=0, error=error)

    hits, error = hybrid_search(
        es=es,
        index=RESOLUTION_INDEX,
        query_text=incident_description,
        query_vector=query_vector,
        vector_field="resolution_vector",
        sparse_field="resolution_sparse",
        top_k=top_k,
    )
    if error:
        return ResolutionSearchResponse(resolutions=[], total_retrieved=0, error=error)

    resolutions = [
        ResolutionNote(
            incident_type=hit["_source"].get("incident_type"),
            detailed_description=hit["_source"].get("detailed_description"),
            resolution_notes=hit["_source"].get("resolution_notes"),
            resolution_steps=hit["_source"].get("resolution_steps"),
            resolution_time_hours=hit["_source"].get("resolution_time_hours"),
            priority=hit["_source"].get("priority"),
            category=hit["_source"].get("category"),
            relevance_score=round(hit["_score"], 4),
        )
        for hit in hits
    ]
    return ResolutionSearchResponse(resolutions=resolutions, total_retrieved=len(resolutions))


# Made with Bob
