# ingestion/search.py
# Used by agents to query Watsonx Discovery

import os
from langchain_ibm import WatsonxEmbeddings
from es_client import get_es_client


def _get_embeddings_client() -> WatsonxEmbeddings:
    return WatsonxEmbeddings(
        model_id="intfloat/multilingual-e5-large",
        url=os.environ["WATSONX_URL"],
        apikey=os.environ["WATSONX_APIKEY"],
        project_id=os.environ["WATSONX_PROJECT_ID"],
    )


def hybrid_search(
    index: str,
    query_text: str,
    vector_field: str,
    sparse_field: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Hybrid search combining BM25 (keyword) and kNN (semantic vector).
    Returns top_k ranked results.
    """
    es = get_es_client()
    embeddings = _get_embeddings_client()
    query_vector = embeddings.embed_query(query_text)

    response = es.search(
        index=index,
        body={
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        # ELSER sparse match
                        {
                            "text_expansion": {
                                sparse_field: {
                                    "model_id": ".elser_model_2_linux-x86_64",
                                    "model_text": query_text,
                                }
                            }
                        },
                        # kNN semantic match via script_score
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": f"cosineSimilarity(params.query_vector, '{vector_field}') + 1.0",
                                    "params": {"query_vector": query_vector}
                                },
                                "boost": 2.0
                            }
                        }
                    ]
                }
            },
            "_source": {"excludes": [vector_field]}   # Don't return raw vectors
        }
    )

    return [
        {
            "score": hit["_score"],
            "content": hit["_source"].get("content") or hit["_source"].get("resolution_steps"),
            "metadata": {k: v for k, v in hit["_source"].items()
                         if k not in ("content", "resolution_steps")}
        }
        for hit in response["hits"]["hits"]
    ]


if __name__ == "__main__":
    results = hybrid_search(
        index="risk_mapping_hybrid_index",
        query_text="system outage causing service disruption",
        vector_field="content_vector",
        sparse_field="content_sparse",
        top_k=3,
    )
    for i, r in enumerate(results, 1):
        print(f"\nResult {i} (score: {r['score']:.4f})")
        print(f"Content : {str(r['content'])[:200]}")
        print(f"Metadata: {r['metadata']}")

# Made with Bob
