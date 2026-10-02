from typing import Optional

from rag import config
from rag.embeddings import embed_query
from rag.vector_store import get_collection, query_similar


def retrieve(
    query: str,
    top_k: Optional[int] = None,
    collection=None
) -> list:
    """
    Retrieve the most relevant knowledge chunks
    for a given query.
    """

    top_k = (
        config.DEFAULT_TOP_K
        if top_k is None
        else top_k
    )

    collection = (
        collection
        if collection is not None
        else get_collection()
    )

    if collection.count() == 0:
        return []

    query_embedding = embed_query(query)

    hits = query_similar(
        collection,
        query_embedding,
        top_k
    )

    return [
        {
            "text": hit["text"],
            "source": hit["metadata"]["source"],
            "topic": hit["metadata"]["topic"],
            "document_name": hit["metadata"]["document_name"],
            "chunk_index": hit["metadata"]["chunk_index"],
            "distance": hit["distance"],
            "score": round(
                1 - hit["distance"] / 2,
                4
            ),
        }
        for hit in hits
    ]