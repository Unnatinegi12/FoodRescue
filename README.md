# FoodRescue

FoodRescue is an AI-powered food redistribution platform designed to reduce food wastage by connecting organizations with surplus food to NGOs that need it.

The system allows donors to provide information about surplus food such as food type, quantity, location, and expiry time. NGOs can specify their food requirements and capacity.

The project uses SQL for structured data management, a Python matching engine that will later be integrated with C++, and a RAG-based GenAI pipeline for grounded food-safety and redistribution recommendations.

## Tech Stack

- Frontend: React
- Backend: FastAPI
- Database: MySQL
- Matching Engine: Python → C++
- GenAI: LLM + RAG
- Vector Database: To be added
- Version Control: Git & GitHub

## Current Features

### Phase 1 — FastAPI Setup

- Basic FastAPI application
- Health check endpoint
- Project structure

### Phase 2 — MySQL Database

- MySQL database schema
- Users and role-based profiles
- Donor management
- NGO management
- Food donation records
- NGO food requirements
- Donation-NGO matching records
- Foreign keys and constraints
- Seed data for testing

### Phase 3 — Donation and NGO APIs

- Donation CRUD APIs
- NGO APIs
- NGO requirement APIs
- Donation availability endpoint
- Donation-NGO match retrieval
- Pydantic request and response validation
- SQLAlchemy integration with MySQL
- API tests using pytest

### Phase 4 — Food Donation Matching Engine

For a donation, the system evaluates every NGO with an open requirement for the same food type.

Matching is **deterministic** (no ML or LLM): unsuitable NGOs are filtered out, while suitable NGOs receive a **weighted score from 0–100** and are ranked from highest to lowest score.

Results are stored in the MySQL `matches` table. If matching is run again for the same donation, existing matches are updated instead of creating duplicates.

| Factor | Points |
|---|---:|
| Food type match | 40 |
| Quantity suitability | 20 |
| Same city | 20 |
| Time left before expiry | 10 |
| NGO capacity fit | 10 |
| **Total** | **100** |

NGOs are rejected if:

- The food type does not match the requirement.
- The donation exceeds the NGO's capacity.
- A non-vegetarian donation is matched with an NGO that does not accept non-vegetarian food.
- The food would expire before the NGO could collect it.

The scoring logic is implemented in:

`backend/app/matching_engine/scoring.py`

The Python implementation is designed so that the matching logic can later be connected to or reimplemented in C++.

#### Matching APIs

```text
POST /matching/donations/{id}/run
GET  /matching/donations/{id}