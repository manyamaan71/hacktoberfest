import os
import ast
import re
from typing import List, Dict, Any, Optional, Tuple
from rank_bm25 import BM25Okapi
from app.models.schemas import CandidateFile, CandidateTest, EvidenceCategory

IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", "venv", ".venv", "env",
    "build", "dist", ".pytest_cache", ".tox", ".nox", "eggs", "*.egg-info",
    ".idea", ".vscode", "coverage", ".coverage"
}

IGNORE_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib", ".exe", ".bin",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".pdf", ".zip",
    ".tar", ".gz", ".7z", ".db", ".sqlite", ".sqlite3", ".woff", ".woff2"
}

def normalize_identifiers(text: str) -> str:
    """
    Normalizes identifiers so snake_case, camelCase, PascalCase and spaced words match.
    Example: 'validate_payload' -> 'validate_payload validate payload'
             'ValidatePayload' -> 'ValidatePayload validate payload'
    """
    if not text:
        return ""
    
    tokens = [text]
    # Split camel/Pascal case
    camel_split = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    tokens.append(camel_split)
    
    # Split snake_case / kebab-case
    snake_split = re.sub(r'[_:\-\.]', ' ', text)
    tokens.append(snake_split)
    
    return " ".join(tokens).lower()

class IndexedFile:
    def __init__(self, relative_path: str, absolute_path: str, content: str, symbols: List[str], is_test: bool):
        self.relative_path = relative_path.replace("\\", "/")
        self.absolute_path = absolute_path
        self.content = content
        self.symbols = symbols
        self.is_test = is_test
        # Tokenize content for BM25
        normalized_content = normalize_identifiers(content) + " " + normalize_identifiers(self.relative_path)
        self.tokens = [t for t in re.split(r'\W+', normalized_content) if len(t) > 1]

