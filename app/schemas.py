from pydantic import BaseModel


class PredictionResponse(BaseModel):
    period: str
    predicted_risk_score: float
    risk_level: str