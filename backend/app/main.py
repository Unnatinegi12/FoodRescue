import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.routers import donations, matches, matching, matching_cpp, ngos, requirements
from app.routers import rag


logger = logging.getLogger("foodrescue")


tags_metadata = [
    {
        "name": "Donations",
        "description": "Surplus food listings from donors",
    },
    {
        "name": "NGOs",
        "description": "Organizations that receive food",
    },
    {
        "name": "Requirements",
        "description": "What food each NGO needs",
    },
    {
        "name": "Matches",
        "description": "Stored donation-to-NGO matches",
    },
    {"name": "Matching", "description": "Run the matching engine and read ranked results"},
]


app = FastAPI(
    title="FoodRescue API",
    description="AI-powered food redistribution system",
   version="0.6.0",
    openapi_tags=tags_metadata,
)


# Register API routers
app.include_router(donations.router)
app.include_router(ngos.router)
app.include_router(requirements.router)
app.include_router(matches.router)
app.include_router(matching.router)
app.include_router(matching_cpp.router)
app.include_router(rag.router)


# Handle database constraint errors
@app.exception_handler(IntegrityError)
async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
):
    logger.error(
        "Integrity error on %s %s: %s",
        request.method,
        request.url.path,
        exc.orig,
    )

    return JSONResponse(
        status_code=409,
        content={
            "detail": "Request conflicts with existing data or violates a database rule."
        },
    )


# Handle other database errors
@app.exception_handler(SQLAlchemyError)
async def database_error_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    logger.error(
        "Database error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "A database error occurred."
        },
    )


@app.get("/")
def root():
    return {
        "message": "Welcome to FoodRescue API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }