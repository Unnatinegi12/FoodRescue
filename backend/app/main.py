from fastapi import FastAPI

app = FastAPI(
    title="FoodRescue API",
    description="AI-powered food redistribution system",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Welcome to FoodRescue API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}