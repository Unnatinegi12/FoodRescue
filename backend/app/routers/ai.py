import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.services import ai_service
from app.services.llm_service import LLMUnavailableError
from app.services.rag_service import RagUnavailableError

logger = logging.getLogger("foodrescue")
router = APIRouter(prefix="/ai", tags=["AI"])


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be empty")
        return value.strip()


class SourceOut(BaseModel):
    document_name: str
    topic: str
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceOut]


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    """Retrieve relevant FoodRescue knowledge (RAG), then let Gemini answer from it only."""
    try:
        return ai_service.ask(payload.question)
    except RagUnavailableError as e:
        logger.error("RAG unavailable: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
    except LLMUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))  # messages are already client-safe