from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import os

class AgentRole(Enum):
    PLANNER = "planner"
    IMPLEMENTATION = "implementation"
    LIBRARIAN = "librarian"

@dataclass
class AgentContext:
    """Context information for an agent."""
    definition_file: str
    history_file: str
    working_directory: str

@dataclass
class TaskRequest:
    task_description: str
    required_context: List[str]
    priority: int = 1
    agent_context: Optional[AgentContext] = None
    
@dataclass
class StatusUpdate:
    agent: AgentRole
    status: str
    output_files: Optional[List[str]] = None
    error_message: Optional[str] = None

class BaseAgent(ABC):
    def __init__(self, role: AgentRole):
        self.role = role
        self.status = "idle"
        self.context: Optional[AgentContext] = None
    
    def load_context(self, context_path: str) -> Dict[str, Any]:
        """Load context from a JSON file."""
        if os.path.exists(context_path):
            with open(context_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_context(self, context_path: str, data: Dict[str, Any]) -> None:
        """Save context to a JSON file."""
        os.makedirs(os.path.dirname(context_path), exist_ok=True)
        with open(context_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @abstractmethod
    async def process_task(self, task: TaskRequest) -> StatusUpdate:
        """Process an assigned task and return a status update."""
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception) -> StatusUpdate:
        """Handle any errors that occur during task processing."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent state to dictionary for serialization."""
        return {
            "role": self.role.value,
            "status": self.status,
            "context": self.context.__dict__ if self.context else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseAgent':
        """Create an agent instance from a dictionary."""
        agent = cls(AgentRole(data["role"]))
        if data.get("context"):
            agent.context = AgentContext(**data["context"])
        return agent

class ProjectState:
    def __init__(self):
        self.directory_structure: Dict[str, Any] = {}
        self.agent_statuses: Dict[str, StatusUpdate] = {}
        self.event_log: List[Dict[str, Any]] = []
    
    def update_agent_status(self, status_update: StatusUpdate) -> None:
        """Update the status of an agent in the project state."""
        self.agent_statuses[status_update.agent.value] = status_update
        self.log_event("agent_status_update", status_update)
    
    def log_event(self, event_type: str, data: Any) -> None:
        """Log an event to the project's event log."""
        event = {
            "type": event_type,
            "data": data if isinstance(data, dict) else data.__dict__
        }
        self.event_log.append(event)
    
    def to_json(self) -> str:
        """Convert project state to JSON string."""
        return json.dumps({
            "directory_structure": self.directory_structure,
            "agent_statuses": {k: v.__dict__ for k, v in self.agent_statuses.items()},
            "event_log": self.event_log
        }, indent=2) 