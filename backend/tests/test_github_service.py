import pytest
import httpx

from app.services import github_service
from app.services.github_service import GitHubAPIError


class FakeAsyncClient:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return None

    async def get(self, url, headers):
        return self.response


@pytest.mark.asyncio
async def test_unauthenticated_rate_limit_gives_token_setup_instructions(monkeypatch):
    response = httpx.Response(
        403,
        headers={"X-RateLimit-Remaining": "0"},
        json={"message": "API rate limit exceeded"},
    )
    monkeypatch.setattr(
        github_service.httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response),
    )

    with pytest.raises(GitHubAPIError, match="Set GITHUB_TOKEN in backend/.env"):
        await github_service.fetch_issue_metadata("owner", "repo", 1)


@pytest.mark.asyncio
async def test_invalid_token_error_tells_user_to_check_and_restart(monkeypatch):
    response = httpx.Response(401, json={"message": "Bad credentials"})
    monkeypatch.setattr(
        github_service.httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response),
    )

    with pytest.raises(GitHubAPIError, match="valid and not expired"):
        await github_service.fetch_issue_metadata("owner", "repo", 1, "invalid-token")


@pytest.mark.asyncio
async def test_forbidden_repository_error_is_not_misreported_as_rate_limit(monkeypatch):
    response = httpx.Response(
        403,
        headers={"X-RateLimit-Remaining": "5000"},
        json={"message": "Resource not accessible by personal access token"},
    )
    monkeypatch.setattr(
        github_service.httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response),
    )

    with pytest.raises(GitHubAPIError, match="denied access"):
        await github_service.fetch_issue_metadata("owner", "repo", 1, "valid-token")
