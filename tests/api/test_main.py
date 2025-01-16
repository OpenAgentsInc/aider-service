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


def test_error_handler(client):
    """Test the global error handler."""
    # This should trigger a 500 error
    response = client.post("/api/v1/repomap/generate", json={
        "repo_url": None,  # This will cause a validation error
        "api_key": "test"
    })
    assert response.status_code == 422  # Validation error
    assert "error" in response.json()["detail"][0]