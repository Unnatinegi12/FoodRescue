from sqlalchemy.orm import Session

from app.models import FoodDonation, Match, NGO, NGORequirement
from app.services.cpp_matcher import run_cpp_engine


def build_cpp_payload(
    donation: FoodDonation,
    ngos: list[NGO],
    requirements: list[NGORequirement],
) -> dict:
    return {
        "donation": {
            "id": donation.id,
            "food_type": donation.food_type,
            "quantity_kg": float(donation.quantity_kg),
            "city": donation.city,
            "expiry_time": donation.expiry_time.isoformat(),
            "is_vegetarian": donation.is_vegetarian,
        },
        "ngos": [
            {
                "id": ngo.id,
                "name": ngo.name,
                "city": ngo.city,
                "capacity_kg": float(ngo.capacity_kg),
                "accepts_non_veg": ngo.accepts_non_veg,
            }
            for ngo in ngos
        ],
        "requirements": [
            {
                "id": requirement.id,
                "ngo_id": requirement.ngo_id,
                "food_type": requirement.food_type,
                "required_meals": float(requirement.required_meals),
            }
            for requirement in requirements
        ],
    }


def run_cpp_matching(
    db: Session,
    donation: FoodDonation,
):
    ngos = db.query(NGO).all()

    requirements = (
        db.query(NGORequirement)
        .filter(NGORequirement.status == "open")
        .all()
    )

    payload = build_cpp_payload(
        donation,
        ngos,
        requirements,
    )

    result = run_cpp_engine(payload)

    matches = []

    for item in result["matches"]:
        match = (
            db.query(Match)
            .filter(
                Match.donation_id == donation.id,
                Match.ngo_id == item["ngo_id"],
            )
            .first()
        )

        if match:
            match.requirement_id = item["requirement_id"]
            match.match_score = item["match_score"]
        else:
            match = Match(
                donation_id=donation.id,
                ngo_id=item["ngo_id"],
                requirement_id=item["requirement_id"],
                match_score=item["match_score"],
                status="pending",
            )
            db.add(match)

        matches.append(match)

    db.commit()

    for match in matches:
        db.refresh(match)

    return matches