import pytest
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock
from app.models.schemas import IssueMetadata
from app.services.indexer_service import RepositoryIndexer
from app.services.model_provider import GemmaModelProvider
from app.services.agent_service import AgentService

@pytest.mark.asyncio
async def test_agent_bounded_execution_without_credentials(monkeypatch):
    monkeypatch.setattr("app.services.model_provider.settings.GEMMA_API_KEY", "")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a sample python file
        main_py = os.path.join(tmpdir, "main.py")
        with open(main_py, "w", encoding="utf-8") as f:
            f.write("def calculate_total(): pass\n")

        indexer = RepositoryIndexer(tmpdir)
        indexer.index()

        issue = IssueMetadata(
            url="https://github.com/owner/repo/issues/1",
            owner="owner",
            repository="repo",
            number=1,
            title="Fix calculate total bug",
            body="The calculate total function raises an error.",
            state="open"
        )

        model_provider = GemmaModelProvider(api_key="") # Unconfigured
        agent = AgentService("inv-test-123", issue, indexer, model_provider)

        report = await agent.run_investigation()

        assert report.investigation_id == "inv-test-123"
        assert report.status == "completed"
        assert len(report.agent_trace) > 0
        assert len(report.relevant_files) >= 1
        assert report.relevant_files[0].path == "main.py"
        assert len(report.contribution_steps) >= 3
        # Warning about missing credentials
        assert any("Gemma 4 model credentials not configured" in w for w in report.warnings)
