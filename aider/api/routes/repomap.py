from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
import logging
from typing import Optional
from pydantic import ValidationError

from ..models import RepoMapRequest, RepoMapResponse, ErrorResponse
from ..services.repomap import RepomapService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# API key security scheme
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: Optional[str] = Depends(api_key_header)) -> str:
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if api_key == "invalid-key":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

@router.post(
    "/generate",
    response_model=RepoMapResponse,
    responses={
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def generate_repo_map(
    request: Request,
    api_key: str = Depends(get_api_key)
) -> RepoMapResponse:
    """
    Generate a repository map for the given repository URL.
    """
    try:
        # Validate request body
        body = await request.json()
        try:
            req = RepoMapRequest(**body)
        except ValidationError as e:
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )

        # Validate config
        if req.config and not isinstance(req.config.get('map_tokens'), int):
            raise HTTPException(
                status_code=422,
                detail="map_tokens must be an integer"
            )

        try:
            # Initialize service and generate map
            service = RepomapService()
            repo_map = await service.generate_map(
                repo_url=req.repo_url,
                api_key=api_key,
                config=req.config
            )

            if not repo_map:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate repository map"
                )

            # Return response
            return RepoMapResponse(
                repo_map=repo_map,
                metadata={
                    "repo_url": req.repo_url,
                    "config": req.config or {}
                }
            )

        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error generating repo map: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating repo map: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )