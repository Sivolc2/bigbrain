import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

from brain.llm.decomposer import TaskDecomposer

def main():
    # Initialize the decomposer
    decomposer = TaskDecomposer(
        model=os.getenv("DEFAULT_MODEL", "claude-3-sonnet-20240229"),
        temperature=float(os.getenv("MODEL_TEMPERATURE", "0.2"))
    )
    
    # Example task
    task = """Create a Python web application that:
    1. Has a login system
    2. Allows users to upload files
    3. Displays a dashboard of uploaded files"""
    
    # Available tools
    available_tools = [
        "code_generator",
        "test_runner",
        "dependency_manager",
        "database_manager",
        "auth_system"
    ]
    
    # Run the decomposition
    analysis = decomposer.decompose_task(task, available_tools)
    
    if analysis:
        print("\nTask Analysis Results:")
        print("-" * 50)
        print(f"Complexity Score: {analysis.complexity_score}/5")
        print(f"\nRequired Tools: {', '.join(analysis.required_tools)}")
        
        print("\nSubtasks:")
        for i, subtask in enumerate(analysis.subtasks, 1):
            print(f"\n{i}. {subtask.name}")
            print(f"   Tool: {subtask.tool}")
            if subtask.dependencies:
                print(f"   Dependencies: {', '.join(subtask.dependencies)}")
            print(f"   Description: {subtask.description}")
        
        print(f"\nReasoning:\n{analysis.reasoning}")
    else:
        print("Failed to analyze task")

if __name__ == "__main__":
    main() 