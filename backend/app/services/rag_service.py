import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class RagUnavailableError(Exception):
    """RAG cannot answer right now (dependencies missing or knowledge base not built)."""


def search_knowledge(query: str, top_k: int = 5) -> list:
    try:
        from rag.retriever import retrieve

        results = retrieve(query.strip(), top_k)

    except ImportError as e:
        raise RagUnavailableError(
            "RAG dependencies are not installed. "
            "Run: pip install -r requirements.txt"
        ) from e

    if not results:
        raise RagUnavailableError(
            "The knowledge base is empty. "
            "From the project root run: python -m rag.ingest"
        )

    return results