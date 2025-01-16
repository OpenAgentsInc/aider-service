from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import APIKeyHeader
import logging
from typing import Optional

from ..models import RepoMapRequest, RepoMapResponse, ErrorResponse
from ..services.repomap import RepomapService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# API key security scheme
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required"
        )
    return api_key

@router.post(
    "/generate",
    response_model=RepoMapResponse,
    responses={
        401: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def generate_repo_map(
    request: RepoMapRequest,
    api_key: str = Depends(get_api_key)
) -> RepoMapResponse:
    """
    Generate a repository map for the given repository URL.
    """
    try:
        # Initialize service
        service = RepomapService()
        
        # Generate map
        repo_map = await service.generate_map(
            repo_url=request.repo_url,
            api_key=api_key,
            config=request.config
        )
        
        # Return response
        return RepoMapResponse(
            repo_map=repo_map,
            metadata={
                "repo_url": request.repo_url,
                "config": request.config or {}
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating repo map: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )