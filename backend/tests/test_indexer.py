import os
import tempfile
import pytest
from app.services.indexer_service import RepositoryIndexer, normalize_identifiers

def test_normalize_identifiers():
    assert "validate" in normalize_identifiers("validate_payload")
    assert "payload" in normalize_identifiers("validate_payload")
    assert "camel" in normalize_identifiers("camelCaseTest")
    assert "case" in normalize_identifiers("camelCaseTest")

def test_repository_indexer_search_and_test():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy source files
        auth_file = os.path.join(tmpdir, "auth_service.py")
        with open(auth_file, "w", encoding="utf-8") as f:
            f.write("""
class AuthManager:
    def validate_token(self, token: str):
        if not token:
            raise ValueError("Token is missing")
        return True
""")

        test_file_path = os.path.join(tmpdir, "test_auth.py")
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("""
def test_validate_token_missing():
    auth = AuthManager()
    # assert exception
""")

        readme_file = os.path.join(tmpdir, "README.md")
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write("# Project Setup\nRun tests using `pytest` command.\n")

        indexer = RepositoryIndexer(tmpdir)
        indexer.index()

        assert len(indexer.files) >= 2
        
        # Test code search
        results = indexer.search_code("validate token", limit=2)
        assert len(results) >= 1
        assert results[0].path == "auth_service.py"
        assert "def validate_token" in str(results[0].symbols) or "class AuthManager" in str(results[0].symbols)

        # Test test search
        tests = indexer.find_tests("validate token", related_source_path="auth_service.py", limit=2)
        assert len(tests) >= 1
        assert tests[0].path == "test_auth.py"

        # Test contributing command extraction
        cmd, source = indexer.extract_contributing_command()
        assert cmd == "pytest"
