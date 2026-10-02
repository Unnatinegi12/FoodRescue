"""Phase 6 tests. They use a temporary ChromaDB folder and a test collection,
so they never touch (or depend on) rag/chroma_db. The first run downloads the embedding model."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # project root, so `import rag` works

from app.main import app
from rag import config
from rag.chunker import chunk_documents, chunk_text
from rag.document_loader import load_documents
from rag.embeddings import embed_texts
from rag.ingest import ingest
from rag.retriever import retrieve
from rag.vector_store import get_collection

TEST_COLLECTION = "pytest_foodrescue_knowledge"
EXPECTED_DOCUMENTS = {
    "cooked_food_safety", "food_storage", "food_transportation", "food_handling", "food_redistribution",
}


@pytest.fixture(scope="module")
def kb_dir(tmp_path_factory):
    """A temporary ChromaDB folder, filled once for this module."""
    path = tmp_path_factory.mktemp("chroma")
    ingest(collection=get_collection(path=path, name=TEST_COLLECTION), verbose=False)
    return path


@pytest.fixture
def kb(kb_dir):
    return get_collection(path=kb_dir, name=TEST_COLLECTION)


@pytest.fixture
def rag_client(kb_dir, monkeypatch):
    """TestClient whose /rag/search reads the temporary knowledge base."""
    monkeypatch.setattr(config, "CHROMA_DIR", kb_dir)
    monkeypatch.setattr(config, "COLLECTION_NAME", TEST_COLLECTION)
    return TestClient(app)


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))  # vectors have length 1


# ------------------------- loading -------------------------

def test_documents_load_correctly():
    docs = load_documents()
    assert {d["document_name"] for d in docs} == EXPECTED_DOCUMENTS
    for d in docs:
        assert d["text"].strip() and d["source"] and d["topic"]
        assert not d["text"].startswith("---")  # front matter was removed


def test_loader_cleans_text_and_reads_front_matter(tmp_path):
    (tmp_path / "sample_note.md").write_bytes(
        b"---\r\nsource: Test source\r\ntopic: Test topic\r\n---\r\nLine one.   \r\n\r\n\r\n\r\nLine  two.\r\n"
    )
    (tmp_path / "ignored.pdf").write_bytes(b"not supported")
    docs = load_documents(tmp_path)
    assert len(docs) == 1
    assert docs[0]["document_name"] == "sample_note"
    assert docs[0]["source"] == "Test source" and docs[0]["topic"] == "Test topic"
    assert docs[0]["text"] == "Line one.\n\nLine two."


# ------------------------- chunking -------------------------

def test_chunks_are_created():
    docs = load_documents()
    chunks = chunk_documents(docs)
    assert len(chunks) > len(docs)
    assert all(c["text"].strip() for c in chunks)


def test_chunk_metadata_is_preserved():
    docs = {d["document_name"]: d for d in load_documents()}
    for c in chunk_documents(list(docs.values())):
        original = docs[c["document_name"]]
        assert c["source"] == original["source"]
        assert c["topic"] == original["topic"]


def test_chunk_size_and_overlap():
    chunks = chunk_documents(load_documents())
    assert max(len(c["text"]) for c in chunks) <= config.CHUNK_SIZE
    by_doc = {}
    for c in chunks:
        by_doc.setdefault(c["document_name"], []).append(c)
    for doc_chunks in by_doc.values():
        for first, second in zip(doc_chunks, doc_chunks[1:]):
            assert second["text"][:10] in first["text"]  # neighbours share text


def test_chunker_edge_cases():
    assert chunk_text("") == []
    assert chunk_text("short text") == ["short text"]
    assert len(chunk_text("word " * 500, chunk_size=100, overlap=20)) > 10
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=10, overlap=10)


def test_chunk_ids_are_stable_and_unique():
    docs = load_documents()
    first, second = chunk_documents(docs), chunk_documents(docs)
    ids = [c["id"] for c in first]
    assert ids == [c["id"] for c in second]
    assert len(set(ids)) == len(ids)
    assert "cooked_food_safety-000" in ids


# ------------------------- embeddings -------------------------

def test_embeddings_are_generated():
    vectors = embed_texts(["cooked rice storage", "bread donation"])
    assert len(vectors) == 2
    assert len(vectors[0]) == len(vectors[1]) > 0
    assert all(isinstance(x, float) for x in vectors[0])
    assert embed_texts([]) == []


def test_similar_text_has_higher_similarity():
    a, b, c = embed_texts([
        "how to store cooked rice safely",
        "safe storage of cooked rice",
        "who won the football match yesterday",
    ])
    assert cosine(a, b) > cosine(a, c)


# ------------------------- vector store -------------------------

def test_vector_store_is_created_and_filled(kb):
    assert kb.count() == len(chunk_documents(load_documents()))


def test_ingestion_is_idempotent(kb):
    before = kb.count()
    result = ingest(collection=kb, verbose=False)
    assert kb.count() == before == result["chunks"]
    assert result["removed"] == 0


# ------------------------- retrieval -------------------------

def test_retrieval_returns_results(kb):
    results = retrieve("how do I donate bread", top_k=3, collection=kb)
    assert len(results) == 3
    for r in results:
        assert {"text", "source", "topic", "document_name", "score", "distance"} <= set(r)
        assert r["text"]
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_cooked_rice_query_returns_food_safety_content(kb):
    results = retrieve("What precautions should be followed when redistributing cooked rice?",
                       top_k=3, collection=kb)
    assert "cooked_food_safety" in {r["document_name"] for r in results}
    assert "rice" in " ".join(r["text"] for r in results).lower()


def test_transport_query_finds_transportation_document(kb):
    results = retrieve("What vehicle and containers should be used to carry hot food?",
                       top_k=3, collection=kb)
    assert "food_transportation" in {r["document_name"] for r in results}


# ------------------------- API -------------------------

def test_api_search_works(rag_client):
    r = rag_client.get("/rag/search", params={"query": "cooked food storage", "top_k": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["query"] == "cooked food storage"
    assert len(body["results"]) == 3
    assert set(body["results"][0]) == {"text", "source", "topic", "document_name", "score"}


@pytest.mark.parametrize("params", [
    {"query": ""},                      # empty
    {"query": "   "},                   # only spaces
    {},                                 # query missing
    {"query": "rice", "top_k": 0},      # below range
    {"query": "rice", "top_k": 11},     # above range
])
def test_api_rejects_invalid_input(rag_client, params):
    assert rag_client.get("/rag/search", params=params).status_code == 422


def test_api_returns_503_when_knowledge_base_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CHROMA_DIR", tmp_path)
    monkeypatch.setattr(config, "COLLECTION_NAME", "pytest_empty_collection")
    r = TestClient(app).get("/rag/search", params={"query": "rice"})
    assert r.status_code == 503
    assert "rag.ingest" in r.json()["detail"]
