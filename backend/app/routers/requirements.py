from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import NGO, NGORequirement
from app.schemas import (
    RequirementCreate,
    RequirementResponse,
    RequirementUpdate,
)


router = APIRouter(
    tags=["Requirements"],
)


def get_requirement_or_404(
    db: Session,
    requirement_id: int,
) -> NGORequirement:

    requirement = db.get(
        NGORequirement,
        requirement_id,
    )

    if requirement is None:
        raise HTTPException(
            status_code=404,
            detail=f"Requirement {requirement_id} not found",
        )

    return requirement


@router.post(
    "/ngos/{ngo_id}/requirements",
    response_model=RequirementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_requirement(
    ngo_id: int,
    payload: RequirementCreate,
    db: Session = Depends(get_db),
):
    if db.get(NGO, ngo_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"NGO {ngo_id} not found",
        )

    requirement = NGORequirement(
        ngo_id=ngo_id,
        **payload.model_dump(),
    )

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    return requirement


@router.get(
    "/requirements",
    response_model=list[RequirementResponse],
)
def list_requirements(
    db: Session = Depends(get_db),
):
    return (
        db.query(NGORequirement)
        .order_by(NGORequirement.requirement_id)
        .all()
    )


@router.get(
    "/requirements/{requirement_id}",
    response_model=RequirementResponse,
)
def get_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
):
    return get_requirement_or_404(
        db,
        requirement_id,
    )


@router.put(
    "/requirements/{requirement_id}",
    response_model=RequirementResponse,
)
def update_requirement(
    requirement_id: int,
    payload: RequirementUpdate,
    db: Session = Depends(get_db),
):
    requirement = get_requirement_or_404(
        db,
        requirement_id,
    )

    changes = payload.model_dump(
        exclude_unset=True
    )

    for field, value in changes.items():
        setattr(requirement, field, value)

    db.commit()
    db.refresh(requirement)

    return requirement


@router.delete(
    "/requirements/{requirement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
):
    requirement = get_requirement_or_404(
        db,
        requirement_id,
    )

    db.delete(requirement)
    db.commit()