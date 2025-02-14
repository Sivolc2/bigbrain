import os
from pathlib import Path
from typing import Dict, List, Optional
from ..core.interfaces import BaseAgent, AgentRole, TaskRequest, StatusUpdate

class LibrarianAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.LIBRARIAN)
        self.cache_duration = 300  # 5 minutes in seconds
        self.directory_cache: Dict[str, dict] = {}
        self.file_cache: Dict[str, tuple] = {}  # (content, timestamp)
    
    async def process_task(self, task: TaskRequest) -> StatusUpdate:
        """Process a knowledge retrieval task."""
        try:
            if "get_directory_structure" in task.task_description:
                structure = self.get_directory_structure()
                return StatusUpdate(
                    agent=self.role,
                    status="success",
                    output_files=None,
                    error_message=None
                )
            elif "read_file" in task.task_description:
                if not task.required_context:
                    return StatusUpdate(
                        agent=self.role,
                        status="error",
                        error_message="No file path provided"
                    )
                file_content = self.read_file(task.required_context[0])
                return StatusUpdate(
                    agent=self.role,
                    status="success",
                    output_files=[task.required_context[0]]
                )
            else:
                return StatusUpdate(
                    agent=self.role,
                    status="error",
                    error_message=f"Unknown task type: {task.task_description}"
                )
        except Exception as e:
            return await self.handle_error(e)
    
    async def handle_error(self, error: Exception) -> StatusUpdate:
        """Handle errors during task processing."""
        return StatusUpdate(
            agent=self.role,
            status="error",
            error_message=str(error)
        )
    
    def get_directory_structure(self, path: str = ".") -> Dict:
        """Get the current directory structure."""
        structure = {}
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    structure[entry.name] = {
                        "type": "file",
                        "size": entry.stat().st_size
                    }
                elif entry.is_dir() and not entry.name.startswith('.'):
                    structure[entry.name] = {
                        "type": "directory",
                        "contents": self.get_directory_structure(entry.path)
                    }
        except Exception as e:
            structure["error"] = str(e)
        return structure
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read and cache file contents."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")
    
    def invalidate_cache(self) -> None:
        """Clear all cached data."""
        self.directory_cache.clear()
        self.file_cache.clear() 