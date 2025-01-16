import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os
from pathlib import Path

from aider.api.services.repomap import RepomapService


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
@patch('git.Repo.clone_from')
async def test_repomap_service_clone_error_handling(mock_clone):
    """Test error handling during repository cloning."""
    mock_clone.side_effect = Exception("Clone failed")
    service = RepomapService()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(RuntimeError) as exc_info:
            await service.clone_repository(
                "https://github.com/test/repo",
                temp_dir
            )
        
        assert "Failed to clone repository" in str(exc_info.value)


@pytest.mark.asyncio
@patch('git.Repo.clone_from')
async def test_repomap_service_clone_repository(mock_clone):
    """Test the repository cloning functionality."""
    mock_clone.return_value = None
    service = RepomapService()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        result = await service.clone_repository(
            "https://github.com/test/repo",
            temp_dir
        )
        
        assert result == temp_dir
        mock_clone.assert_called_once_with(
            "https://github.com/test/repo",
            temp_dir
        )