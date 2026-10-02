import os
from pathlib import Path


RAG_DIR = Path(__file__).resolve().parent

DATA_DIR = RAG_DIR / "data"

CHROMA_DIR = Path(
    os.getenv("RAG_CHROMA_DIR", RAG_DIR / "chroma_db")
)

COLLECTION_NAME = os.getenv(
    "RAG_COLLECTION_NAME",
    "foodrescue_knowledge"
)

EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

CHUNK_SIZE = 700
CHUNK_OVERLAP = 80

DEFAULT_TOP_K = 5
MAX_TOP_K = 10