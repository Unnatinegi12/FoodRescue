import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.rag_service import (
    RagUnavailableError,
    search_knowledge,
)


logger = logging.getLogger("foodrescue")

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


class RagResult(BaseModel):
    text: str
    source: str
    topic: str
    document_name: str
    score: float


class RagSearchResponse(BaseModel):
    query: str
    results: list[RagResult]


@router.get(
    "/search",
    response_model=RagSearchResponse,
)
def search(
    query: str = Query(
        ...,
        min_length=1,
        max_length=500,
        description="What to look up",
    ),
    top_k: int = Query(
        5,
        ge=1,
        le=10,
        description="How many chunks to return (1-10)",
    ),
):
    if not query.strip():
        raise HTTPException(
            status_code=422,
            detail="query must not be empty",
        )

    try:
        results = search_knowledge(
            query,
            top_k,
        )

    except RagUnavailableError as e:
        logger.error(
            "RAG unavailable: %s",
            e,
        )

        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    return RagSearchResponse(
        query=query,
        results=results,
    )