import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os
from pathlib import Path

from aider.api.services.repomap import RepomapService
from aider.repomap import RepoMap


def test_repomap_service_initialization():
    """Test RepomapService initialization."""
    service = RepomapService()
    assert service.io is not None


def test_repomap_service_config_defaults():
    """Test default configuration values."""
    service = RepomapService()
    config = service._get_repomap_config(None)
    
    assert config["map_tokens"] == 1024
    assert config["max_context_window"] == 8192
    assert config["map_mul_no_files"] == 8
    assert config["refresh"] == "auto"


def test_repomap_service_config_override():
    """Test configuration override behavior."""
    service = RepomapService()
    custom_config = {
        "map_tokens": 2048,
        "max_context_window": 16384,
        "map_mul_no_files": 4,
        "refresh": "always"
    }
    
    config = service._get_repomap_config(custom_config)
    
    assert config["map_tokens"] == 2048
    assert config["max_context_window"] == 16384
    assert config["map_mul_no_files"] == 4
    assert config["refresh"] == "always"


@pytest.mark.asyncio
async def test_repomap_service_clone_error_handling():
    """Test error handling during repository cloning."""
    service = RepomapService()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('git.Repo.clone_from', side_effect=Exception("Clone failed")):
            with pytest.raises(RuntimeError) as exc_info:
                await service.clone_repository(
                    "https://github.com/test/repo",
                    temp_dir
                )
            
            assert "Failed to clone repository" in str(exc_info.value)


@pytest.mark.asyncio
async def test_repomap_service_generate_map_error_handling(mock_io):
    """Test error handling during map generation."""
    service = RepomapService()
    service.io = mock_io
    
    # Test with invalid repository path
    with pytest.raises(RuntimeError) as exc_info:
        await service.generate_map(
            "invalid/path",
            "test-key"
        )
    
    assert "Failed to generate repository map" in str(exc_info.value)


def test_repomap_integration_with_core(mock_repo, mock_io):
    """Test integration with core RepoMap functionality."""
    repo_map = RepoMap(
        root=str(mock_repo),
        io=mock_io,
        verbose=True
    )
    
    # Get all files in the mock repo
    files = []
    for root, _, filenames in os.walk(mock_repo):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    
    # Generate map
    result = repo_map.get_repo_map(
        chat_files=[],
        other_files=files
    )
    
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0