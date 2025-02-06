from typing import TypedDict, Dict, List
from langgraph.graph import Graph, END
from datetime import datetime
from .schemas import TaskSchema, AgentState

class WorkflowState(TypedDict):
    """Container for the workflow state."""
    current_task: TaskSchema
    agent_states: Dict[str, AgentState]
    history: List[Dict]  # List of state deltas
    version: str

class WorkflowManager:
    """Manages the workflow state and transitions."""
    
    def __init__(self):
        self.version = "0.1.0"
        self.graph = self._build_graph()
    
    def _build_graph(self) -> Graph:
        """Builds the core workflow graph."""
        # Initialize the graph
        workflow = Graph()

        # We'll add nodes and edges here in subsequent implementations
        # For now, we're just setting up the basic structure
        
        return workflow.compile()
    
    def create_initial_state(self, task: TaskSchema) -> WorkflowState:
        """Creates the initial workflow state."""
        return WorkflowState(
            current_task=task,
            agent_states={},
            history=[],
            version=self.version
        )
    
    def record_state_delta(self, state: WorkflowState, delta_description: str) -> WorkflowState:
        """Records a change in state."""
        delta = {
            "timestamp": datetime.now().isoformat(),
            "description": delta_description,
            "version": self.version
        }
        
        # Create a new state with updated history
        return WorkflowState(
            current_task=state["current_task"],
            agent_states=state["agent_states"],
            history=state["history"] + [delta],
            version=self.version
        )
    
    def validate_state_version(self, state: WorkflowState) -> bool:
        """Validates that the state version matches the workflow version."""
        return state["version"] == self.version 