from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FoodDonation
from app.services.cpp_matching_service import run_cpp_matching

router = APIRouter(
    prefix="/matching",
    tags=["C++ Matching"],
)


@router.post("/cpp/donations/{donation_id}/run")
def run_cpp_donation_matching(
    donation_id: int,
    db: Session = Depends(get_db),
):
    donation = (
        db.query(FoodDonation)
        .filter(FoodDonation.id == donation_id)
        .first()
    )

    if not donation:
        raise HTTPException(
            status_code=404,
            detail="Donation not found",
        )

    if donation.status != "available":
        raise HTTPException(
            status_code=409,
            detail="Only available donations can be matched",
        )

    try:
        matches = run_cpp_matching(
            db,
            donation,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return {
        "donation_id": donation_id,
        "matches_found": len(matches),
        "matches": [
            {
                "match_id": match.id,
                "donation_id": match.donation_id,
                "ngo_id": match.ngo_id,
                "requirement_id": match.requirement_id,
                "match_score": match.match_score,
                "status": match.status,
            }
            for match in matches
        ],
    }