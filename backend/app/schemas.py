from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, NaiveDatetime, model_validator


FoodType = Literal[
    "cooked_meals",
    "bakery",
    "fruits_vegetables",
    "packaged",
    "dairy",
]

DietaryType = Literal["veg", "non_veg"]

DonationStatus = Literal[
    "available",
    "matched",
    "picked_up",
    "expired",
    "cancelled",
]

Priority = Literal["low", "medium", "high"]

RequirementStatus = Literal[
    "open",
    "fulfilled",
    "cancelled",
]

MAX_MEALS = 1_000_000


# ---------------------------- Donations ----------------------------

class DonationCreate(BaseModel):
    donor_id: int
    food_type: FoodType
    description: Optional[str] = Field(default=None, max_length=255)
    dietary_type: DietaryType
    quantity_meals: int = Field(gt=0, le=MAX_MEALS)
    quantity_kg: Optional[float] = Field(default=None, gt=0)
    pickup_address: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    prepared_at: NaiveDatetime
    expiry_time: NaiveDatetime

    @model_validator(mode="after")
    def expiry_after_prepared(self):
        if self.expiry_time <= self.prepared_at:
            raise ValueError(
                "expiry_time must be later than prepared_at"
            )
        return self


class DonationUpdate(BaseModel):
    food_type: Optional[FoodType] = None
    description: Optional[str] = Field(
        default=None,
        max_length=255
    )
    dietary_type: Optional[DietaryType] = None
    quantity_meals: Optional[int] = Field(
        default=None,
        gt=0,
        le=MAX_MEALS
    )
    quantity_kg: Optional[float] = Field(
        default=None,
        gt=0
    )
    pickup_address: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255
    )
    city: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90
    )
    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180
    )
    prepared_at: Optional[NaiveDatetime] = None
    expiry_time: Optional[NaiveDatetime] = None
    status: Optional[DonationStatus] = None

    @model_validator(mode="after")
    def validate_update(self):
        for name in self.model_fields_set:
            if (
                getattr(self, name) is None
                and name not in ("description", "quantity_kg")
            ):
                raise ValueError(f"{name} cannot be null")

        if self.prepared_at and self.expiry_time:
            if self.expiry_time <= self.prepared_at:
                raise ValueError(
                    "expiry_time must be later than prepared_at"
                )

        return self


class DonationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    donation_id: int
    donor_id: int
    food_type: FoodType
    description: Optional[str]
    dietary_type: DietaryType
    quantity_meals: int
    quantity_kg: Optional[float]
    pickup_address: str
    city: str
    latitude: float
    longitude: float
    prepared_at: datetime
    expiry_time: datetime
    status: DonationStatus
    created_at: datetime
    updated_at: datetime


# ------------------------------- NGOs -------------------------------

class NGOResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ngo_id: int
    name: str
    contact_phone: str
    address: str
    city: str
    latitude: float
    longitude: float
    capacity_meals: int
    accepts_non_veg: bool
    created_at: datetime


# -------------------------- Requirements ----------------------------

class RequirementCreate(BaseModel):
    food_type: FoodType
    required_meals: int = Field(
        gt=0,
        le=MAX_MEALS
    )
    priority: Priority = "medium"


class RequirementUpdate(BaseModel):
    food_type: Optional[FoodType] = None
    required_meals: Optional[int] = Field(
        default=None,
        gt=0,
        le=MAX_MEALS
    )
    priority: Optional[Priority] = None
    status: Optional[RequirementStatus] = None

    @model_validator(mode="after")
    def no_nulls(self):
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class RequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    requirement_id: int
    ngo_id: int
    food_type: FoodType
    required_meals: int
    priority: Priority
    status: RequirementStatus
    created_at: datetime


# ------------------------------ Matches -----------------------------

class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_id: int
    donation_id: int
    ngo_id: int
    ngo_name: str
    match_score: float
    status: str
    created_at: datetime
    # ------------------------- Matching engine --------------------------


class ScoreBreakdownResponse(BaseModel):
    food_type: float
    quantity: float
    location: float
    expiry: float
    capacity: float


class RankedMatchResponse(BaseModel):
    match_id: int
    donation_id: int
    ngo_id: int
    ngo_name: str
    requirement_id: int
    match_score: float
    status: str
    breakdown: ScoreBreakdownResponse


class MatchRunResponse(BaseModel):
    donation_id: int
    matches_found: int
    matches: list[RankedMatchResponse]