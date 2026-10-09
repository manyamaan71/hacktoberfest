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
    assert isinstance(data["github_token_configured"], bool)

def test_cors_allows_vite_fallback_port():
    res = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://localhost:5174"

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
