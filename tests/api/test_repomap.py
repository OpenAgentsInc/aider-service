import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os
from pathlib import Path

from aider.api.services.repomap import RepomapService


def test_generate_map_endpoint_no_api_key(client):
    """Test the generate map endpoint without API key."""
    response = client.post("/api/v1/repomap/generate", json={
        "repo_url": "https://github.com/test/repo"
    })
    assert response.status_code == 422  # Validation error


def test_generate_map_endpoint_invalid_api_key(client):
    """Test the generate map endpoint with invalid API key."""
    response = client.post(
        "/api/v1/repomap/generate",
        json={
            "repo_url": "https://github.com/test/repo",
            "api_key": "invalid-key"
        },
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 401


def test_generate_map_endpoint_success(client, valid_api_key, mock_repo, mock_io):
    """Test successful map generation."""
    with patch('aider.api.services.repomap.RepomapService') as MockService:
        # Configure the mock
        instance = MockService.return_value
        instance.generate_map.return_value = "Test repo map content"
        
        response = client.post(
            "/api/v1/repomap/generate",
            json={
                "repo_url": "https://github.com/test/repo",
                "api_key": valid_api_key,
                "config": {
                    "map_tokens": 512,
                    "max_context_window": 4096
                }
            },
            headers={"X-API-Key": valid_api_key}
        )
        
        assert response.status_code == 200
        assert "repo_map" in response.json()
        assert "metadata" in response.json()
        assert response.json()["repo_map"] == "Test repo map content"


def test_generate_map_endpoint_invalid_config(client, valid_api_key):
    """Test the generate map endpoint with invalid configuration."""
    response = client.post(
        "/api/v1/repomap/generate",
        json={
            "repo_url": "https://github.com/test/repo",
            "api_key": valid_api_key,
            "config": {
                "map_tokens": "invalid",  # Should be an integer
            }
        },
        headers={"X-API-Key": valid_api_key}
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_repomap_service_generate_map(mock_repo, mock_io):
    """Test the RepomapService generate_map method."""
    service = RepomapService()
    service.io = mock_io
    
    # Test with a real directory
    result = await service.generate_map(
        str(mock_repo),
        "test-key",
        {"map_tokens": 512}
    )
    
    assert result is not None
    assert isinstance(result, str)
    assert len(mock_io.outputs) > 0  # Should have some output


@pytest.mark.asyncio
async def test_repomap_service_clone_repository(mock_repo):
    """Test the repository cloning functionality."""
    service = RepomapService()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the git clone operation
        with patch('git.Repo.clone_from') as mock_clone:
            mock_clone.return_value = None
            
            result = await service.clone_repository(
                "https://github.com/test/repo",
                temp_dir
            )
            
            assert result == temp_dir
            mock_clone.assert_called_once_with(
                "https://github.com/test/repo",
                temp_dir
            )


def test_repomap_service_config_handling():
    """Test the configuration handling in RepomapService."""
    service = RepomapService()
    
    # Test with empty config
    config = service._get_repomap_config(None)
    assert config["map_tokens"] == 1024
    assert config["max_context_window"] == 8192
    
    # Test with custom config
    custom_config = {
        "map_tokens": 512,
        "max_context_window": 4096
    }
    config = service._get_repomap_config(custom_config)
    assert config["map_tokens"] == 512
    assert config["max_context_window"] == 4096
    
    # Test that unknown keys are preserved
    custom_config["unknown_key"] = "value"
    config = service._get_repomap_config(custom_config)
    assert config["unknown_key"] == "value"