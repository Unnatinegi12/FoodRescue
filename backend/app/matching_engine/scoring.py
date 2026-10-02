"""Pure scoring rules: no database, no FastAPI.
Every rule is deterministic, so this file can later be ported to C++ line by line.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ---- Weights (must add up to 100) ----
FOOD_TYPE_POINTS = 40
QUANTITY_POINTS = 20
LOCATION_POINTS = 20
EXPIRY_POINTS = 10
CAPACITY_POINTS = 10


# ---- Simple assumptions ----
PICKUP_HOURS_SAME_CITY = 1
PICKUP_HOURS_OTHER_CITY = 4
TIGHT_MARGIN_HOURS = 1
CAPACITY_COMFORT_RATIO = 0.5


@dataclass
class ScoreBreakdown:
    food_type: float
    quantity: float
    location: float
    expiry: float
    capacity: float

    @property
    def total(self) -> float:
        return round(
            self.food_type
            + self.quantity
            + self.location
            + self.expiry
            + self.capacity,
            2,
        )


def same_city(city_a: str, city_b: str) -> bool:
    return city_a.strip().lower() == city_b.strip().lower()


def quantity_points(donation_meals: int, required_meals: int) -> float:
    """Full points if the donation covers the requirement, proportional otherwise."""
    return QUANTITY_POINTS * min(donation_meals, required_meals) / required_meals


def location_points(donation_city: str, ngo_city: str) -> float:
    return LOCATION_POINTS if same_city(donation_city, ngo_city) else 0


def capacity_points(
    donation_meals: int,
    capacity_meals: int,
) -> Optional[float]:
    """None means the NGO cannot take this much food."""

    if donation_meals > capacity_meals:
        return None

    if donation_meals <= capacity_meals * CAPACITY_COMFORT_RATIO:
        return CAPACITY_POINTS

    return CAPACITY_POINTS / 2


def expiry_points(
    expiry_time: datetime,
    now: datetime,
    same_location: bool,
) -> Optional[float]:
    """None means the food would expire before the NGO could collect it."""

    hours_left = (expiry_time - now).total_seconds() / 3600

    hours_needed = (
        PICKUP_HOURS_SAME_CITY
        if same_location
        else PICKUP_HOURS_OTHER_CITY
    )

    margin = hours_left - hours_needed

    if margin <= 0:
        return None

    if margin < TIGHT_MARGIN_HOURS:
        return EXPIRY_POINTS / 2

    return EXPIRY_POINTS


def score_match(
    donation,
    ngo,
    requirement,
    now: datetime,
) -> Optional[ScoreBreakdown]:
    """Score one donation against one NGO requirement.

    Returns None if the NGO is unsuitable,
    otherwise a ScoreBreakdown with a total from 0–100.
    """

    # Hard filters
    if donation.food_type != requirement.food_type:
        return None

    if donation.dietary_type == "non_veg" and not ngo.accepts_non_veg:
        return None

    capacity = capacity_points(
        donation.quantity_meals,
        ngo.capacity_meals,
    )

    if capacity is None:
        return None

    same_location = same_city(
        donation.city,
        ngo.city,
    )

    expiry = expiry_points(
        donation.expiry_time,
        now,
        same_location,
    )

    if expiry is None:
        return None

    # Weighted score
    return ScoreBreakdown(
        food_type=FOOD_TYPE_POINTS,
        quantity=quantity_points(
            donation.quantity_meals,
            requirement.required_meals,
        ),
        location=location_points(
            donation.city,
            ngo.city,
        ),
        expiry=expiry,
        capacity=capacity,
    )