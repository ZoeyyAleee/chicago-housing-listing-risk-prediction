from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_latest_prediction():
    response = client.get("/predict/latest")
    body = response.json()

    assert response.status_code == 200
    assert "period" in body
    assert isinstance(body["period"], str)
    assert isinstance(body["predicted_risk_score"], (int, float))
    assert body["risk_level"] in {"High", "Low"}


