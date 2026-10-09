import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from app.models.schemas import (
    IssueRequest, ModelStatusResponse, InvestigationStatusResponse,
    InvestigationReport
)
from app.services.github_service import parse_github_issue_url, InvalidGitHubURLError
from app.services.model_provider import GemmaModelProvider
from app.services.investigation_manager import manager
from app.config import settings

router = APIRouter(prefix="/api")

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "RepoXray API",
        "version": "1.0.0",
        "github_token_configured": bool(settings.GITHUB_TOKEN),
        "gemma_configured": bool(settings.GEMMA_API_KEY)
    }

@router.get("/model/status", response_model=ModelStatusResponse)
async def model_status():
    provider = GemmaModelProvider(
        api_key=settings.GEMMA_API_KEY,
        model=settings.GEMMA_MODEL,
        provider=settings.GEMMA_PROVIDER,
        base_url=settings.GEMMA_API_BASE_URL
    )
    configured = provider.is_configured()
    if not configured:
        return ModelStatusResponse(
            provider=settings.GEMMA_PROVIDER,
            model=settings.GEMMA_MODEL,
            configured=False,
            status="unavailable",
            message="GEMMA_API_KEY is not configured in backend environment. Operating in heuristic evidence mode."
        )

    connected, msg = await provider.check_connectivity()
    status_str = "connectivity_verified" if connected else "configured"
    return ModelStatusResponse(
        provider=settings.GEMMA_PROVIDER,
        model=settings.GEMMA_MODEL,
        configured=True,
        status=status_str,
        message=msg
    )

@router.post("/investigations", status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: IssueRequest,
    background_tasks: BackgroundTasks
):
    try:
        parse_github_issue_url(payload.issue_url)
    except InvalidGitHubURLError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    investigation_id = manager.create_investigation(payload.issue_url)
    # Trigger background task
    background_tasks.add_task(manager.run_investigation_task, investigation_id)

    return {
        "investigation_id": investigation_id,
        "status": "queued",
        "message": "Investigation started successfully."
    }

@router.get("/investigations/{investigation_id}", response_model=InvestigationStatusResponse)
async def get_investigation_status(investigation_id: str):
    res = manager.get_status(investigation_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation '{investigation_id}' not found."
        )
    return res

@router.get("/investigations/{investigation_id}/trace")
async def get_investigation_trace(investigation_id: str):
    trace = manager.get_trace(investigation_id)
    if trace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation '{investigation_id}' not found."
        )
    return {"investigation_id": investigation_id, "trace": trace}

@router.get("/investigations/{investigation_id}/report", response_model=InvestigationReport)
async def get_investigation_report(investigation_id: str):
    report = manager.get_report(investigation_id)
    if not report:
        st = manager.get_status(investigation_id)
        if not st:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation '{investigation_id}' not found."
            )
        if st.status == "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Investigation failed: {st.error_message}"
            )
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=f"Investigation is still in progress (status: {st.status})."
        )
    return report

@router.post("/investigations/{investigation_id}/cancel")
async def cancel_investigation(investigation_id: str):
    success = manager.cancel_investigation(investigation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed, failed, or non-existent investigation."
        )
    return {"investigation_id": investigation_id, "message": "Investigation cancelled."}
