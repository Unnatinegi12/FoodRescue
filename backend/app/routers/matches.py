from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import FoodDonation, Match
from app.schemas import MatchResponse


router = APIRouter(
    tags=["Matches"],
)


@router.get(
    "/donations/{donation_id}/matches",
    response_model=list[MatchResponse],
)
def list_donation_matches(
    donation_id: int,
    db: Session = Depends(get_db),
):
    # Make sure the donation exists
    if db.get(FoodDonation, donation_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Donation {donation_id} not found",
        )

    return (
        db.query(Match)
        .options(joinedload(Match.ngo))
        .filter(Match.donation_id == donation_id)
        .order_by(
            Match.match_score.desc(),
            Match.match_id,
        )
        .all()
    )