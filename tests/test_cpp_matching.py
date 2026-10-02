import json
import os
from pathlib import Path

import pytest

from app.services.cpp_matcher import find_executable, run_cpp_engine


def test_cpp_executable_exists():
    executable = find_executable()

    if not Path(executable).exists():
        pytest.skip("C++ matcher executable not built")

    assert Path(executable).exists()


def sample_payload():
    return {
        "donation": {
            "id": 1,
            "food_type": "rice",
            "quantity_kg": 50,
            "city": "Jaipur",
            "expiry_time": "2026-10-03T18:00:00",
            "is_vegetarian": True,
        },
        "ngos": [
            {
                "id": 1,
                "name": "Helping Hands",
                "city": "Jaipur",
                "capacity_kg": 100,
                "accepts_non_veg": False,
            },
            {
                "id": 2,
                "name": "Food For All",
                "city": "Delhi",
                "capacity_kg": 100,
                "accepts_non_veg": True,
            },
        ],
        "requirements": [
            {
                "id": 1,
                "ngo_id": 1,
                "food_type": "rice",
                "required_meals": 50,
            },
            {
                "id": 2,
                "ngo_id": 2,
                "food_type": "rice",
                "required_meals": 50,
            },
        ],
    }


def test_cpp_engine_returns_matches():
    if not Path(find_executable()).exists():
        pytest.skip("C++ matcher executable not built")

    result = run_cpp_engine(sample_payload())

    assert "matches" in result
    assert len(result["matches"]) == 2


def test_cpp_engine_ranks_same_city_first():
    if not Path(find_executable()).exists():
        pytest.skip("C++ matcher executable not built")

    result = run_cpp_engine(sample_payload())

    matches = result["matches"]

    assert matches[0]["ngo_id"] == 1
    assert matches[0]["match_score"] > matches[1]["match_score"]


def test_cpp_engine_rejects_food_type_mismatch():
    if not Path(find_executable()).exists():
        pytest.skip("C++ matcher executable not built")

    payload = sample_payload()

    payload["donation"]["food_type"] = "bread"

    result = run_cpp_engine(payload)

    assert result["matches"] == []


def test_cpp_engine_rejects_over_capacity():
    if not Path(find_executable()).exists():
        pytest.skip("C++ matcher executable not built")

    payload = sample_payload()

    payload["donation"]["quantity_kg"] = 150

    result = run_cpp_engine(payload)

    assert result["matches"] == []


def test_cpp_engine_returns_valid_json_structure():
    if not Path(find_executable()).exists():
        pytest.skip("C++ matcher executable not built")

    result = run_cpp_engine(sample_payload())

    for match in result["matches"]:
        assert "ngo_id" in match
        assert "ngo_name" in match
        assert "requirement_id" in match
        assert "match_score" in match
        assert "breakdown" in match

        breakdown = match["breakdown"]

        assert "food_type" in breakdown
        assert "quantity" in breakdown
        assert "location" in breakdown
        assert "expiry" in breakdown
        assert "capacity" in breakdown