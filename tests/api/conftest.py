import pytest
from fastapi.testclient import TestClient
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from aider.api.main import app
from aider.io import InputOutput


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_api_key():
    return "test-api-key-123"


@pytest.fixture
def test_repo_url():
    return "https://github.com/test/repo"


@pytest.fixture(autouse=True)
def mock_git_operations():
    """Mock all Git operations to avoid actual GitHub calls."""
    with patch('git.Repo.clone_from') as mock_clone:
        mock_clone.return_value = None
        yield mock_clone


@pytest.fixture(autouse=True)
def mock_litellm():
    """Mock litellm to avoid actual API calls."""
    with patch('litellm.completion') as mock_completion:
        mock_completion.return_value = MagicMock()
        yield mock_completion


@pytest.fixture
def mock_repo(tmp_path):
    """Create a mock repository structure for testing."""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    
    # Create some test files
    (repo_dir / "main.py").write_text("def main():\n    print('hello')\n")
    (repo_dir / "utils.py").write_text("def helper():\n    return True\n")
    
    # Create a nested directory
    lib_dir = repo_dir / "lib"
    lib_dir.mkdir()
    (lib_dir / "core.py").write_text("class Core:\n    pass\n")
    
    return repo_dir


@pytest.fixture
def mock_io():
    """Create a mock InputOutput instance."""
    class MockIO(InputOutput):
        def __init__(self):
            self.outputs = []
            self.warnings = []
            self.errors = []
        
        def tool_output(self, msg):
            self.outputs.append(msg)
        
        def tool_warning(self, msg):
            self.warnings.append(msg)
        
        def tool_error(self, msg):
            self.errors.append(msg)
            
        def read_text(self, fname):
            try:
                with open(fname) as f:
                    return f.read()
            except Exception:
                return None
    
    return MockIO()