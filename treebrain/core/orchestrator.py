from typing import Dict, Any, Optional, List
import os
from .interfaces import AgentRole, TaskRequest, StatusUpdate, AgentContext, BaseAgent
from ..agents import PlannerAgent, LibrarianAgent, ImplementationAgent

class Orchestrator:
    def __init__(self, project_root: str = "examples/app"):
        self.project_root = project_root
        
        # Initialize core agents
        self.planner = PlannerAgent()
        self.librarian = LibrarianAgent()
        
        # Initialize implementation agents
        self.implementation_agents = self._setup_implementation_agents()
        
        # Track all agents
        self.agents = {
            AgentRole.PLANNER: self.planner,
            AgentRole.LIBRARIAN: self.librarian,
            **{AgentRole.IMPLEMENTATION: agent for agent in self.implementation_agents}
        }
        
        # Project state
        self.project_state = {
            "status": "idle",
            "current_task": None,
            "agent_statuses": {}
        }
    
    def _get_agent_display_name(self, agent: BaseAgent) -> str:
        """Get a display name for an agent that includes its context if available."""
        if isinstance(agent, ImplementationAgent) and agent.context:
            return f"{agent.role.value} ({agent.context.working_directory})"
        return f"{agent.role.value} (core)"
    
    def _setup_implementation_agents(self) -> List[ImplementationAgent]:
        """Set up implementation agents based on project structure."""
        agents = []
        
        # Look for agent definition files in project subdirectories
        for subdir in ["frontend", "backend"]:
            dir_path = os.path.join(self.project_root, subdir)
            if os.path.exists(dir_path):
                context = AgentContext(
                    definition_file=os.path.join(dir_path, "agent_definition.json"),
                    history_file=os.path.join(dir_path, "agent_history.json"),
                    working_directory=dir_path
                )
                agents.append(ImplementationAgent(context))
        
        return agents
    
    async def process_task(self, task_description: str) -> Dict[str, Any]:
        """Process a high-level task by coordinating between agents."""
        try:
            # 1. Send task to planner for decomposition
            planning_request = TaskRequest(
                task_description=task_description,
                required_context=["README.md", "requirements.txt"]
            )
            
            planning_status = await self.planner.process_task(planning_request)
            if planning_status.status == "error":
                return self._format_error_response(planning_status.error_message)
            
            # 2. Get and execute subtasks
            results = []
            while True:
                # Process tasks for each implementation agent
                for agent in self.implementation_agents:
                    next_task = self.planner.get_next_task(AgentRole.IMPLEMENTATION)
                    if next_task:
                        # Create task request with agent context
                        task_request = TaskRequest(
                            task_description=next_task.description,
                            required_context=[],  # Determined by agent
                            agent_context=agent.context
                        )
                        
                        status = await agent.process_task(task_request)
                        results.append({
                            "agent": self._get_agent_display_name(agent),
                            "task": next_task.description,
                            "status": status.status,
                            "output_files": status.output_files
                        })
                        
                        # Update planner
                        self.planner.mark_task_complete(
                            next_task.description,
                            success=(status.status == "success")
                        )
                
                # Check if all tasks are complete
                if not any(t.status == "pending" for t in self.planner.task_queue):
                    break
            
            return {
                "status": "success",
                "results": results,
                "project_status": self.planner.get_project_status()
            }
            
        except Exception as e:
            return self._format_error_response(str(e))
    
    def get_agent_status(self, agent: BaseAgent) -> Optional[Dict[str, Any]]:
        """Get the current status of a specific agent."""
        if isinstance(agent, ImplementationAgent):
            return agent.get_implementation_status()
        elif isinstance(agent, PlannerAgent):
            return agent.get_project_status()
        else:
            return {"role": agent.role.value, "status": agent.status}
    
    def get_project_overview(self) -> Dict[str, Any]:
        """Get an overview of the entire project state."""
        return {
            "status": self.project_state["status"],
            "current_task": self.project_state["current_task"],
            "agent_statuses": {
                self._get_agent_display_name(agent): self.get_agent_status(agent)
                for agent in [self.planner, self.librarian] + self.implementation_agents
            }
        }
    
    def _format_error_response(self, error_message: str) -> Dict[str, Any]:
        """Format an error response."""
        return {
            "status": "error",
            "error": error_message,
            "project_status": self.get_project_overview()
        } 