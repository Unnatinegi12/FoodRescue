from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings

from rag import config


def get_collection(
    path: Optional[Path] = None,
    name: Optional[str] = None
):
    """Open or create a persistent ChromaDB collection."""

    folder = (
        Path(path)
        if path
        else config.CHROMA_DIR
    )

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=str(folder),
        settings=Settings(
            anonymized_telemetry=False
        )
    )

    return client.get_or_create_collection(
        name=name or config.COLLECTION_NAME
    )


def add_chunks(
    collection,
    chunks: list,
    embeddings: list
) -> None:
    """Store or update chunks in ChromaDB."""

    collection.upsert(
        ids=[
            chunk["id"]
            for chunk in chunks
        ],
        documents=[
            chunk["text"]
            for chunk in chunks
        ],
        embeddings=embeddings,
        metadatas=[
            {
                "source": chunk["source"],
                "topic": chunk["topic"],
                "document_name": chunk["document_name"],
                "chunk_index": chunk["chunk_index"],
            }
            for chunk in chunks
        ],
    )


def remove_stale_chunks(
    collection,
    valid_ids: set
) -> int:
    """Remove chunks that no longer exist in source documents."""

    existing_ids = collection.get()["ids"]

    stale = [
        chunk_id
        for chunk_id in existing_ids
        if chunk_id not in valid_ids
    ]

    if stale:
        collection.delete(ids=stale)

    return len(stale)


def query_similar(
    collection,
    query_embedding: list,
    top_k: int
) -> list:
    """Return the nearest chunks from ChromaDB."""

    count = collection.count()

    if count == 0:
        return []

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, count),
        include=[
            "documents",
            "metadatas",
            "distances"
        ],
    )

    return [
        {
            "text": text,
            "metadata": metadata,
            "distance": distance,
        }
        for text, metadata, distance in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]