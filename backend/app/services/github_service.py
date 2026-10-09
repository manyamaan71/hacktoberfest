import re
import os
import zipfile
import io
import httpx
from typing import Tuple, Dict, Any, List, Optional
from app.models.schemas import IssueMetadata, ConflictInfo

GITHUB_URL_REGEX = re.compile(
    r"^https?://(?:www\.)?github\.com/([a-zA-Z0-9_\.-]+)/([a-zA-Z0-9_\.-]+)/issues/(\d+)/?$",
    re.IGNORECASE
)

PR_URL_REGEX = re.compile(
    r"^https?://(?:www\.)?github\.com/([a-zA-Z0-9_\.-]+)/([a-zA-Z0-9_\.-]+)/pull/(\d+)/?$",
    re.IGNORECASE
)

class GitHubServiceError(Exception):
    pass

class InvalidGitHubURLError(GitHubServiceError):
    pass

class GitHubAPIError(GitHubServiceError):
    pass

def parse_github_issue_url(url: str) -> Tuple[str, str, int]:
    url = url.strip()
    if PR_URL_REGEX.match(url):
        raise InvalidGitHubURLError(
            "The URL provided is a Pull Request URL. RepoXray requires a GitHub Issue URL (e.g. https://github.com/owner/repo/issues/123)."
        )
    
    match = GITHUB_URL_REGEX.match(url)
    if not match:
        raise InvalidGitHubURLError(
            "Invalid GitHub Issue URL format. Supported format: https://github.com/owner/repository/issues/123"
        )
    
    owner, repo, number_str = match.groups()
    return owner, repo, int(number_str)

def get_headers(github_token: Optional[str] = None) -> Dict[str, str]:
    headers = {
        "User-Agent": "RepoXray-AI-Agent/1.0",
        "Accept": "application/vnd.github.v3+json"
    }
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    return headers

def _github_api_error_message(response: httpx.Response, github_token: Optional[str]) -> str:
    try:
        message = response.json().get("message", "")
    except ValueError:
        message = ""

    message = message if isinstance(message, str) else ""
    is_rate_limited = (
        response.status_code == 429
        or response.headers.get("X-RateLimit-Remaining") == "0"
        or "rate limit" in message.lower()
    )

    if response.status_code == 401:
        return (
            "GitHub rejected GITHUB_TOKEN. Check that the token is valid and not expired, "
            "then restart the backend."
        )

    if is_rate_limited:
        if github_token:
            return (
                "GitHub rate limit exceeded for the configured token. Wait for the limit "
                "to reset before trying again."
            )
        return (
            "GitHub's unauthenticated API rate limit was exceeded. Set GITHUB_TOKEN in "
            "backend/.env and restart the backend."
        )

    if response.status_code == 403:
        return (
            "GitHub denied access to this repository or issue. Check that the repository "
            "is public, or that GITHUB_TOKEN has access to it, then restart the backend."
        )

    return f"GitHub API error ({response.status_code}): {message or response.text}"

async def fetch_issue_metadata(
    owner: str,
    repo: str,
    issue_number: int,
    github_token: Optional[str] = None
) -> IssueMetadata:
    headers = get_headers(github_token)
    issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(issue_url, headers=headers)
        if res.status_code == 404:
            raise GitHubAPIError(f"Issue #{issue_number} or repository {owner}/{repo} not found on GitHub.")
        elif res.status_code != 200:
            raise GitHubAPIError(_github_api_error_message(res, github_token))
        
        data = res.json()
        if "pull_request" in data:
            raise InvalidGitHubURLError(f"Issue #{issue_number} is actually a Pull Request on GitHub. Please submit a standard issue URL.")
        
        # Fetch repository commit SHA (HEAD of default branch)
        commit_sha = None
        repo_res = await client.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
        if repo_res.status_code == 200:
            repo_data = repo_res.json()
            default_branch = repo_data.get("default_branch", "main")
            branch_res = await client.get(f"https://api.github.com/repos/{owner}/{repo}/branches/{default_branch}", headers=headers)
            if branch_res.status_code == 200:
                commit_sha = branch_res.json().get("commit", {}).get("sha")

        labels = [label["name"] for label in data.get("labels", []) if isinstance(label, dict) and "name" in label]
        assignee = data.get("assignee", {}).get("login") if data.get("assignee") else None
        
        return IssueMetadata(
            url=data.get("html_url", f"https://github.com/{owner}/{repo}/issues/{issue_number}"),
            owner=owner,
            repository=repo,
            number=issue_number,
            title=data.get("title", ""),
            body=data.get("body", "") or "",
            state=data.get("state", "open"),
            labels=labels,
            assignee=assignee,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            commit_sha=commit_sha
        )

