from typing import List, Dict, Any
from ..core.interfaces import BaseAgent, AgentRole, TaskRequest, StatusUpdate

class Task:
    def __init__(self, description: str, assigned_to: AgentRole, dependencies: List[str] = None):
        self.description = description
        self.assigned_to = assigned_to
        self.dependencies = dependencies or []
        self.status = "pending"
        self.attempts = 0

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.PLANNER)
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.max_retries = 3
    
    async def process_task(self, task: TaskRequest) -> StatusUpdate:
        """Process a planning task and decompose it into subtasks."""
        try:
            # Decompose the task based on its description
            subtasks = self.decompose_task(task.task_description)
            
            # Add subtasks to the queue
            for subtask in subtasks:
                self.task_queue.append(subtask)
            
            return StatusUpdate(
                agent=self.role,
                status="success",
                output_files=None,
                error_message=None
            )
        except Exception as e:
            return await self.handle_error(e)
    
    def decompose_task(self, task_description: str) -> List[Task]:
        """Decompose a high-level task into subtasks."""
        subtasks = []
        
        # Always create both frontend and backend tasks for now
        # In practice, this would use LLM to determine appropriate subtasks
        subtasks.extend([
            Task(
                f"Implement frontend for: {task_description}",
                AgentRole.IMPLEMENTATION
            ),
            Task(
                f"Implement backend for: {task_description}",
                AgentRole.IMPLEMENTATION
            )
        ])
        
        return subtasks
    
    async def handle_error(self, error: Exception) -> StatusUpdate:
        """Handle errors during task processing."""
        return StatusUpdate(
            agent=self.role,
            status="error",
            error_message=str(error)
        )
    
    def get_next_task(self, agent_role: AgentRole) -> Task:
        """Get the next available task for an agent."""
        for task in self.task_queue:
            if (task.assigned_to == agent_role and 
                task.status == "pending" and
                all(dep in [t.description for t in self.completed_tasks] 
                    for dep in task.dependencies)):
                return task
        return None
    
    def mark_task_complete(self, task_description: str, success: bool = True) -> None:
        """Mark a task as complete or failed."""
        for task in self.task_queue:
            if task.description == task_description:
                if success:
                    task.status = "completed"
                    self.completed_tasks.append(task)
                    self.task_queue.remove(task)
                else:
                    task.attempts += 1
                    if task.attempts >= self.max_retries:
                        task.status = "failed"
                    else:
                        task.status = "pending"
                break
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get the current status of all tasks."""
        return {
            "pending_tasks": len([t for t in self.task_queue if t.status == "pending"]),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len([t for t in self.task_queue if t.status == "failed"]),
            "current_tasks": [
                {
                    "description": t.description,
                    "assigned_to": t.assigned_to.value,
                    "status": t.status,
                    "attempts": t.attempts
                }
                for t in self.task_queue
            ]
        } 