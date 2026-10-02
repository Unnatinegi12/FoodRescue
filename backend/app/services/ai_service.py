"""Grounded answers: RAG retrieval first, then Gemini answers from the retrieved chunks only."""
import os

from app.services.llm_service import generate_answer
from app.services.rag_service import search_knowledge

TOP_K = 4
# Chunks scoring below this (cosine similarity) are treated as unrelated to the question.
# Tune it by looking at the scores returned by GET /rag/search.
MIN_SCORE = float(os.getenv("AI_MIN_SCORE", "0.2"))

NOT_ENOUGH_INFO = (
    "The FoodRescue knowledge base does not provide enough information to answer this question."
)


def build_context(chunks: list) -> str:
    """Label each chunk so the model (and a human reading the prompt) can tell them apart."""
    return "\n\n".join(
        f"[Source {i}: {c['document_name']} - {c['topic']}]\n{c['text']}"
        for i, c in enumerate(chunks, start=1)
    )


def unique_sources(chunks: list) -> list:
    """One entry per document, with its best score (chunks arrive best-first)."""
    seen = {}
    for c in chunks:
        seen.setdefault(c["document_name"], {
            "document_name": c["document_name"], "topic": c["topic"], "score": c["score"],
        })
    return list(seen.values())


def ask(question: str) -> dict:
    question = question.strip()
    results = search_knowledge(question, TOP_K)   # may raise RagUnavailableError
    relevant = [r for r in results if r["score"] >= MIN_SCORE]

    if not relevant:  # nothing related in the knowledge base: don't call the LLM at all
        return {"question": question, "answer": NOT_ENOUGH_INFO, "sources": []}

    answer = generate_answer(question, build_context(relevant))  # may raise LLMUnavailableError
    return {"question": question, "answer": answer, "sources": unique_sources(relevant)}
