from typing import List, Dict, Any, Optional
from abc import abstractmethod
from ..core.interfaces import BaseAgent, AgentRole, TaskRequest, StatusUpdate

class ActionAgent(BaseAgent):
    def __init__(self, role: AgentRole):
        super().__init__(role)
        self.current_task: Optional[TaskRequest] = None
        self.context: Dict[str, Any] = {}
    
    async def process_task(self, task: TaskRequest) -> StatusUpdate:
        """Process an implementation task."""
        try:
            self.current_task = task
            
            # Get required context
            context_status = await self.gather_context(task.required_context)
            if context_status.status == "error":
                return context_status
            
            # Validate task requirements
            validation_status = await self.validate_requirements()
            if validation_status.status == "error":
                return validation_status
            
            # Implement the task
            implementation_status = await self.implement_task()
            if implementation_status.status == "error":
                return implementation_status
            
            # Run tests
            test_status = await self.run_tests()
            if test_status.status == "error":
                return test_status
            
            return StatusUpdate(
                agent=self.role,
                status="success",
                output_files=implementation_status.output_files
            )
            
        except Exception as e:
            return await self.handle_error(e)
    
    async def gather_context(self, required_files: List[str]) -> StatusUpdate:
        """Gather required context for the task."""
        try:
            self.context = {}  # Reset context
            # In practice, this would use the Librarian agent to fetch files
            return StatusUpdate(
                agent=self.role,
                status="success"
            )
        except Exception as e:
            return StatusUpdate(
                agent=self.role,
                status="error",
                error_message=f"Failed to gather context: {str(e)}"
            )
    
    async def validate_requirements(self) -> StatusUpdate:
        """Validate that all requirements are met before implementation."""
        try:
            # Implement validation logic specific to the agent type
            return StatusUpdate(
                agent=self.role,
                status="success"
            )
        except Exception as e:
            return StatusUpdate(
                agent=self.role,
                status="error",
                error_message=f"Requirements validation failed: {str(e)}"
            )
    
    @abstractmethod
    async def implement_task(self) -> StatusUpdate:
        """Implement the task - to be implemented by specific agent types."""
        pass
    
    async def run_tests(self) -> StatusUpdate:
        """Run tests for the implemented task."""
        try:
            # Implement test running logic specific to the agent type
            return StatusUpdate(
                agent=self.role,
                status="success"
            )
        except Exception as e:
            return StatusUpdate(
                agent=self.role,
                status="error",
                error_message=f"Tests failed: {str(e)}"
            )
    
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
            "current_task": self.current_task.task_description if self.current_task else None,
            "status": self.status,
            "context_files": list(self.context.keys())
        } 