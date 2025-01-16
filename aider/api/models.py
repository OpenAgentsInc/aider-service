from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class RepoMapRequest(BaseModel):
    repo_url: str = Field(..., description="URL of the repository to analyze")
    api_key: str = Field(..., description="API key for authentication")
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional configuration parameters for repository mapping"
    )


class RepoMapResponse(BaseModel):
    repo_map: str = Field(..., description="Generated repository map")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the generated map"
    )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )