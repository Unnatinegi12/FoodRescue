from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Donor(Base):
    __tablename__ = "donors"

    donor_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(150), nullable=False)
    donor_type = Column(String(30), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    donations = relationship("FoodDonation", back_populates="donor")


class NGO(Base):
    __tablename__ = "ngos"

    ngo_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(150), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    capacity_meals = Column(Integer, nullable=False)
    accepts_non_veg = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    requirements = relationship(
        "NGORequirement",
        back_populates="ngo",
        passive_deletes=True,
    )


class FoodDonation(Base):
    __tablename__ = "food_donations"

    donation_id = Column(Integer, primary_key=True)
    donor_id = Column(
        Integer,
        ForeignKey("donors.donor_id"),
        nullable=False,
    )
    food_type = Column(String(30), nullable=False)
    description = Column(String(255), nullable=True)
    dietary_type = Column(String(10), nullable=False)
    quantity_meals = Column(Integer, nullable=False)
    quantity_kg = Column(Numeric(8, 2), nullable=True)
    pickup_address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    prepared_at = Column(DateTime, nullable=False)
    expiry_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, server_default="available")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    donor = relationship("Donor", back_populates="donations")


class NGORequirement(Base):
    __tablename__ = "ngo_requirements"

    requirement_id = Column(Integer, primary_key=True)
    ngo_id = Column(
        Integer,
        ForeignKey("ngos.ngo_id"),
        nullable=False,
    )
    food_type = Column(String(30), nullable=False)
    required_meals = Column(Integer, nullable=False)
    priority = Column(String(10), nullable=False, server_default="medium")
    status = Column(String(15), nullable=False, server_default="open")
    created_at = Column(DateTime, server_default=func.now())

    ngo = relationship("NGO", back_populates="requirements")


class Match(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True)
    donation_id = Column(
        Integer,
        ForeignKey("food_donations.donation_id"),
        nullable=False,
    )
    ngo_id = Column(
        Integer,
        ForeignKey("ngos.ngo_id"),
        nullable=False,
    )
    match_score = Column(Numeric(5, 2), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    ngo = relationship("NGO")

    @property
    def ngo_name(self):
        return self.ngo.name