from fastapi.testclient import TestClient
from src.server.main import app

client = TestClient(app)

def test_rate_minimal():
    resp = client.post("/rate", json={"ingredients_text":"sugar, cocoa, milk solids", "nutrition_raw": {"sugars": 25, "salt": 1.7, "saturated fat": 8, "protein": 9, "fiber": 2}})
    assert resp.status_code == 200
    data = resp.json()
    # Either a HITL pause (if input considered low) or a scoring payload
    assert data.get("action") == "PAUSE_HITL" or "scoring" in data