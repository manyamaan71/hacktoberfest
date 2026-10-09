import pytest
from app.services.github_service import parse_github_issue_url, InvalidGitHubURLError

def test_parse_valid_github_issue_url():
    owner, repo, number = parse_github_issue_url("https://github.com/fastapi/fastapi/issues/1234")
    assert owner == "fastapi"
    assert repo == "fastapi"
    assert number == 1234

def test_parse_valid_github_issue_url_trailing_slash():
    owner, repo, number = parse_github_issue_url("https://github.com/psf/requests/issues/5678/")
    assert owner == "psf"
    assert repo == "requests"
    assert number == 5678

def test_reject_pull_request_url():
    with pytest.raises(InvalidGitHubURLError) as excinfo:
        parse_github_issue_url("https://github.com/python/cpython/pull/999")
    assert "Pull Request URL" in str(excinfo.value)

def test_reject_invalid_host():
    with pytest.raises(InvalidGitHubURLError):
        parse_github_issue_url("https://gitlab.com/owner/repo/issues/123")

def test_reject_malformed_url():
    with pytest.raises(InvalidGitHubURLError):
        parse_github_issue_url("not-a-valid-url")