class RepositoryIndexer:
    def __init__(self, repo_root: str, max_files: int = 1500, max_file_size: int = 524288):
        self.repo_root = os.path.abspath(repo_root)
        self.max_files = max_files
        self.max_file_size = max_file_size
        self.files: List[IndexedFile] = []
        self.bm25: Optional[BM25Okapi] = None
        self.file_map: Dict[str, IndexedFile] = {}
        self.contributing_text: Optional[str] = None
        self.contributing_file: Optional[str] = None
        self.readme_text: Optional[str] = None

    def index(self):
        self.files.clear()
        self.file_map.clear()

        count = 0
        for root, dirs, filenames in os.walk(self.repo_root):
            # Exclude ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.endswith(".egg-info")]

            for filename in filenames:
                if count >= self.max_files:
                    break

                ext = os.path.splitext(filename)[1].lower()
                if ext in IGNORE_EXTENSIONS:
                    continue

                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, self.repo_root).replace("\\", "/")

                # Check file size limit
                try:
                    size = os.path.getsize(abs_path)
                    if size > self.max_file_size:
                        continue
                except OSError:
                    continue

                # Read content safely
                content = self._read_file_content(abs_path)
                if content is None:
                    continue

                # Check for contributing/readme guides
                lower_filename = filename.lower()
                if lower_filename in ("contributing.md", "contributing.rst", "contributing.txt", "contributing"):
                    self.contributing_text = content
                    self.contributing_file = rel_path
                elif lower_filename in ("readme.md", "readme.rst", "readme.txt", "readme") and not self.readme_text:
                    self.readme_text = content

                symbols = []
                if ext == ".py":
                    symbols = self._extract_python_symbols(content)

                is_test = (
                    "test" in rel_path.lower().split("/") or
                    filename.lower().startswith("test_") or
                    filename.lower().endswith("_test.py") or
                    filename.lower().startswith("tests_")
                )

                indexed_file = IndexedFile(
                    relative_path=rel_path,
                    absolute_path=abs_path,
                    content=content,
                    symbols=symbols,
                    is_test=is_test
                )
                self.files.append(indexed_file)
                self.file_map[rel_path] = indexed_file
                count += 1

        # Build BM25 index
        corpus_tokens = [f.tokens if f.tokens else ["empty"] for f in self.files]
        if corpus_tokens:
            self.bm25 = BM25Okapi(corpus_tokens)

    def _read_file_content(self, path: str) -> Optional[str]:
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                with open(path, "r", encoding=encoding, errors="replace") as f:
                    return f.read()
            except Exception:
                continue
        return None

    def _extract_python_symbols(self, content: str) -> List[str]:
        symbols = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbols.append(f"def {node.name}")
                elif isinstance(node, ast.AsyncFunctionDef):
                    symbols.append(f"async def {node.name}")
                elif isinstance(node, ast.ClassDef):
                    symbols.append(f"class {node.name}")
        except Exception:
            pass
        return symbols

    def search_code(
        self,
        query: str,
        file_type: Optional[str] = None,
        limit: int = 5,
        commit_sha: Optional[str] = None,
        repo_url_base: Optional[str] = None
    ) -> List[CandidateFile]:
        if not self.files or not self.bm25:
            return []

        normalized_query = normalize_identifiers(query)
        query_tokens = [t for t in re.split(r'\W+', normalized_query) if len(t) > 1]
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)
        
        scored_files: List[Tuple[float, IndexedFile]] = []
        for score, f in zip(scores, self.files):
            # Apply file_type filter if specified
            if file_type:
                ft = file_type.lstrip(".").lower()
                if not f.relative_path.lower().endswith(f".{ft}"):
                    continue
            
            # Exclude tests if general code search is performed, unless query is specifically looking for tests
            if f.is_test and "test" not in query.lower():
                score *= 0.5

            # Fallback token overlap scoring if BM25 score is 0 or low
            overlap = sum(1 for q_t in query_tokens if q_t in f.tokens)
            effective_score = float(score) if score > 0 else (overlap * 1.0)

            if effective_score > 0:
                scored_files.append((effective_score, f))

        scored_files.sort(key=lambda x: x[0], reverse=True)
        results: List[CandidateFile] = []

        for score, f in scored_files[:limit]:
            snippet, start_line, end_line = self._extract_best_snippet(f.content, query)
            github_url = None
            if repo_url_base:
                sha = commit_sha or "main"
                github_url = f"{repo_url_base}/blob/{sha}/{f.relative_path}"
                if start_line:
                    github_url += f"#L{start_line}"

            reason = f"Ranked #{len(results)+1} by BM25 text retrieval (Score: {score:.2f}) matching query '{query}'."
            if f.symbols:
                reason += f" Contains symbols: {', '.join(f.symbols[:3])}."

            results.append(CandidateFile(
                path=f.relative_path,
                url=github_url,
                line_start=start_line,
                line_end=end_line,
                symbols=f.symbols[:5],
                reason=reason,
                evidence_type=EvidenceCategory.HEURISTIC_MATCH,
                score=round(score, 2),
                excerpt=snippet
            ))

        return results

    def find_tests(
        self,
        query: str,
        related_source_path: Optional[str] = None,
        limit: int = 5,
        commit_sha: Optional[str] = None,
        repo_url_base: Optional[str] = None
    ) -> List[CandidateTest]:
        test_files = [f for f in self.files if f.is_test]
        if not test_files:
            return []

        results: List[CandidateTest] = []
        query_terms = [t.lower() for t in re.split(r'\W+', query) if len(t) > 1]
        
        # If a related source path is given (e.g. app/services/auth.py), match test_auth.py
        target_stem = ""
        if related_source_path:
            base_name = os.path.basename(related_source_path)
            target_stem = os.path.splitext(base_name)[0].lower()

        for f in test_files:
            match_type = "content_match"
            reason = ""
            score = 0

            rel_lower = f.relative_path.lower()
            if target_stem and (f"test_{target_stem}" in rel_lower or f"{target_stem}_test" in rel_lower):
                match_type = "filename_match"
                score += 10.0
                reason = f"Test filename directly corresponds to target module '{target_stem}'."

            # Check matching symbols
            matching_test_funcs = [s for s in f.symbols if any(term in s.lower() for term in query_terms)]
            if matching_test_funcs:
                score += 5.0
                if not reason:
                    match_type = "symbol_match"
                    reason = f"Test file contains matching test function: {matching_test_funcs[0]}."

            # Check content match
            content_lower = f.content.lower()
            matched_terms = [term for term in query_terms if term in content_lower]
            if matched_terms:
                score += len(matched_terms)
                if not reason:
                    reason = f"Test file content references query terms: {', '.join(matched_terms[:3])}."

            if score > 0:
                snippet, start_line, end_line = self._extract_best_snippet(f.content, query)
                github_url = None
                if repo_url_base:
                    sha = commit_sha or "main"
                    github_url = f"{repo_url_base}/blob/{sha}/{f.relative_path}"
                    if start_line:
                        github_url += f"#L{start_line}"

                results.append(CandidateTest(
                    path=f.relative_path,
                    url=github_url,
                    test_functions=f.symbols[:5],
                    reason=reason,
                    evidence_type=EvidenceCategory.HEURISTIC_MATCH,
                    match_type=match_type,
                    excerpt=snippet
                ))

        results.sort(key=lambda x: len(x.reason), reverse=True)
        return results[:limit]

    def _extract_best_snippet(self, content: str, query: str, max_lines: int = 6) -> Tuple[str, Optional[int], Optional[int]]:
        lines = content.splitlines()
        if not lines:
            return "", None, None

        query_terms = [t.lower() for t in re.split(r'\W+', query) if len(t) > 1]
        best_line_idx = 0
        best_matches = -1

        for idx, line in enumerate(lines):
            line_lower = line.lower()
            matches = sum(1 for term in query_terms if term in line_lower)
            if matches > best_matches:
                best_matches = matches
                best_line_idx = idx

        start_idx = max(0, best_line_idx - 2)
        end_idx = min(len(lines), start_idx + max_lines)
        snippet_lines = lines[start_idx:end_idx]
        snippet = "\n".join(snippet_lines)
        
        return snippet, start_idx + 1, end_idx

    def read_file(self, rel_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> Tuple[Optional[str], Optional[int], Optional[int]]:
        # Clean relative path to prevent path traversal
        clean_path = os.path.normpath(rel_path).replace("\\", "/")
        if clean_path.startswith("..") or clean_path.startswith("/"):
            return None, None, None

        indexed_file = self.file_map.get(clean_path)
        if not indexed_file:
            return None, None, None

        lines = indexed_file.content.splitlines()
        total_lines = len(lines)

        s_line = start_line if (start_line and 1 <= start_line <= total_lines) else 1
        e_line = end_line if (end_line and s_line <= end_line <= total_lines) else min(total_lines, s_line + 100)

        selected_lines = lines[s_line - 1 : e_line]
        return "\n".join(selected_lines), s_line, e_line

    def extract_contributing_command(self) -> Tuple[Optional[str], Optional[str]]:
        guide_text = self.contributing_text or self.readme_text
        source_file = self.contributing_file or "README.md"
        if not guide_text:
            return None, None

        # Look for common test execution patterns in code blocks or text
        test_patterns = [
            r"(`pytest[^`]*`)",
            r"(`python -m unittest[^`]*`)",
            r"(`poetry run pytest[^`]*`)",
            r"(`tox[^`]*`)",
            r"(`nox[^`]*`)",
            r"(`npm test[^`]*`)",
            r"(pytest\s+[a-zA-Z0-9_\-\.\/]+)",
            r"(python -m unittest\s+[a-zA-Z0-9_\-\.\/]+)"
        ]

        for pattern in test_patterns:
            match = re.search(pattern, guide_text, re.IGNORECASE)
            if match:
                cmd = match.group(1).strip("`")
                return cmd, source_file

        return None, None
