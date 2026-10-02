"""Loads data from MySQL, scores every candidate, ranks them, and saves to `matches`."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.matching_engine.scoring import ScoreBreakdown, score_match
from app.models import FoodDonation, Match, NGO, NGORequirement


class DonationNotFoundError(Exception):
    pass


class DonationNotMatchableError(Exception):
    pass


@dataclass
class RankedMatch:
    match: Match
    ngo: NGO
    requirement: NGORequirement
    breakdown: ScoreBreakdown


def rank_candidates(donation, requirements, now: datetime) -> list:
    """Score each requirement, drop unsuitable ones, keep the best per NGO,
    sort by score (highest first). Ties are broken by ngo_id so output is
    deterministic.
    """

    best_per_ngo = {}

    for req in requirements:
        breakdown = score_match(
            donation,
            req.ngo,
            req,
            now,
        )

        if breakdown is None:
            continue

        current = best_per_ngo.get(req.ngo_id)

        if current is None or breakdown.total > current[2].total:
            best_per_ngo[req.ngo_id] = (
                req.ngo,
                req,
                breakdown,
            )

    return sorted(
        best_per_ngo.values(),
        key=lambda c: (-c[2].total, c[0].ngo_id),
    )


def run_matching(
    db: Session,
    donation_id: int,
    now: Optional[datetime] = None,
) -> list:

    now = now or datetime.now()

    donation = db.get(
        FoodDonation,
        donation_id,
    )

    if donation is None:
        raise DonationNotFoundError(
            f"Donation {donation_id} not found"
        )

    if donation.status != "available" or donation.expiry_time <= now:
        raise DonationNotMatchableError(
            f"Donation {donation_id} is not available for matching "
            f"(status '{donation.status}', or already expired)"
        )

    # Only open requirements of the same food type can possibly match
    requirements = (
        db.query(NGORequirement)
        .options(joinedload(NGORequirement.ngo))
        .filter(
            NGORequirement.food_type == donation.food_type,
            NGORequirement.status == "open",
        )
        .all()
    )

    ranked = rank_candidates(
        donation,
        requirements,
        now,
    )

    # Upsert:
    # update the row if (donation, ngo) already exists,
    # otherwise insert
    existing = {
        m.ngo_id: m
        for m in db.query(Match)
        .filter(Match.donation_id == donation_id)
        .all()
    }

    results = []

    for ngo, req, breakdown in ranked:

        match = existing.get(ngo.ngo_id)

        if match is not None:
            match.match_score = breakdown.total

        else:
            match = Match(
                donation_id=donation_id,
                ngo_id=ngo.ngo_id,
                match_score=breakdown.total,
                status="suggested",
            )

            db.add(match)

        results.append(
            (
                match,
                ngo,
                req,
                breakdown,
            )
        )

    db.commit()

    ranked_matches = []

    for match, ngo, req, breakdown in results:
        db.refresh(match)

        ranked_matches.append(
            RankedMatch(
                match,
                ngo,
                req,
                breakdown,
            )
        )

    return ranked_matches


def get_stored_matches(
    db: Session,
    donation_id: int,
) -> list:
    """Read saved matches, best score first.
    Raises DonationNotFoundError if no such donation.
    """

    if db.get(FoodDonation, donation_id) is None:
        raise DonationNotFoundError(
            f"Donation {donation_id} not found"
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