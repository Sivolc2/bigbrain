from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class TaskSchema(BaseModel):
    """Schema for a task in the system."""
    task_id: UUID = Field(default_factory=uuid4)
    input: str
    parent_task_id: Optional[UUID] = None
    priority: int = Field(default=1, ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "pending"

class ToolHistory(BaseModel):
    """Record of a tool's usage."""
    tool_name: str
    inputs: Dict
    outputs: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None

class AgentState(BaseModel):
    """Current state of an agent."""
    memory: Dict = Field(default_factory=dict)
    context: Dict = Field(default_factory=dict)
    tool_history: List[ToolHistory] = Field(default_factory=list)
    last_update: datetime = Field(default_factory=datetime.now)

    def add_tool_usage(self, tool_name: str, inputs: Dict, outputs: Optional[Dict] = None, 
                      success: bool = True, error_message: Optional[str] = None) -> None:
        """Add a tool usage record to the history."""
        history_entry = ToolHistory(
            tool_name=tool_name,
            inputs=inputs,
            outputs=outputs,
            success=success,
            error_message=error_message
        )
        self.tool_history.append(history_entry)
        self.last_update = datetime.now() 