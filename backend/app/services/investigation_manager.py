import asyncio
import uuid
import os
import shutil
import tempfile
from typing import Dict, Optional, Any
from app.models.schemas import InvestigationStatusResponse, InvestigationReport
from app.services.github_service import (
    parse_github_issue_url, fetch_issue_metadata, download_and_extract_repo,
    InvalidGitHubURLError, GitHubAPIError
)
from app.services.indexer_service import RepositoryIndexer
from app.services.model_provider import GemmaModelProvider
from app.services.agent_service import AgentService
from app.config import settings

class InvestigationState:
    def __init__(self, investigation_id: str, issue_url: str):
        self.investigation_id = investigation_id
        self.issue_url = issue_url
        self.status = "queued"  # "queued" | "indexing" | "investigating" | "completed" | "failed" | "cancelled"
        self.progress_percentage = 0
        self.current_step = "Queued for investigation"
        self.error_message: Optional[str] = None
        self.report: Optional[InvestigationReport] = None
        self.agent_service: Optional[AgentService] = None

class InvestigationManager:
    def __init__(self):
        self.investigations: Dict[str, InvestigationState] = {}

    def create_investigation(self, issue_url: str) -> str:
        investigation_id = f"inv-{uuid.uuid4().hex[:10]}"
        state = InvestigationState(investigation_id, issue_url)
        self.investigations[investigation_id] = state
        return investigation_id

    def get_status(self, investigation_id: str) -> Optional[InvestigationStatusResponse]:
        state = self.investigations.get(investigation_id)
        if not state:
            return None
        return InvestigationStatusResponse(
            investigation_id=state.investigation_id,
            status=state.status,
            progress_percentage=state.progress_percentage,
            current_step=state.current_step,
            issue_url=state.issue_url,
            error_message=state.error_message
        )

    def get_report(self, investigation_id: str) -> Optional[InvestigationReport]:
        state = self.investigations.get(investigation_id)
        if state and state.report:
            return state.report
        return None

    def get_trace(self, investigation_id: str) -> Optional[list]:
        state = self.investigations.get(investigation_id)
        if state:
            if state.report:
                return [step.model_dump() for step in state.report.agent_trace]
            elif state.agent_service:
                return [step.model_dump() for step in state.agent_service.trace]
        return []

    def cancel_investigation(self, investigation_id: str) -> bool:
        state = self.investigations.get(investigation_id)
        if state and state.status not in ("completed", "failed", "cancelled"):
            state.status = "cancelled"
            state.current_step = "Investigation cancelled by user."
            return True
        return False

    async def run_investigation_task(self, investigation_id: str):
        state = self.investigations.get(investigation_id)
        if not state:
            return

        temp_dir = tempfile.mkdtemp(prefix="repoxray_")
        try:
            # Step 1: Validate URL & Fetch Metadata
            state.status = "indexing"
            state.progress_percentage = 15
            state.current_step = "Retrieving GitHub Issue metadata..."

            owner, repo, issue_number = parse_github_issue_url(state.issue_url)
            issue_meta = await fetch_issue_metadata(
                owner=owner,
                repo=repo,
                issue_number=issue_number,
                github_token=settings.GITHUB_TOKEN
            )

            if state.status == "cancelled":
                return

            # Step 2: Download & Extract Repository safely
            state.progress_percentage = 35
            state.current_step = f"Acquiring repository snapshot for {owner}/{repo}..."
            
            extracted_path = await download_and_extract_repo(
                owner=owner,
                repo=repo,
                target_dir=temp_dir,
                github_token=settings.GITHUB_TOKEN
            )

            if state.status == "cancelled":
                return

            # Step 3: Index Repository Files
            state.progress_percentage = 50
            state.current_step = "Indexing repository files & AST symbols..."
            
            indexer = RepositoryIndexer(
                repo_root=extracted_path,
                max_files=settings.MAX_REPOSITORY_FILES,
                max_file_size=settings.MAX_FILE_SIZE_BYTES
            )
            indexer.index()

            if state.status == "cancelled":
                return

            # Step 4: Run AI / Bounded Tool Agent Investigation
            state.status = "investigating"
            state.progress_percentage = 70
            state.current_step = "Agent executing investigative tool calls..."

            model_provider = GemmaModelProvider(
                api_key=settings.GEMMA_API_KEY,
                model=settings.GEMMA_MODEL,
                provider=settings.GEMMA_PROVIDER,
                base_url=settings.GEMMA_API_BASE_URL
            )

            agent = AgentService(
                investigation_id=investigation_id,
                issue=issue_meta,
                indexer=indexer,
                model_provider=model_provider,
                github_token=settings.GITHUB_TOKEN
            )
            state.agent_service = agent

            report = await agent.run_investigation()

            if state.status == "cancelled":
                return

            # Step 5: Complete
            state.report = report
            state.status = "completed"
            state.progress_percentage = 100
            state.current_step = "Investigation completed successfully."

        except (InvalidGitHubURLError, GitHubAPIError) as e:
            state.status = "failed"
            state.error_message = str(e)
            state.current_step = f"Failed: {str(e)}"
        except Exception as e:
            state.status = "failed"
            state.error_message = f"Unexpected investigation error: {str(e)}"
            state.current_step = f"Failed: {str(e)}"
        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

manager = InvestigationManager()
