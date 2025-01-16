# Repository Mapping Service

The repository mapping service provides an API endpoint that generates a structured map of a Git repository's codebase. This helps agents and users better understand the repository structure and relationships between different code components.

## Overview

The service uses Aider's repository mapping technology to analyze repositories and generate maps that show:
- File structure
- Code dependencies
- Important identifiers
- File relationships

## API Endpoint

### Generate Repository Map

```
POST /api/v1/repomap/generate
```

Request body:
```json
{
    "repo_url": "https://github.com/username/repo",
    "api_key": "your-api-key",
    "config": {
        "map_tokens": 1024,
        "max_context_window": 8192,
        "map_mul_no_files": 8,
        "refresh": "auto"
    }
}
```

Response:
```json
{
    "repo_map": "... repository map content ...",
    "metadata": {
        "repo_url": "https://github.com/username/repo",
        "config": {
            "map_tokens": 1024,
            "max_context_window": 8192,
            "map_mul_no_files": 8,
            "refresh": "auto"
        }
    }
}
```

## Configuration

The repository mapping service accepts several configuration parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| map_tokens | Maximum tokens in the map | 1024 |
| max_context_window | Maximum context window size | 8192 |
| map_mul_no_files | Multiplier for no files case | 8 |
| refresh | Refresh strategy | "auto" |

## Development

### Running the Service

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the service:
```bash
uvicorn aider.api.main:app --reload
```

The service will be available at http://localhost:8000

### Running Tests

The test suite includes unit tests and integration tests. To run the tests:

```bash
# Run all tests
pytest tests/api

# Run specific test file
pytest tests/api/test_repomap.py

# Run with coverage
pytest tests/api --cov=aider.api
```

### Test Structure

The tests are organized as follows:

```
tests/api/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_main.py         # Main app tests
├── test_repomap.py      # Repository map endpoint tests
└── test_services.py     # Service layer tests
```

## Error Handling

The service includes comprehensive error handling:

- 400 Bad Request: Invalid input parameters
- 401 Unauthorized: Invalid or missing API key
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Server-side errors

## Security

The service implements several security measures:

1. API key validation
2. Rate limiting
3. Input validation
4. Error message sanitization

## Monitoring

The service includes basic monitoring endpoints:

- GET /health - Health check endpoint
- GET /metrics - Prometheus metrics (if configured)