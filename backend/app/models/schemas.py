from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class IssueRequest(BaseModel):
    issue_url: str = Field(..., description="Public GitHub issue URL, e.g., https://github.com/owner/repo/issues/123")

class IssueMetadata(BaseModel):
    url: str
    owner: str
    repository: str
    number: int
    title: str
    body: Optional[str] = ""
    state: str  # "open", "closed"
    labels: List[str] = []
    assignee: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    commit_sha: Optional[str] = None

class EvidenceCategory(str):
    VERIFIED_FACT = "VERIFIED_FACT"
    HEURISTIC_MATCH = "HEURISTIC_MATCH"
    AI_INFERENCE = "AI_INFERENCE"

class CandidateFile(BaseModel):
    path: str
    url: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    symbols: List[str] = []
    reason: str
    evidence_type: str = EvidenceCategory.HEURISTIC_MATCH
    score: Optional[float] = None
    excerpt: Optional[str] = None

class CandidateTest(BaseModel):
    path: str
    url: Optional[str] = None
    test_functions: List[str] = []
    reason: str
    evidence_type: str = EvidenceCategory.HEURISTIC_MATCH
    match_type: str = "content_match"  # "filename_match" | "content_match" | "symbol_match"
    excerpt: Optional[str] = None

class ConflictInfo(BaseModel):
    type: str  # "CLOSED_ISSUE" | "ASSIGNED_CONTRIBUTOR" | "LINKED_PR" | "NO_CONFLICT" | "UNKNOWN"
    severity: str  # "high" | "medium" | "low" | "none"
    title: str
    description: str
    linked_pr_urls: List[str] = []

class ContributionStep(BaseModel):
    step_number: int
    title: str
    description: str
    action_type: str  # "inspect_file" | "run_tests" | "maintainer_question" | "setup" | "verify_behavior"
    target_files: List[str] = []
    test_command: Optional[str] = None
    completed: bool = False

class StepStatus(str):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class AgentTraceStep(BaseModel):
    step_number: int
    tool_name: str
    action_description: str
    input_summary: Dict[str, Any] = {}
    status: str = StepStatus.PENDING
    result_summary: Optional[str] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ModelStatusResponse(BaseModel):
    provider: str
    model: str
    configured: bool
    status: str  # "configured" | "connectivity_verified" | "unavailable"
    message: str

class InvestigationStatusResponse(BaseModel):
    investigation_id: str
    status: str  # "queued" | "indexing" | "investigating" | "completed" | "failed" | "cancelled"
    progress_percentage: int = 0
    current_step: Optional[str] = None
    issue_url: str
    error_message: Optional[str] = None

class InvestigationReport(BaseModel):
    investigation_id: str
    status: str  # "completed" | "failed" | "cancelled"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    issue: IssueMetadata
    summary: str
    uncertainties: List[str] = []
    relevant_files: List[CandidateFile] = []
    relevant_tests: List[CandidateTest] = []
    possible_conflicts: List[ConflictInfo] = []
    contribution_steps: List[ContributionStep] = []
    agent_trace: List[AgentTraceStep] = []
    warnings: List[str] = []
    limitations: List[str] = []
    contributing_command: Optional[str] = None

# Tool Arguments Pydantic Models for Agent Tool Validation
class SearchCodeArgs(BaseModel):
    query: str
    file_type: Optional[str] = None
    limit: Optional[int] = 5

class ReadFileArgs(BaseModel):
    path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None

class GetIssueStateArgs(BaseModel):
    investigation_id: Optional[str] = None

class FindLinkedPRsArgs(BaseModel):
    issue_number: int
    repository: str

class FindTestsArgs(BaseModel):
    query: str
    related_source_path: Optional[str] = None

class ReadContributingGuideArgs(BaseModel):
    repository: str
