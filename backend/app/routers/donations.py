from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Donor, FoodDonation
from app.schemas import (
    DonationCreate,
    DonationResponse,
    DonationUpdate,
)

router = APIRouter(
    prefix="/donations",
    tags=["Donations"],
)


def get_donation_or_404(
    db: Session,
    donation_id: int,
) -> FoodDonation:

    donation = db.get(FoodDonation, donation_id)

    if donation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Donation {donation_id} not found",
        )

    return donation


@router.post(
    "",
    response_model=DonationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_donation(
    payload: DonationCreate,
    db: Session = Depends(get_db),
):
    if db.get(Donor, payload.donor_id) is None:
        raise HTTPException(
            status_code=400,
            detail=f"donor_id {payload.donor_id} does not exist",
        )

    donation = FoodDonation(
        **payload.model_dump()
    )

    db.add(donation)
    db.commit()
    db.refresh(donation)

    return donation


@router.get(
    "",
    response_model=list[DonationResponse],
)
def list_donations(
    db: Session = Depends(get_db),
):
    return (
        db.query(FoodDonation)
        .order_by(FoodDonation.donation_id)
        .all()
    )


@router.get(
    "/available",
    response_model=list[DonationResponse],
)
def list_available_donations(
    db: Session = Depends(get_db),
):
    return (
        db.query(FoodDonation)
        .filter(
            FoodDonation.status == "available",
            FoodDonation.expiry_time > datetime.now(),
        )
        .order_by(FoodDonation.expiry_time)
        .all()
    )


@router.get(
    "/{donation_id}",
    response_model=DonationResponse,
)
def get_donation(
    donation_id: int,
    db: Session = Depends(get_db),
):
    return get_donation_or_404(
        db,
        donation_id,
    )


@router.put(
    "/{donation_id}",
    response_model=DonationResponse,
)
def update_donation(
    donation_id: int,
    payload: DonationUpdate,
    db: Session = Depends(get_db),
):
    donation = get_donation_or_404(
        db,
        donation_id,
    )

    changes = payload.model_dump(
        exclude_unset=True
    )

    new_prepared = changes.get(
        "prepared_at",
        donation.prepared_at,
    )

    new_expiry = changes.get(
        "expiry_time",
        donation.expiry_time,
    )

    if new_expiry <= new_prepared:
        raise HTTPException(
            status_code=422,
            detail="expiry_time must be later than prepared_at",
        )

    for field, value in changes.items():
        setattr(donation, field, value)

    db.commit()
    db.refresh(donation)

    return donation


@router.delete(
    "/{donation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_donation(
    donation_id: int,
    db: Session = Depends(get_db),
):
    donation = get_donation_or_404(
        db,
        donation_id,
    )

    db.delete(donation)
    db.commit()