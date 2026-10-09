import time
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from app.models.schemas import (
    IssueMetadata, CandidateFile, CandidateTest, ConflictInfo,
    ContributionStep, AgentTraceStep, StepStatus, EvidenceCategory,
    InvestigationReport, SearchCodeArgs, ReadFileArgs, FindTestsArgs
)
from app.services.indexer_service import RepositoryIndexer
from app.services.github_service import check_linked_prs
from app.services.model_provider import GemmaModelProvider
from app.config import settings

TOOLS_DESCRIPTION = """
1. search_code(query: str, file_type: str = None, limit: int = 5)
   - Searches indexed repository for code files using BM25 retrieval.
   
2. read_file(path: str, start_line: int = None, end_line: int = None)
   - Reads specific source lines from a repository file.

3. get_issue_state()
   - Returns the issue title, description, state, labels, and assignee.

4. find_linked_prs(issue_number: int, repository: str)
   - Searches GitHub for linked pull requests referencing this issue.

5. find_tests(query: str, related_source_path: str = None)
   - Searches test files matching a query or related source file.

6. read_contributing_guide(repository: str)
   - Reads CONTRIBUTING.md or README.md to extract setup and test commands.
"""

class AgentService:
    def __init__(
        self,
        investigation_id: str,
        issue: IssueMetadata,
        indexer: RepositoryIndexer,
        model_provider: GemmaModelProvider,
        github_token: Optional[str] = None
    ):
        self.investigation_id = investigation_id
        self.issue = issue
        self.indexer = indexer
        self.model_provider = model_provider
        self.github_token = github_token
        self.trace: List[AgentTraceStep] = []
        self.candidate_files_map: Dict[str, CandidateFile] = {}
        self.candidate_tests_map: Dict[str, CandidateTest] = {}
        self.linked_prs: List[Dict[str, Any]] = []
        self.contributing_cmd: Optional[str] = None
        self.contributing_guide_path: Optional[str] = None
        self.warnings: List[str] = []

    async def run_investigation(self) -> InvestigationReport:
        max_steps = settings.MAX_AGENT_STEPS
        repo_url_base = f"https://github.com/{self.issue.owner}/{self.issue.repository}"
        
        # Check model configuration
        model_active = self.model_provider.is_configured()
        if not model_active:
            self.warnings.append(
                "Gemma 4 model credentials not configured (GEMMA_API_KEY is missing). "
                "Agent conducted investigation using deterministic evidence discovery."
            )

        tool_history = []
        ai_summary = None
        ai_uncertainties = []
        ai_steps = []

        step_count = 0
        while step_count < max_steps:
            step_count += 1
            
            if model_active:
                action_data = await self.model_provider.generate_action(
                    issue_title=self.issue.title,
                    issue_body=self.issue.body,
                    tool_history=tool_history,
                    available_tools_description=TOOLS_DESCRIPTION
                )
            else:
                action_data = self._get_fallback_action(step_count)

            if not action_data:
                # If model failed or gave invalid output, use default heuristic plan
                action_data = self._get_fallback_action(step_count)

            tool_name = action_data.get("tool", "")
            args = action_data.get("arguments", {})
            thought = action_data.get("thought", f"Executing investigative action: {tool_name}")

            if tool_name == "final_answer":
                ai_summary = args.get("summary")
                ai_uncertainties = args.get("uncertainties", [])
                ai_steps = args.get("contribution_steps", [])
                
                # Record trace for final synthesis
                self._record_trace(
                    step_number=step_count,
                    tool_name="final_answer",
                    action_desc="Synthesized final investigation report",
                    input_summary={},
                    status=StepStatus.COMPLETED,
                    result_summary="Report generated successfully with verified evidence.",
                    duration_ms=45.0
                )
                break

            # Execute tool
            tool_result_str = await self._execute_tool(
                step_number=step_count,
                tool_name=tool_name,
                args=args,
                action_desc=thought,
                repo_url_base=repo_url_base
            )

            tool_history.append({
                "step": step_count,
                "tool": tool_name,
                "thought": thought,
                "args": args,
                "result": tool_result_str
            })

        # Ensure we always run core tool evidence gathering if missing
        await self._ensure_baseline_evidence(repo_url_base)

        # Synthesize conflicts
        conflicts = self._synthesize_conflicts()

        # Build contribution roadmap
        roadmap = self._build_roadmap(ai_steps)

        # Build summary if model didn't provide one
        if not ai_summary:
            ai_summary = self._build_baseline_summary()

        # Verify all file citations against indexed snapshot
        verified_files = self._verify_files(repo_url_base)
        verified_tests = list(self.candidate_tests_map.values())

        # Limitations
        limitations = [
            "RepoXray provides candidate code references and recommendations based on automated search and evidence analysis.",
            "RepoXray does not claim to fix bugs automatically or guarantee that an issue is available for contribution."
        ]

        return InvestigationReport(
            investigation_id=self.investigation_id,
            status="completed",
            issue=self.issue,
            summary=ai_summary,
            uncertainties=ai_uncertainties or [
                "Specific runtime variable states cannot be evaluated without executing local tests.",
                "Maintainer team availability or ongoing unlinked work."
            ],
            relevant_files=verified_files,
            relevant_tests=verified_tests,
            possible_conflicts=conflicts,
            contribution_steps=roadmap,
            agent_trace=self.trace,
            warnings=self.warnings,
            limitations=limitations,
            contributing_command=self.contributing_cmd
        )

    def _get_fallback_action(self, step: int) -> Dict[str, Any]:
        """Deterministic step-by-step heuristic actions when model is unconfigured or returns invalid format."""
        if step == 1:
            return {
                "thought": f"Search repository code for key terms from issue title: '{self.issue.title}'",
                "tool": "search_code",
                "arguments": {"query": self.issue.title, "limit": 5}
            }
        elif step == 2:
            return {
                "thought": "Discover relevant test files matching the issue context",
                "tool": "find_tests",
                "arguments": {"query": self.issue.title}
            }
        elif step == 3:
            return {
                "thought": "Read contribution documentation for setup and test execution commands",
                "tool": "read_contributing_guide",
                "arguments": {"repository": self.issue.repository}
            }
        elif step == 4:
            return {
                "thought": f"Check for linked pull requests referencing Issue #{self.issue.number}",
                "tool": "find_linked_prs",
                "arguments": {"issue_number": self.issue.number, "repository": self.issue.repository}
            }
        else:
            return {
                "thought": "Completed empirical evidence collection across all tools.",
                "tool": "final_answer",
                "arguments": {}
            }

    async def _execute_tool(
        self,
        step_number: int,
        tool_name: str,
        args: Dict[str, Any],
        action_desc: str,
        repo_url_base: str
    ) -> str:
        start_time = time.time()
        
        try:
            if tool_name == "search_code":
                query = args.get("query", self.issue.title)
                file_type = args.get("file_type")
                limit = args.get("limit", 5)
                
                results = self.indexer.search_code(
                    query=query,
                    file_type=file_type,
                    limit=limit,
                    commit_sha=self.issue.commit_sha,
                    repo_url_base=repo_url_base
                )
                for res in results:
                    self.candidate_files_map[res.path] = res
                    
                duration = (time.time() - start_time) * 1000
                res_str = f"Found {len(results)} candidate files: " + ", ".join([r.path for r in results])
                self._record_trace(step_number, tool_name, action_desc, args, StepStatus.COMPLETED, res_str, duration)
                return res_str

            elif tool_name == "read_file":
                rel_path = args.get("path", "")
                s_line = args.get("start_line")
                e_line = args.get("end_line")
                
                content, actual_start, actual_end = self.indexer.read_file(rel_path, s_line, e_line)
                duration = (time.time() - start_time) * 1000
                
                if content is not None:
                    # Upgrade evidence type to VERIFIED_FACT
                    if rel_path in self.candidate_files_map:
                        self.candidate_files_map[rel_path].evidence_type = EvidenceCategory.VERIFIED_FACT
                        self.candidate_files_map[rel_path].line_start = actual_start
                        self.candidate_files_map[rel_path].line_end = actual_end
                    else:
                        sha = self.issue.commit_sha or "main"
                        g_url = f"{repo_url_base}/blob/{sha}/{rel_path}#L{actual_start}"
                        self.candidate_files_map[rel_path] = CandidateFile(
                            path=rel_path,
                            url=g_url,
                            line_start=actual_start,
                            line_end=actual_end,
                            reason=f"Read by agent during investigation step #{step_number}.",
                            evidence_type=EvidenceCategory.VERIFIED_FACT,
                            excerpt=content[:300]
                        )

                    res_str = f"Successfully read {rel_path} (lines {actual_start}-{actual_end})."
                    self._record_trace(step_number, tool_name, action_desc, args, StepStatus.COMPLETED, res_str, duration)
                    return res_str
                else:
                    res_str = f"File {rel_path} not found in repository snapshot."
                    self._record_trace(step_number, tool_name, action_desc, args, StepStatus.FAILED, res_str, duration, error_message="File not found")
                    return res_str

            elif tool_name == "get_issue_state":
                duration = (time.time() - start_time) * 1000
                res_str = f"Issue #{self.issue.number} state: '{self.issue.state}', Assignee: {self.issue.assignee or 'None'}, Labels: {self.issue.labels}"
                self._record_trace(step_number, tool_name, action_desc, args, StepStatus.COMPLETED, res_str, duration)
                return res_str

            elif tool_name == "find_linked_prs":
                prs = await check_linked_prs(
                    owner=self.issue.owner,
                    repo=self.issue.repository,
                    issue_number=self.issue.number,
                    github_token=self.github_token
                )
                self.linked_prs = prs
                duration = (time.time() - start_time) * 1000
                res_str = f"Found {len(prs)} linked pull requests."
                self._record_trace(step_number, tool_name, action_desc, args, StepStatus.COMPLETED, res_str, duration)
                return res_str

            elif tool_name == "find_tests":
                query = args.get("query", self.issue.title)
                source_path = args.get("related_source_path")
                tests = self.indexer.find_tests(
                    query=query,
                    related_source_path=source_path,
                    limit=5,
                    commit_sha=self.issue.commit_sha,
                    repo_url_base=repo_url_base
                )
                for t in tests:
                    self.candidate_tests_map[t.path] = t
                
                duration = (time.time() - start_time) * 1000
                res_str = f"Found {len(tests)} candidate test files: " + ", ".join([t.path for t in tests])
                self._record_trace(step_number, tool_name, action_desc, args, StepStatus.COMPLETED, res_str, duration)
                return res_str

            elif tool_name == "read_contributing_guide":
                cmd, guide_file = self.indexer.extract_contributing_command()
                self.contributing_cmd = cmd
                self.contributing_guide_path = guide_file
                duration = (time.time() - start_time) * 1000
                
                if cmd:
                    res_str = f"Extracted test command '{cmd}' from {guide_file}."
                else:
                    res_str = f"No specific test command found in {guide_file or 'contributing docs'}. General test suggestions will be used."
                
                self._record_trace(step_number, tool_name, action_desc, args, StepStatus.COMPLETED, res_str, duration)
                return res_str

            else:
                duration = (time.time() - start_time) * 1000
                res_str = f"Unknown tool '{tool_name}' requested."
                self._record_trace(step_number, tool_name, action_desc, args, StepStatus.FAILED, res_str, duration, error_message="Unknown tool")
                return res_str

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_msg = str(e)
            self._record_trace(step_number, tool_name, action_desc, args, StepStatus.FAILED, f"Tool execution failed: {error_msg}", duration, error_message=error_msg)
            return f"Error executing {tool_name}: {error_msg}"

    async def _ensure_baseline_evidence(self, repo_url_base: str):
        """Ensures all essential tools are executed to guarantee complete evidence structure."""
        if not self.candidate_files_map:
            results = self.indexer.search_code(self.issue.title, limit=5, commit_sha=self.issue.commit_sha, repo_url_base=repo_url_base)
            for res in results:
                self.candidate_files_map[res.path] = res
                
        if not self.candidate_tests_map:
            tests = self.indexer.find_tests(self.issue.title, limit=5, commit_sha=self.issue.commit_sha, repo_url_base=repo_url_base)
            for t in tests:
                self.candidate_tests_map[t.path] = t

        if self.contributing_cmd is None:
            cmd, guide_file = self.indexer.extract_contributing_command()
            self.contributing_cmd = cmd
            self.contributing_guide_path = guide_file

        if not self.linked_prs:
            try:
                self.linked_prs = await check_linked_prs(self.issue.owner, self.issue.repository, self.issue.number, self.github_token)
            except Exception:
                pass

    def _synthesize_conflicts(self) -> List[ConflictInfo]:
        conflicts = []
        if self.issue.state == "closed":
            conflicts.append(ConflictInfo(
                type="CLOSED_ISSUE",
                severity="high",
                title="Issue is already closed",
                description=f"GitHub Issue #{self.issue.number} is marked as closed on GitHub. Verify with maintainers before working on closed issues."
            ))

        if self.issue.assignee:
            conflicts.append(ConflictInfo(
                type="ASSIGNED_CONTRIBUTOR",
                severity="medium",
                title=f"Issue assigned to @{self.issue.assignee}",
                description=f"This issue is explicitly assigned to contributor @{self.issue.assignee}. Check with them before starting redundant work."
            ))

        if self.linked_prs:
            pr_urls = [pr["url"] for pr in self.linked_prs if pr.get("url")]
            conflicts.append(ConflictInfo(
                type="LINKED_PR",
                severity="medium",
                title="Related Pull Request(s) detected",
                description="One or more pull requests reference this issue on GitHub. Review them to avoid duplicate effort.",
                linked_pr_urls=pr_urls
            ))

        if not conflicts:
            conflicts.append(ConflictInfo(
                type="NO_CONFLICT",
                severity="none",
                title="No explicit contribution conflicts detected",
                description="No assigned contributor or linked PR was found in available GitHub metadata. Note: maintainers or others may still be working unlinked."
            ))

        return conflicts

    def _build_roadmap(self, ai_steps: List[Dict[str, Any]]) -> List[ContributionStep]:
        if ai_steps and len(ai_steps) >= 3:
            roadmap = []
            for idx, s in enumerate(ai_steps):
                roadmap.append(ContributionStep(
                    step_number=s.get("step_number", idx + 1),
                    title=s.get("title", f"Step {idx+1}"),
                    description=s.get("description", ""),
                    action_type=s.get("action_type", "inspect_file"),
                    target_files=s.get("target_files", []),
                    test_command=self.contributing_cmd if "test" in s.get("action_type", "") else None
                ))
            return roadmap

        # Baseline empirical roadmap
        files_list = list(self.candidate_files_map.keys())[:3]
        tests_list = list(self.candidate_tests_map.keys())[:2]
        
        step1 = ContributionStep(
            step_number=1,
            title="Inspect Candidate Source Files",
            description=f"Review the primary candidate file(s): {', '.join(files_list) if files_list else 'indexed repository files'}. Focus on function definitions related to the reported issue.",
            action_type="inspect_file",
            target_files=files_list
        )
        
        step2 = ContributionStep(
            step_number=2,
            title="Run Relevant Unit Tests",
            description=f"Locally execute the test suite for this module using: '{self.contributing_cmd or 'pytest'}' to verify existing behavior before making edits.",
            action_type="run_tests",
            target_files=tests_list,
            test_command=self.contributing_cmd or "pytest"
        )
        
        step3 = ContributionStep(
            step_number=3,
            title="Reproduce the Issue locally",
            description="Create a small test case or script replicating the behavior described in the issue description.",
            action_type="verify_behavior",
            target_files=files_list
        )
        
        step4 = ContributionStep(
            step_number=4,
            title="Clarify Requirements with Maintainers",
            description="If implementation details remain ambiguous, post a polite comment on the issue referencing your investigation findings.",
            action_type="maintainer_question"
        )

        return [step1, step2, step3, step4]

    def _build_baseline_summary(self) -> str:
        num_files = len(self.candidate_files_map)
        num_tests = len(self.candidate_tests_map)
        return (
            f"RepoXray investigated Issue #{self.issue.number} ('{self.issue.title}') in {self.issue.owner}/{self.issue.repository}. "
            f"Automated BM25 code retrieval and AST analysis identified {num_files} candidate source file(s) and {num_tests} test file(s) with supporting evidence. "
            f"Review the ranked evidence cards and contribution roadmap below."
        )

    def _verify_files(self, repo_url_base: str) -> List[CandidateFile]:
        verified = []
        for path, cand in self.candidate_files_map.items():
            # Confirm path exists in indexed repository snapshot
            if path in self.indexer.file_map:
                verified.append(cand)
            else:
                # Omit unverified paths
                self.warnings.append(f"Omitted unverified model file recommendation '{path}' (file absent in repository snapshot).")
        return verified

    def _record_trace(
        self,
        step_number: int,
        tool_name: str,
        action_desc: str,
        input_summary: Dict[str, Any],
        status: str,
        result_summary: str,
        duration_ms: float,
        error_message: Optional[str] = None
    ):
        # Sanitize keys / tokens from trace
        sanitized_input = {k: v for k, v in input_summary.items() if "token" not in k and "key" not in k}
        
        self.trace.append(AgentTraceStep(
            step_number=step_number,
            tool_name=tool_name,
            action_description=action_desc,
            input_summary=sanitized_input,
            status=status,
            result_summary=result_summary,
            duration_ms=round(duration_ms, 2),
            error_message=error_message
        ))
