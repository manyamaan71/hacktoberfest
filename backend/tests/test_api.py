import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import (
    CandidateFile,
    CandidateTest,
    ConflictInfo,
    ContributionStep,
    InvestigationReport,
    IssueMetadata,
)
from app.services.investigation_manager import manager

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

def test_pdf_report_endpoint_returns_downloadable_pdf(monkeypatch):
    report = InvestigationReport(
        investigation_id="inv-pdf-test",
        status="completed",
        issue=IssueMetadata(
            url="https://github.com/example/project/issues/42",
            owner="example",
            repository="project",
            number=42,
            title="Fix the parser — café 🐛",
            body="The parser fails on valid input — reproduced from the issue.",
            state="open",
        ),
        summary="The parser behavior and candidate implementation file were identified.",
        uncertainties=["The root cause still needs maintainer confirmation."],
        relevant_files=[
            CandidateFile(
                path="src/parser.py",
                url="https://github.com/example/project/blob/main/src/parser.py#L10",
                line_start=10,
                line_end=14,
                symbols=["parse_input"],
                reason="Contains the parser function named in the issue.",
                evidence_type="HEURISTIC_MATCH",
            )
        ],
        relevant_tests=[
            CandidateTest(
                path="tests/test_parser.py",
                url="https://github.com/example/project/blob/main/tests/test_parser.py",
                test_functions=["test_parse_valid_input"],
                reason="Tests the related parsing behavior.",
                evidence_type="HEURISTIC_MATCH",
            )
        ],
        possible_conflicts=[
            ConflictInfo(
                type="LINKED_PR",
                severity="medium",
                title="Potentially related pull request",
                description="The issue has a linked pull request to review.",
                linked_pr_urls=["https://github.com/example/project/pull/43"],
            )
        ],
        contribution_steps=[
            ContributionStep(
                step_number=1,
                title="Inspect parser implementation",
                description="Review the identified parser and determine the failing branch.",
                action_type="inspect_file",
                target_files=["src/parser.py"],
            )
        ],
        warnings=["Repository analysis is limited to the captured snapshot."],
    )
    monkeypatch.setattr(manager, "get_report", lambda investigation_id: report)

    response = client.get("/api/investigations/inv-pdf-test/report/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "repoxray-example-project-42.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF-")
    assert b"src/parser.py" in response.content
    assert b"HEURISTIC_MATCH" in response.content
    assert b"not executed" in response.content
    assert b"/URI" in response.content

def test_pdf_report_endpoint_returns_202_until_report_is_ready(monkeypatch):
    monkeypatch.setattr(manager, "get_report", lambda investigation_id: None)
    monkeypatch.setattr(
        manager,
        "get_status",
        lambda investigation_id: type(
            "Status",
            (),
            {"status": "investigating"},
        )(),
    )

    response = client.get("/api/investigations/inv-pdf-pending/report/pdf")

    assert response.status_code == 202
    assert "still in progress" in response.json()["detail"]
