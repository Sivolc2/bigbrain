from typing import List, Dict
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize the Anthropic client
llm = ChatAnthropic(
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    model=os.getenv("DEFAULT_MODEL", "claude-3-sonnet-20240229"),
    temperature=float(os.getenv("MODEL_TEMPERATURE", "0.2"))
)

class SubTask(BaseModel):
    """A single subtask in the decomposition."""
    name: str = Field(..., description="Name of the subtask")
    dependencies: List[str] = Field(default_factory=list, description="Names of subtasks this depends on")
    tool: str = Field(..., description="Name of the tool required for this subtask")
    description: str = Field(..., description="Detailed description of what needs to be done")

class TaskAnalysis(BaseModel):
    """Complete analysis of a task."""
    required_tools: List[str] = Field(..., description="List of tools needed for the entire task")
    complexity_score: int = Field(..., ge=1, le=5, description="Complexity score from 1-5")
    subtasks: List[SubTask] = Field(..., description="List of subtasks to complete")
    reasoning: str = Field(..., description="Explanation of the task breakdown")

TASK_ANALYSIS_PROMPT = """You are an expert system designed to break down complex tasks into manageable subtasks.
Given a task, analyze it and provide a structured breakdown.

Task: {task}

Available Tools: {available_tools}

Provide a JSON response that includes:
1. List of required tools from the available tools
2. Complexity score (1-5) where 5 is most complex
3. Ordered list of subtasks, each with:
   - name
   - dependencies (other subtask names it depends on)
   - required tool
   - detailed description
4. Reasoning for your breakdown

Your response must be valid JSON matching this structure:
{{
    "required_tools": ["tool1", "tool2"],
    "complexity_score": 3,
    "subtasks": [
        {{
            "name": "subtask1",
            "dependencies": [],
            "tool": "tool1",
            "description": "detailed description"
        }}
    ],
    "reasoning": "explanation of breakdown"
}}

Remember:
- Each subtask should be atomic and achievable with a single tool
- Dependencies should create a valid DAG (no cycles)
- Complexity score should reflect both number of subtasks and their interdependence
"""

# Environment-aware parsing rules
PARSING_RULES = {
    "tool_unavailable": "If a required tool is unavailable, suggest alternative approach using available tools",
    "high_complexity": "For complexity > 3, break down into more granular subtasks",
    "max_subtasks": "Limit to 10 subtasks per level to maintain manageability"
} 