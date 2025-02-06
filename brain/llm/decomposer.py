from typing import List, Dict, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from .prompts import TaskAnalysis, TASK_ANALYSIS_PROMPT, PARSING_RULES, llm
import json
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class TaskDecomposer:
    """Handles task decomposition with validation and retry logic."""
    
    def __init__(self, model: str = "claude-3-sonnet-20240229", temperature: float = 0.2):
        self.llm = llm  # Use the pre-configured LLM from prompts.py
        self.max_retries = 3
    
    def decompose_task(self, task: str, available_tools: List[str]) -> Optional[TaskAnalysis]:
        """
        Decomposes a task into subtasks with validation and retry logic.
        
        Args:
            task: The task to decompose
            available_tools: List of available tool names
            
        Returns:
            TaskAnalysis object if successful, None if all retries fail
        """
        prompt = TASK_ANALYSIS_PROMPT.format(
            task=task,
            available_tools=json.dumps(available_tools, indent=2)
        )
        
        for attempt in range(self.max_retries):
            try:
                # Get LLM response using LangChain's message format
                response = self.llm.invoke([HumanMessage(content=prompt)])
                
                # Parse JSON response
                try:
                    analysis_dict = json.loads(response.content)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON on attempt {attempt + 1}: {e}")
                    continue
                
                # Validate with Pydantic
                analysis = TaskAnalysis(**analysis_dict)
                
                # Apply environment-aware parsing rules
                analysis = self._apply_parsing_rules(analysis, available_tools)
                
                return analysis
                
            except ValidationError as e:
                logger.warning(f"Validation error on attempt {attempt + 1}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                continue
        
        logger.error("All decomposition attempts failed")
        return None
    
    def _apply_parsing_rules(self, analysis: TaskAnalysis, available_tools: List[str]) -> TaskAnalysis:
        """Applies environment-aware parsing rules to the analysis."""
        
        # Check for unavailable tools
        for tool in analysis.required_tools:
            if tool not in available_tools:
                logger.warning(f"Tool {tool} not available, analysis may need adjustment")
                # In a full implementation, we would modify the analysis here
                
        # Handle high complexity tasks
        if analysis.complexity_score > 3:
            logger.info("High complexity task detected, may need further breakdown")
            # In a full implementation, we might recursively break down complex subtasks
            
        # Enforce maximum subtasks
        if len(analysis.subtasks) > 10:
            logger.warning("Too many subtasks, truncating to 10")
            analysis.subtasks = analysis.subtasks[:10]
        
        return analysis 