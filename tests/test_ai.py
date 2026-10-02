import sys
from pathlib import Path

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app


client = TestClient(app)


def test_ai_ask_missing_question():
    response = client.post("/ai/ask", json={})
    assert response.status_code == 422


def test_ai_ask_empty_question():
    response = client.post(
        "/ai/ask",
        json={"question": ""}
    )
    assert response.status_code == 422


def test_ai_ask_whitespace_question():
    response = client.post(
        "/ai/ask",
        json={"question": "   "}
    )
    assert response.status_code == 422


def test_ai_ask_question_too_long():
    response = client.post(
        "/ai/ask",
        json={"question": "a" * 501}
    )
    assert response.status_code == 422
