export interface IssueMetadata {
  url: string;
  owner: string;
  repository: string;
  number: number;
  title: string;
  body: string;
  state: 'open' | 'closed';
  labels: string[];
  assignee: string | null;
  created_at?: string;
  updated_at?: string;
  commit_sha?: string | null;
}

export type EvidenceCategory = 'VERIFIED_FACT' | 'HEURISTIC_MATCH' | 'AI_INFERENCE';

export interface CandidateFile {
  path: string;
  url?: string | null;
  line_start?: number | null;
  line_end?: number | null;
  symbols: string[];
  reason: string;
  evidence_type: EvidenceCategory;
  score?: number | null;
  excerpt?: string | null;
}

export interface CandidateTest {
  path: string;
  url?: string | null;
  test_functions: string[];
  reason: string;
  evidence_type: EvidenceCategory;
  match_type: 'filename_match' | 'content_match' | 'symbol_match';
  excerpt?: string | null;
}

export interface ConflictInfo {
  type: 'CLOSED_ISSUE' | 'ASSIGNED_CONTRIBUTOR' | 'LINKED_PR' | 'NO_CONFLICT' | 'UNKNOWN';
  severity: 'high' | 'medium' | 'low' | 'none';
  title: string;
  description: string;
  linked_pr_urls?: string[];
}

export interface ContributionStep {
  step_number: number;
  title: string;
  description: string;
  action_type: 'inspect_file' | 'run_tests' | 'maintainer_question' | 'setup' | 'verify_behavior';
  target_files?: string[];
  test_command?: string | null;
  completed?: boolean;
}

export type StepStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

export interface AgentTraceStep {
  step_number: number;
  tool_name: string;
  action_description: string;
  input_summary: Record<string, unknown>;
  status: StepStatus;
  result_summary?: string | null;
  duration_ms?: number | null;
  error_message?: string | null;
  timestamp: string;
}

export interface ModelStatusResponse {
  provider: string;
  model: string;
  configured: boolean;
  status: 'configured' | 'connectivity_verified' | 'unavailable';
  message: string;
}

export interface InvestigationStatusResponse {
  investigation_id: string;
  status: 'queued' | 'indexing' | 'investigating' | 'completed' | 'failed' | 'cancelled';
  progress_percentage: number;
  current_step?: string | null;
  issue_url: string;
  error_message?: string | null;
}

export interface InvestigationReport {
  investigation_id: string;
  status: 'completed' | 'failed' | 'cancelled';
  created_at: string;
  issue: IssueMetadata;
  summary: string;
  uncertainties: string[];
  relevant_files: CandidateFile[];
  relevant_tests: CandidateTest[];
  possible_conflicts: ConflictInfo[];
  contribution_steps: ContributionStep[];
  agent_trace: AgentTraceStep[];
  warnings: string[];
  limitations: string[];
  contributing_command?: string | null;
}

export interface HistoryItem {
  id: string;
  issue_url: string;
  title: string;
  repo: string;
  timestamp: string;
  status: string;
}
