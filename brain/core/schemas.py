from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ActionType(str, Enum):
    AGENT = "agent"
    WORKFLOW = "workflow"
    EXIT = "exit"

class AgentConfig(BaseModel):
    agent_type: str
    tools: List[str]
    objective: Optional[str] = None

class WorkflowStep(BaseModel):
    agent_type: str
    tools: List[str]
    dependencies: List[str] = Field(default_factory=list)

class WorkflowConfig(BaseModel):
    name: str
    steps: List[WorkflowStep]
    description: Optional[str] = None

class ExecutionResult(BaseModel):
    result: Any
    cost: float
    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    action_type: ActionType
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GameStats(BaseModel):
    total_cost: float = 0.0
    tasks_run: int = 0
    successes: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)

class BrainMemory(BaseModel):
    tasks: Dict[str, ExecutionResult] = Field(default_factory=dict)
    workflows: Dict[str, WorkflowConfig] = Field(default_factory=dict)
    stats: GameStats = Field(default_factory=GameStats)