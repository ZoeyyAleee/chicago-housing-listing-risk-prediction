from fastapi import FastAPI

from app.schemas import PredictionResponse
from app.services.prediction_service import get_latest_prediction


app = FastAPI(
    title="Chicago Housing Listing Risk API",
    description="API for retrieving a listing-risk prediction from the latest engineered Chicago market data.",
    version="1.0.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/predict/latest", response_model=PredictionResponse)
def predict_latest() -> PredictionResponse:
    return get_latest_prediction()