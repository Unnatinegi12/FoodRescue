from pathlib import Path
from typing import Optional

from rag import config
from rag.chunker import chunk_documents
from rag.document_loader import load_documents
from rag.embeddings import embed_texts
from rag.vector_store import (
    add_chunks,
    get_collection,
    remove_stale_chunks,
)


def ingest(
    data_dir: Optional[Path] = None,
    collection=None,
    verbose: bool = True,
) -> dict:

    def say(message):
        if verbose:
            print(message)

    # 1. Load documents
    documents = load_documents(data_dir)
    say(f"Loaded {len(documents)} documents")

    # 2. Create chunks
    chunks = chunk_documents(documents)

    if not chunks:
        raise ValueError(
            "No text found to ingest. "
            "Check the rag/data folder."
        )

    say(f"Created {len(chunks)} chunks")

    # 3. Generate embeddings
    say(
        f"Embedding with {config.EMBEDDING_MODEL} "
        "(the first run downloads the model)..."
    )

    embeddings = embed_texts(
        [chunk["text"] for chunk in chunks]
    )

    # 4. Store in ChromaDB
    collection = (
        collection
        if collection is not None
        else get_collection()
    )

    add_chunks(
        collection,
        chunks,
        embeddings
    )

    say(f"Stored {len(chunks)} chunks")

    # 5. Remove old chunks
    removed = remove_stale_chunks(
        collection,
        {
            chunk["id"]
            for chunk in chunks
        },
    )

    if removed:
        say(
            f"Removed {removed} outdated chunks"
        )

    say(
        f"Collection '{collection.name}' "
        f"now holds {collection.count()} chunks"
    )

    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "removed": removed,
        "total": collection.count(),
    }


if __name__ == "__main__":
    ingest()