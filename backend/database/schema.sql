-- =====================================================================
-- FoodRescue database schema (MySQL 8.0.16+)
-- Re-runnable in development: drops and recreates all tables.
-- WARNING: running this deletes existing FoodRescue data.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS foodrescue
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE foodrescue;

-- Drop in reverse dependency order (children before parents)
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS ngo_requirements;
DROP TABLE IF EXISTS food_donations;
DROP TABLE IF EXISTS ngos;
DROP TABLE IF EXISTS donors;
DROP TABLE IF EXISTS users;

-- ---------------------------------------------------------------------
-- users: login identity only
-- ---------------------------------------------------------------------
CREATE TABLE users (
  user_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
  email         VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('donor', 'ngo') NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- donors: organizations that give surplus food (1:1 with a user)
-- ---------------------------------------------------------------------
CREATE TABLE donors (
  donor_id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id       INT UNSIGNED NOT NULL,
  name          VARCHAR(150) NOT NULL,
  donor_type    ENUM(
    'restaurant',
    'canteen',
    'hostel',
    'event_organizer',
    'other'
  ) NOT NULL,
  contact_phone VARCHAR(20) NOT NULL,
  address       VARCHAR(255) NOT NULL,
  city          VARCHAR(100) NOT NULL,
  latitude      DECIMAL(9,6) NOT NULL,
  longitude     DECIMAL(9,6) NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (donor_id),

  UNIQUE KEY uq_donors_user (user_id),

  CONSTRAINT fk_donors_user
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
    ON DELETE CASCADE,

  CONSTRAINT chk_donors_geo
    CHECK (
      latitude BETWEEN -90 AND 90
      AND longitude BETWEEN -180 AND 180
    )
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- ngos: organizations that receive food (1:1 with a user)
-- capacity_meals = max meals the NGO can accept in a day
-- ---------------------------------------------------------------------
CREATE TABLE ngos (
  ngo_id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id         INT UNSIGNED NOT NULL,
  name            VARCHAR(150) NOT NULL,
  contact_phone   VARCHAR(20) NOT NULL,
  address         VARCHAR(255) NOT NULL,
  city            VARCHAR(100) NOT NULL,
  latitude        DECIMAL(9,6) NOT NULL,
  longitude       DECIMAL(9,6) NOT NULL,
  capacity_meals  INT UNSIGNED NOT NULL,
  accepts_non_veg BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (ngo_id),

  UNIQUE KEY uq_ngos_user (user_id),

  CONSTRAINT fk_ngos_user
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
    ON DELETE CASCADE,

  CONSTRAINT chk_ngos_capacity
    CHECK (capacity_meals > 0),

  CONSTRAINT chk_ngos_geo
    CHECK (
      latitude BETWEEN -90 AND 90
      AND longitude BETWEEN -180 AND 180
    )
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- food_donations: one row per surplus-food listing
-- quantity_meals is the unit used for matching; quantity_kg is optional info
-- ---------------------------------------------------------------------
CREATE TABLE food_donations (
  donation_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  donor_id       INT UNSIGNED NOT NULL,

  food_type ENUM(
    'cooked_meals',
    'bakery',
    'fruits_vegetables',
    'packaged',
    'dairy'
  ) NOT NULL,

  description    VARCHAR(255) NULL,
  dietary_type   ENUM('veg', 'non_veg') NOT NULL,

  quantity_meals INT UNSIGNED NOT NULL,
  quantity_kg    DECIMAL(8,2) NULL,

  pickup_address VARCHAR(255) NOT NULL,
  city           VARCHAR(100) NOT NULL,

  latitude       DECIMAL(9,6) NOT NULL,
  longitude      DECIMAL(9,6) NOT NULL,

  prepared_at    DATETIME NOT NULL,
  expiry_time    DATETIME NOT NULL,

  status ENUM(
    'available',
    'matched',
    'picked_up',
    'expired',
    'cancelled'
  ) NOT NULL DEFAULT 'available',

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  updated_at DATETIME NOT NULL
    DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (donation_id),

  -- Serves: "available, not-yet-expired donations, most urgent first"
  KEY idx_donations_status_expiry (status, expiry_time),

  CONSTRAINT fk_donations_donor
    FOREIGN KEY (donor_id)
    REFERENCES donors (donor_id)
    ON DELETE RESTRICT,

  CONSTRAINT chk_donations_meals
    CHECK (quantity_meals > 0),

  CONSTRAINT chk_donations_kg
    CHECK (quantity_kg IS NULL OR quantity_kg > 0),

  CONSTRAINT chk_donations_times
    CHECK (expiry_time > prepared_at),

  CONSTRAINT chk_donations_geo
    CHECK (
      latitude BETWEEN -90 AND 90
      AND longitude BETWEEN -180 AND 180
    )
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- ngo_requirements: what food an NGO currently needs (many per NGO)
-- ---------------------------------------------------------------------
CREATE TABLE ngo_requirements (
  requirement_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ngo_id         INT UNSIGNED NOT NULL,

  food_type ENUM(
    'cooked_meals',
    'bakery',
    'fruits_vegetables',
    'packaged',
    'dairy'
  ) NOT NULL,

  required_meals INT UNSIGNED NOT NULL,

  priority ENUM(
    'low',
    'medium',
    'high'
  ) NOT NULL DEFAULT 'medium',

  status ENUM(
    'open',
    'fulfilled',
    'cancelled'
  ) NOT NULL DEFAULT 'open',

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (requirement_id),

  -- Serves: "which NGOs have an open need for food type X"
  KEY idx_requirements_type_status (food_type, status),

  CONSTRAINT fk_requirements_ngo
    FOREIGN KEY (ngo_id)
    REFERENCES ngos (ngo_id)
    ON DELETE CASCADE,

  CONSTRAINT chk_requirements_meals
    CHECK (required_meals > 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- matches: junction table between donations and NGOs.
-- Will store the C++ engine's output (score 0.00 - 100.00).
-- ---------------------------------------------------------------------
CREATE TABLE matches (
  match_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  donation_id INT UNSIGNED NOT NULL,
  ngo_id      INT UNSIGNED NOT NULL,

  match_score DECIMAL(5,2) NOT NULL,

  status ENUM(
    'suggested',
    'accepted',
    'rejected',
    'completed'
  ) NOT NULL DEFAULT 'suggested',

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  updated_at DATETIME NOT NULL
    DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (match_id),

  -- Integrity: the same donation/NGO pair cannot be matched twice
  UNIQUE KEY uq_matches_donation_ngo (donation_id, ngo_id),

  -- Serves: "best-scoring NGOs for donation X"
  KEY idx_matches_donation_score (
    donation_id,
    match_score DESC
  ),

  CONSTRAINT fk_matches_donation
    FOREIGN KEY (donation_id)
    REFERENCES food_donations (donation_id)
    ON DELETE CASCADE,

  CONSTRAINT fk_matches_ngo
    FOREIGN KEY (ngo_id)
    REFERENCES ngos (ngo_id)
    ON DELETE CASCADE,

  CONSTRAINT chk_matches_score
    CHECK (match_score BETWEEN 0 AND 100)
) ENGINE=InnoDB;