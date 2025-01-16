from unittest.mock import patch

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_invalid_endpoint(client):
    """Test accessing an invalid endpoint."""
    response = client.get("/invalid")
    assert response.status_code == 404


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/health", headers={
        "Origin": "http://testserver",
        "Access-Control-Request-Method": "GET",
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers


@patch('git.Repo.clone_from')
def test_error_handler(mock_clone, client):
    """Test the global error handler."""
    mock_clone.return_value = None
    
    # This should trigger a validation error
    response = client.post("/api/v1/repomap/generate", json={
        "repo_url": None,  # This will cause a validation error
        "api_key": "test"
    }, headers={"X-API-Key": "test"})
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()
