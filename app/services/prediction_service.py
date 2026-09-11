from pathlib import Path

import joblib
import pandas as pd

from app.schemas import PredictionResponse


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "chicago_housing_engineered.csv"


def get_latest_prediction() -> PredictionResponse:
    """Return a listing-risk prediction for the latest engineered month."""

    model = joblib.load(MODELS_DIR / "linear_regression.pkl")
    scaler = joblib.load(MODELS_DIR / "scaler.pkl")
    feature_columns = joblib.load(MODELS_DIR / "feature_cols.pkl")

    df = pd.read_csv(DATA_PATH)
    latest_row = df.sort_values("PERIOD_BEGIN").iloc[[-1]]

    latest_features = latest_row[feature_columns]
    scaled_features = scaler.transform(latest_features)
    predicted_score = float(model.predict(scaled_features)[0])

    period = pd.to_datetime(latest_row["PERIOD_BEGIN"].iloc[0]).strftime("%Y-%m-%d")
    risk_level = "High" if predicted_score > 0 else "Low"

    return PredictionResponse(
        period=period,
        predicted_risk_score=round(predicted_score, 3),
        risk_level=risk_level,
    )