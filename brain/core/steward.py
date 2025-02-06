import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from .schemas import BrainMemory, ExecutionResult, GameStats, WorkflowConfig

class Steward:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.memory_path = self.data_dir / "memory.json"
        self.stats_path = self.data_dir / "stats.json"
        
        # Initialize memory structure
        self.brain_memory = self._load_memory()
    
    def _load_memory(self) -> BrainMemory:
        """Load or initialize brain memory from disk."""
        try:
            if self.memory_path.exists():
                data = json.loads(self.memory_path.read_text())
                return BrainMemory.model_validate(data)
        except Exception as e:
            print(f"Error loading memory: {e}. Initializing new memory.")
        return BrainMemory()
    
    def _save_memory(self) -> None:
        """Save current memory state to disk."""
        self.memory_path.write_text(self.brain_memory.model_dump_json())
    
    def add_execution_result(self, result: ExecutionResult) -> None:
        """Add a new execution result and update stats."""
        task_id = f"task_{len(self.brain_memory.tasks)}"
        self.brain_memory.tasks[task_id] = result
        
        # Update stats
        self.brain_memory.stats.total_cost += result.cost
        self.brain_memory.stats.tasks_run += 1
        if result.success:
            self.brain_memory.stats.successes += 1
        self.brain_memory.stats.last_updated = datetime.now()
        
        self._save_memory()
    
    def register_workflow(self, workflow: WorkflowConfig) -> None:
        """Register a new workflow configuration."""
        self.brain_memory.workflows[workflow.name] = workflow
        self._save_memory()
    
    def get_workflow(self, name: str) -> Optional[WorkflowConfig]:
        """Retrieve a workflow configuration by name."""
        return self.brain_memory.workflows.get(name)
    
    def get_stats(self) -> GameStats:
        """Get current game statistics."""
        return self.brain_memory.stats
    
    def get_recent_tasks(self, limit: int = 5) -> Dict[str, ExecutionResult]:
        """Get the most recent task executions."""
        tasks = list(self.brain_memory.tasks.items())
        return dict(tasks[-limit:]) 