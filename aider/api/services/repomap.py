import os
import tempfile
import logging
from typing import Dict, Any, Optional
import asyncio
from git import Repo
from pathlib import Path

from ...repomap import RepoMap
from ...io import InputOutput

logger = logging.getLogger(__name__)

class RepomapService:
    def __init__(self):
        self.io = InputOutput()
        
    async def clone_repository(self, repo_url: str, temp_dir: str) -> str:
        """Clone a repository to a temporary directory."""
        try:
            logger.info(f"Cloning repository {repo_url} to {temp_dir}")
            Repo.clone_from(repo_url, temp_dir)
            return temp_dir
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            raise RuntimeError(f"Failed to clone repository: {str(e)}")

    async def generate_map(
        self,
        repo_url: str,
        api_key: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a repository map for the given repository URL."""
        
        # Create temporary directory for repo
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Clone repository
                await self.clone_repository(repo_url, temp_dir)
                
                # Initialize RepoMap
                repo_map = RepoMap(
                    root=temp_dir,
                    io=self.io,
                    verbose=True,
                    **self._get_repomap_config(config)
                )
                
                # Get all source files
                src_files = []
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if not file.startswith('.'):  # Skip hidden files
                            src_files.append(os.path.join(root, file))
                
                # Generate map
                map_content = repo_map.get_repo_map(
                    chat_files=[],  # No files in chat yet
                    other_files=src_files,
                    mentioned_fnames=set(),
                    mentioned_idents=set()
                )
                
                if not map_content:
                    raise RuntimeError("Failed to generate repository map")
                
                return map_content
                
            except Exception as e:
                logger.error(f"Error in generate_map: {e}", exc_info=True)
                raise RuntimeError(f"Failed to generate repository map: {str(e)}")
    
    def _get_repomap_config(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract RepoMap configuration from request config."""
        default_config = {
            "map_tokens": 1024,
            "max_context_window": 8192,
            "map_mul_no_files": 8,
            "refresh": "auto"
        }
        
        if config:
            default_config.update(config)
            
        return default_config