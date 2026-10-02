from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.matching_engine import scoring
from app.matching_engine.scoring import score_match
from app.models import Match


client = TestClient(app)

NOW = datetime(2026, 10, 1, 12, 0, 0)


# =============== Unit tests: pure scoring, no database ===============


def case(donation=None, ngo=None, requirement=None):
    d = dict(
        food_type="cooked_meals",
        dietary_type="veg",
        quantity_meals=100,
        city="Jaipur",
        expiry_time=NOW + timedelta(hours=10),
    )

    n = dict(
        city="Jaipur",
        capacity_meals=300,
        accepts_non_veg=True,
    )

    r = dict(
        food_type="cooked_meals",
        required_meals=100,
    )

    d.update(donation or {})
    n.update(ngo or {})
    r.update(requirement or {})

    return score_match(
        SimpleNamespace(**d),
        SimpleNamespace(**n),
        SimpleNamespace(**r),
        NOW,
    )


def test_weights_add_up_to_100():
    assert (
        scoring.FOOD_TYPE_POINTS
        + scoring.QUANTITY_POINTS
        + scoring.LOCATION_POINTS
        + scoring.EXPIRY_POINTS
        + scoring.CAPACITY_POINTS
    ) == 100


def test_ideal_match_scores_100():
    assert case().total == 100


def test_food_type_mismatch_is_rejected():
    assert case(
        requirement={"food_type": "bakery"}
    ) is None


def test_over_capacity_is_rejected():
    assert case(
        donation={"quantity_meals": 400},
        ngo={"capacity_meals": 300},
    ) is None


def test_non_veg_rejected_by_veg_only_ngo():
    assert case(
        donation={"dietary_type": "non_veg"},
        ngo={"accepts_non_veg": False},
    ) is None


def test_smaller_donation_gets_partial_quantity_points():
    assert case(
        donation={"quantity_meals": 30}
    ).quantity == pytest.approx(6.0)


def test_location_adds_exactly_location_points():
    same = case()

    other = case(
        ngo={"city": "Mumbai"}
    )

    assert same.total - other.total == pytest.approx(
        scoring.LOCATION_POINTS
    )


def test_expiry_too_close_is_rejected():
    soon = {
        "expiry_time": NOW + timedelta(minutes=30)
    }

    assert case(donation=soon) is None

    assert case(
        donation={
            "expiry_time": NOW + timedelta(hours=3)
        },
        ngo={
            "city": "Mumbai"
        },
    ) is None


def test_tight_expiry_gets_half_points():
    result = case(
        donation={
            "expiry_time": NOW + timedelta(hours=1, minutes=30)
        }
    )

    assert result.expiry == scoring.EXPIRY_POINTS / 2


# =============== API tests: use the development database ===============


@pytest.fixture
def make_donation():
    created = []

    def _make(**overrides):
        now = datetime.now().replace(microsecond=0)

        payload = {
            "donor_id": 1,
            "food_type": "cooked_meals",
            "description": "pytest matching",
            "dietary_type": "veg",
            "quantity_meals": 60,
            "pickup_address": "12 Example Marg, C-Scheme",
            "city": "Jaipur",
            "latitude": 26.9124,
            "longitude": 75.7873,
            "prepared_at": (
                now - timedelta(hours=1)
            ).isoformat(),
            "expiry_time": (
                now + timedelta(hours=10)
            ).isoformat(),
        }

        payload.update(overrides)

        r = client.post(
            "/donations",
            json=payload,
        )

        assert r.status_code == 201, r.text

        created.append(
            r.json()["donation_id"]
        )

        return r.json()

    yield _make

    for donation_id in created:
        client.delete(
            f"/donations/{donation_id}"
        )


def run(donation):
    r = client.post(
        f"/matching/donations/{donation['donation_id']}/run"
    )

    assert r.status_code == 200, r.text

    return r.json()


def test_run_matching_for_valid_donation(make_donation):
    d = make_donation()

    body = run(d)

    assert body["donation_id"] == d["donation_id"]

    assert body["matches_found"] == len(
        body["matches"]
    ) >= 1

    for m in body["matches"]:
        assert 0 <= m["match_score"] <= 100
        assert m["status"] == "suggested"
        assert m["ngo_name"]

        assert set(m["breakdown"]) == {
            "food_type",
            "quantity",
            "location",
            "expiry",
            "capacity",
        }


def test_matches_sorted_by_score_descending(make_donation):
    d = make_donation()

    scores = [
        m["match_score"]
        for m in run(d)["matches"]
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )

    stored = client.get(
        f"/matching/donations/{d['donation_id']}"
    ).json()

    stored_scores = [
        m["match_score"]
        for m in stored
    ]

    assert stored_scores == sorted(
        stored_scores,
        reverse=True,
    )


def test_food_type_mismatch_is_not_matched(make_donation):
    bakery_ngos = {
        r["ngo_id"]
        for r in client.get(
            "/requirements"
        ).json()
        if r["food_type"] == "bakery"
        and r["status"] == "open"
    }

    matched = {
        m["ngo_id"]
        for m in run(
            make_donation(food_type="bakery")
        )["matches"]
    }

    assert matched, (
        "expected at least one NGO "
        "with an open bakery need"
    )

    assert matched <= bakery_ngos


def test_over_capacity_ngos_are_filtered_out(make_donation):
    capacity = {
        n["ngo_id"]: n["capacity_meals"]
        for n in client.get(
            "/ngos"
        ).json()
    }

    matched = {
        m["ngo_id"]
        for m in run(
            make_donation(quantity_meals=400)
        )["matches"]
    }

    assert matched, (
        "expected at least one NGO "
        "able to take 400 meals"
    )

    assert all(
        capacity[i] >= 400
        for i in matched
    )

    assert any(
        c < 400
        for c in capacity.values()
    )


def test_location_affects_score(make_donation):
    local = {
        m["ngo_id"]: m["match_score"]
        for m in run(
            make_donation(city="Jaipur")
        )["matches"]
    }

    remote = {
        m["ngo_id"]: m["match_score"]
        for m in run(
            make_donation(city="Mumbai")
        )["matches"]
    }

    common = set(local) & set(remote)

    assert common

    for ngo_id in common:
        assert (
            local[ngo_id] - remote[ngo_id]
            == pytest.approx(
                scoring.LOCATION_POINTS
            )
        )


def test_running_twice_creates_no_duplicates(make_donation):
    d = make_donation()

    first = run(d)
    second = run(d)

    assert sorted(
        m["match_id"]
        for m in first["matches"]
    ) == sorted(
        m["match_id"]
        for m in second["matches"]
    )

    stored = client.get(
        f"/matching/donations/{d['donation_id']}"
    ).json()

    assert len(stored) == len(
        first["matches"]
    )

    assert len({
        m["ngo_id"]
        for m in stored
    }) == len(stored)


def test_rerun_restores_score_but_keeps_status(make_donation):
    d = make_donation()

    target = run(d)["matches"][0]

    db = SessionLocal()

    try:
        row = db.get(
            Match,
            target["match_id"]
        )

        row.match_score = 1
        row.status = "accepted"

        db.commit()

    finally:
        db.close()

    again = next(
        m
        for m in run(d)["matches"]
        if m["match_id"] == target["match_id"]
    )

    assert again["match_score"] == target["match_score"]

    assert again["status"] == "accepted"


def test_get_stored_matches(make_donation):
    d = make_donation()

    ran = run(d)

    stored = client.get(
        f"/matching/donations/{d['donation_id']}"
    )

    assert stored.status_code == 200

    assert [
        m["match_id"]
        for m in stored.json()
    ] == [
        m["match_id"]
        for m in ran["matches"]
    ]


def test_nonexistent_donation_returns_404():
    assert client.post(
        "/matching/donations/999999/run"
    ).status_code == 404

    assert client.get(
        "/matching/donations/999999"
    ).status_code == 404


def test_cancelled_donation_cannot_be_matched(make_donation):
    d = make_donation()

    assert client.put(
        f"/donations/{d['donation_id']}",
        json={"status": "cancelled"},
    ).status_code == 200

    assert client.post(
        f"/matching/donations/{d['donation_id']}/run"
    ).status_code == 409