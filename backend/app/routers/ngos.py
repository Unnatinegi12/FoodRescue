from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import NGO, NGORequirement
from app.schemas import NGOResponse, RequirementResponse


router = APIRouter(
    prefix="/ngos",
    tags=["NGOs"],
)


def get_ngo_or_404(
    db: Session,
    ngo_id: int,
) -> NGO:

    ngo = db.get(NGO, ngo_id)

    if ngo is None:
        raise HTTPException(
            status_code=404,
            detail=f"NGO {ngo_id} not found",
        )

    return ngo


@router.get(
    "",
    response_model=list[NGOResponse],
)
def list_ngos(
    db: Session = Depends(get_db),
):
    return (
        db.query(NGO)
        .order_by(NGO.ngo_id)
        .all()
    )


@router.get(
    "/{ngo_id}",
    response_model=NGOResponse,
)
def get_ngo(
    ngo_id: int,
    db: Session = Depends(get_db),
):
    return get_ngo_or_404(
        db,
        ngo_id,
    )


@router.get(
    "/{ngo_id}/requirements",
    response_model=list[RequirementResponse],
)
def list_ngo_requirements(
    ngo_id: int,
    db: Session = Depends(get_db),
):
    # Make sure the NGO actually exists
    get_ngo_or_404(db, ngo_id)

    return (
        db.query(NGORequirement)
        .filter(NGORequirement.ngo_id == ngo_id)
        .order_by(NGORequirement.requirement_id)
        .all()
    )