async def check_linked_prs(
    owner: str,
    repo: str,
    issue_number: int,
    github_token: Optional[str] = None
) -> List[Dict[str, Any]]:
    headers = get_headers(github_token)
    linked_prs = []
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Check issue timeline for cross-referenced PRs
        timeline_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/timeline"
        headers_timeline = {**headers, "Accept": "application/vnd.github.mockingbird-preview+json"}
        res = await client.get(timeline_url, headers=headers_timeline)
        if res.status_code == 200:
            events = res.json()
            for event in events:
                if isinstance(event, dict):
                    event_type = event.get("event")
                    if event_type in ("cross-referenced", "referenced", "connected"):
                        source = event.get("source", {})
                        issue_info = source.get("issue", {})
                        if issue_info.get("pull_request"):
                            linked_prs.append({
                                "url": issue_info.get("html_url"),
                                "number": issue_info.get("number"),
                                "title": issue_info.get("title"),
                                "state": issue_info.get("state")
                            })
        
        # Fallback search query for PRs referencing issue number
        if not linked_prs:
            search_url = f"https://api.github.com/search/issues?q=repo:{owner}/{repo}+type:pr+{issue_number}"
            search_res = await client.get(search_url, headers=headers)
            if search_res.status_code == 200:
                items = search_res.json().get("items", [])
                for item in items:
                    linked_prs.append({
                        "url": item.get("html_url"),
                        "number": item.get("number"),
                        "title": item.get("title"),
                        "state": item.get("state")
                    })

    # Deduplicate by URL
    seen = set()
    unique_prs = []
    for pr in linked_prs:
        if pr.get("url") and pr["url"] not in seen:
            seen.add(pr["url"])
            unique_prs.append(pr)
            
    return unique_prs

async def download_and_extract_repo(
    owner: str,
    repo: str,
    target_dir: str,
    github_token: Optional[str] = None
) -> str:
    """
    Downloads repository archive zip from GitHub safely and extracts it inside target_dir.
    Returns path to the extracted repository root directory.
    """
    headers = get_headers(github_token)
    zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        res = await client.get(zip_url, headers=headers)
        if res.status_code != 200:
            # Fallback to direct codeload zip
            alt_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
            res = await client.get(alt_url)
            if res.status_code != 200:
                alt_url_master = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
                res = await client.get(alt_url_master)
                if res.status_code != 200:
                    raise GitHubAPIError(f"Failed to download repository zipball for {owner}/{repo} (status {res.status_code}).")

        zip_content = res.content
        
    os.makedirs(target_dir, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
        # Security: Prevent zip slip path traversal
        for member in zf.infolist():
            filename = member.filename
            # Resolve destination path
            dest_path = os.path.abspath(os.path.join(target_dir, filename))
            if not dest_path.startswith(os.path.abspath(target_dir)):
                raise GitHubAPIError(f"Security error: Attempted zip path traversal in file {filename}")
        
        zf.extractall(target_dir)

    # Find the extracted root directory (usually owner-repo-commit_sha/)
    subdirs = [os.path.join(target_dir, d) for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
    if subdirs:
        return subdirs[0]
    return target_dir
