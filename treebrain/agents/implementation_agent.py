from typing import Dict, Any, List, Optional
import json
import os
from ..core.interfaces import BaseAgent, AgentRole, TaskRequest, StatusUpdate, AgentContext

class ImplementationAgent(BaseAgent):
    def __init__(self, context: AgentContext):
        super().__init__(AgentRole.IMPLEMENTATION)
        self.context = context
        self.definition = self.load_context(context.definition_file)
        self.history = self.load_context(context.history_file)
        
    async def process_task(self, task: TaskRequest) -> StatusUpdate:
        """Process an implementation task using LLM-based decision making."""
        try:
            # Load latest context
            self.history = self.load_context(self.context.history_file)
            
            # Prepare task context for LLM
            task_context = self._prepare_task_context(task)
            
            # In practice, this would:
            # 1. Call LLM with task context
            # 2. Parse LLM response
            # 3. Execute suggested changes
            # 4. Validate changes
            # 5. Update history
            
            # Mock implementation for now
            output_files = self._mock_implementation(task)
            
            # Update history
            self._update_history(task, output_files)
            
            return StatusUpdate(
                agent=self.role,
                status="success",
                output_files=output_files
            )
            
        except Exception as e:
            return await self.handle_error(e)
    
    def _prepare_task_context(self, task: TaskRequest) -> Dict[str, Any]:
        """Prepare context for LLM consumption."""
        return {
            "task": task.task_description,
            "agent_definition": self.definition,
            "working_directory": self.context.working_directory,
            "history": self.history,
            "required_context": task.required_context
        }
    
    def _mock_implementation(self, task: TaskRequest) -> List[str]:
        """Mock implementation - to be replaced with LLM-based implementation."""
        base_path = self.context.working_directory
        task_type = task.task_description.lower()
        
        if "frontend" in base_path:
            if "component" in task_type:
                return [f"{base_path}/src/components/NewComponent.tsx"]
            elif "page" in task_type:
                return [f"{base_path}/src/pages/NewPage.tsx"]
        elif "backend" in base_path:
            if "api" in task_type:
                return [
                    f"{base_path}/src/api/new_endpoint.py",
                    f"{base_path}/tests/api/test_new_endpoint.py"
                ]
            elif "model" in task_type:
                return [f"{base_path}/src/models/new_model.py"]
        
        return []
    
    def _update_history(self, task: TaskRequest, output_files: List[str]) -> None:
        """Update agent history with completed task."""
        if not self.history.get("completed_tasks"):
            self.history["completed_tasks"] = []
            
        self.history["completed_tasks"].append({
            "timestamp": "2024-02-09T12:00:00Z",  # Use actual timestamp in practice
            "task": task.task_description,
            "files_modified": output_files,
            "status": "success"
        })
        
        self.save_context(self.context.history_file, self.history)
    
    async def handle_error(self, error: Exception) -> StatusUpdate:
        """Handle errors during task processing."""
        return StatusUpdate(
            agent=self.role,
            status="error",
            error_message=str(error)
        )
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """Get the current implementation status."""
        return {
            "role": self.role.value,
            "working_directory": self.context.working_directory,
            "completed_tasks": len(self.history.get("completed_tasks", [])),
            "current_context": self.history.get("current_context", {})
        } 