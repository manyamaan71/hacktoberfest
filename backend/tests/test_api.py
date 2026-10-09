import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "RepoXray API"

def test_model_status_endpoint():
    res = client.get("/api/model/status")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data
    assert "status" in data

def test_create_investigation_invalid_url():
    res = client.post("/api/investigations", json={"issue_url": "https://github.com/owner/repo/pull/42"})
    assert res.status_code == 400
    assert "Pull Request URL" in res.json()["detail"]

def test_create_investigation_valid_url():
    res = client.post("/api/investigations", json={"issue_url": "https://github.com/fastapi/fastapi/issues/1000"})
    assert res.status_code == 201
    data = res.json()
    assert "investigation_id" in data
    assert data["status"] == "queued"
