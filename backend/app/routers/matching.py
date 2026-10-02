from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.matching_engine.matcher import (
    DonationNotFoundError,
    DonationNotMatchableError,
    get_stored_matches,
    run_matching,
)
from app.schemas import (
    MatchResponse,
    MatchRunResponse,
    RankedMatchResponse,
)

router = APIRouter(
    prefix="/matching",
    tags=["Matching"],
)


@router.post(
    "/donations/{donation_id}/run",
    response_model=MatchRunResponse,
)
def run_matching_for_donation(
    donation_id: int,
    db: Session = Depends(get_db),
):
    """Score all suitable NGOs, save the results, return them ranked."""

    try:
        ranked = run_matching(
            db,
            donation_id,
        )

    except DonationNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except DonationNotMatchableError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )

    matches = [
        RankedMatchResponse(
            match_id=r.match.match_id,
            donation_id=r.match.donation_id,
            ngo_id=r.ngo.ngo_id,
            ngo_name=r.ngo.name,
            requirement_id=r.requirement.requirement_id,
            match_score=float(r.match.match_score),
            status=r.match.status,
            breakdown=asdict(r.breakdown),
        )
        for r in ranked
    ]

    return MatchRunResponse(
        donation_id=donation_id,
        matches_found=len(matches),
        matches=matches,
    )


@router.get(
    "/donations/{donation_id}",
    response_model=list[MatchResponse],
)
def get_matches_for_donation(
    donation_id: int,
    db: Session = Depends(get_db),
):
    """Stored matches, best score first."""

    try:
        return get_stored_matches(
            db,
            donation_id,
        )

    except DonationNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )