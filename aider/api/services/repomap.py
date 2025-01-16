import os
import tempfile
import logging
from typing import Dict, Any, Optional
import asyncio
from git import Repo
from pathlib import Path

from ...repomap import RepoMap
from ...io import InputOutput
from ...models import Model

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
                
                # Validate config before initializing RepoMap
                config_dict = self._get_repomap_config(config)
                if not isinstance(config_dict.get('map_tokens'), int):
                    raise ValueError("map_tokens must be an integer")
                
                # Initialize RepoMap with validated config
                repo_map = RepoMap(
                    root=temp_dir,
                    io=self.io,
                    verbose=True,
                    **config_dict
                )
                
                # Skip cache files
                def filter_files(fname):
                    return not (
                        '.aider.tags.cache' in fname or
                        fname.endswith('.pyc') or
                        '/__pycache__/' in fname
                    )
            
                # Get all source files
                src_files = []
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        if filter_files(full_path):
                            src_files.append(full_path)
                
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
            "refresh": "auto",
            "main_model": Model("gpt-3.5-turbo")
        }
        
        if config:
            # Don't override main_model from config
            model = default_config["main_model"]
            default_config.update(config)
            default_config["main_model"] = model
            
        return default_config