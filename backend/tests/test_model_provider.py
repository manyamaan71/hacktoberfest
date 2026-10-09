import pytest
from unittest.mock import AsyncMock

from app.services.model_provider import GemmaModelProvider


@pytest.mark.asyncio
async def test_generate_action_formats_json_example_when_model_is_configured(monkeypatch):
    provider = GemmaModelProvider(api_key="test-api-key")
    call_model = AsyncMock(return_value='{"tool": "final_answer", "arguments": {}}')
    monkeypatch.setattr(provider, "_call_model_api", call_model)

    action = await provider.generate_action(
        issue_title="Example issue",
        issue_body="Example description",
        tool_history=[],
        available_tools_description="No tools",
    )

    assert action == {"tool": "final_answer", "arguments": {}}
    prompt = call_model.await_args.args[0]
    assert '[{"step_number": 1,' in prompt
