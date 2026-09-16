from fastapi.testclient import TestClient
from app.api.main import app
c=TestClient(app)
def test_health():assert c.get("/health").json()["status"]=="ok"
def test_risk():
    r=c.get("/risk/SUP-0100");assert r.status_code==200;assert r.json()["validation"]["passed"];assert r.json()["evidence"]
def test_404():assert c.get("/risk/SUP-9999").status_code==404
