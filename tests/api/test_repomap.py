import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
import os
from pathlib import Path

from aider.api.services.repomap import RepomapService


def test_generate_map_endpoint_no_api_key(client):
    """Test the generate map endpoint without API key."""
    response = client.post("/api/v1/repomap/generate", json={
        "repo_url": "https://github.com/test/repo"
    })
    assert response.status_code == 403  # Forbidden - missing header


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


@patch('aider.api.routes.repomap.RepomapService')
def test_generate_map_endpoint_success(MockService, client, valid_api_key):
    """Test successful map generation."""
    # Configure the mock
    mock_instance = AsyncMock()
    mock_instance.generate_map.return_value = "Test repo map content"
    MockService.return_value = mock_instance
    
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
    with patch('aider.api.services.repomap.RepoMap') as MockRepoMap, \
         patch('aider.api.services.repomap.Model') as MockModel:
        # Configure Model mock
        mock_model = MagicMock()
        mock_model.token_count.return_value = 100
        MockModel.return_value = mock_model

        # Configure RepoMap mock
        mock_repomap = MagicMock()
        mock_repomap.get_repo_map.return_value = "Test repo map content"
        mock_repomap.main_model = mock_model
        MockRepoMap.return_value = mock_repomap
        
        service = RepomapService()
        service.io = mock_io
        
        result = await service.generate_map(
            str(mock_repo),
            "test-key",
            {"map_tokens": 512}
        )
        
        assert result == "Test repo map content"
        mock_repomap.get_repo_map.assert_called_once()