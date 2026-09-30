# FoodRescue

FoodRescue is an AI-powered food redistribution platform designed to reduce food wastage by connecting organizations with surplus food to NGOs that need it.

The system allows donors to provide information about surplus food such as food type, quantity, location, and expiry time. NGOs can specify their food requirements and capacity.

The project will use SQL for structured data management, a C++ matching engine for intelligent NGO ranking, and a RAG-based GenAI pipeline for grounded food-safety and redistribution recommendations.

## Tech Stack

- Frontend: React
- Backend: FastAPI
- Database: MySQL
- Matching Engine: C++
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

## Database Structure

The main tables are:

- `users`
- `donors`
- `ngos`
- `food_donations`
- `ngo_requirements`
- `matches`

### Major Relationships

- One user → one donor or NGO profile
- One donor → many food donations
- One NGO → many food requirements
- One food donation → many possible NGO matches
- One NGO → many possible donation matches

## Project Roadmap

- [x] Phase 1 — FastAPI project setup
- [x] Phase 2 — MySQL schema and seed data
- [ ] Phase 3 — Donation and NGO APIs
- [ ] Phase 4 — Food donation matching engine
- [ ] Phase 5 — C++ matching engine integration
- [ ] Phase 6 — Food safety RAG pipeline
- [ ] Phase 7 — Grounded AI recommendations
- [ ] Phase 8 — React dashboard
- [ ] Phase 9 — Testing and validation
- [ ] Phase 10 — Documentation

## Project Structure

```text
FoodRescue/
├── backend/
│   ├── app/
│   ├── database/
│   │   ├── schema.sql
│   │   └── seed.sql
│   ├── requirements.txt
│   └── .env.example
├── matching_engine/
├── rag/
├── frontend/
├── tests/
├── docs/
├── .gitignore
├── LICENSE
└── README.md