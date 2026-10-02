from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_donations():
    response = client.get("/donations")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_donation_by_id():
    response = client.get("/donations/1")

    assert response.status_code == 200
    assert response.json()["donation_id"] == 1


def test_nonexistent_donation_returns_404():
    response = client.get("/donations/999999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_available_donations_are_unexpired():
    response = client.get("/donations/available")

    assert response.status_code == 200

    for donation in response.json():
        assert donation["status"] == "available"
        assert (
            datetime.fromisoformat(donation["expiry_time"])
            > datetime.now()
        )


def test_create_donation_then_clean_up():
    now = datetime.now().replace(microsecond=0)

    payload = {
        "donor_id": 1,
        "food_type": "cooked_meals",
        "description": "pytest donation",
        "dietary_type": "veg",
        "quantity_meals": 25,
        "quantity_kg": 10.5,
        "pickup_address": "12 Example Marg, C-Scheme",
        "city": "Jaipur",
        "latitude": 26.9124,
        "longitude": 75.7873,
        "prepared_at": (
            now - timedelta(hours=1)
        ).isoformat(),
        "expiry_time": (
            now + timedelta(hours=4)
        ).isoformat(),
    }

    response = client.post(
        "/donations",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()
    donation_id = body["donation_id"]

    try:
        assert body["status"] == "available"
        assert body["quantity_meals"] == 25
    finally:
        delete_response = client.delete(
            f"/donations/{donation_id}"
        )

        assert delete_response.status_code == 204

    assert (
        client.get(
            f"/donations/{donation_id}"
        ).status_code
        == 404
    )


def test_create_donation_rejects_bad_input():
    now = datetime.now().replace(microsecond=0)

    payload = {
        "donor_id": 1,
        "food_type": "cooked_meals",
        "dietary_type": "veg",
        "quantity_meals": 0,
        "pickup_address": "x",
        "city": "Jaipur",
        "latitude": 26.9,
        "longitude": 75.8,
        "prepared_at": now.isoformat(),
        "expiry_time": (
            now - timedelta(hours=1)
        ).isoformat(),
    }

    response = client.post(
        "/donations",
        json=payload,
    )

    assert response.status_code == 422


def test_list_ngos():
    response = client.get("/ngos")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_ngo_requirements():
    response = client.get(
        "/ngos/1/requirements"
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1

    assert all(
        requirement["ngo_id"] == 1
        for requirement in response.json()
    )


def test_requirements_for_missing_ngo_returns_404():
    response = client.get(
        "/ngos/999999/requirements"
    )

    assert response.status_code == 404


def test_donation_matches_sorted_by_score_desc():
    response = client.get(
        "/donations/1/matches"
    )

    assert response.status_code == 200

    scores = [
        match["match_score"]
        for match in response.json()
    ]

    assert len(scores) >= 1
    assert scores == sorted(
        scores,
        reverse=True,
    )