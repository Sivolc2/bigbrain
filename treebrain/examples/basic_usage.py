import asyncio
import os
import json
from treebrain.core.orchestrator import Orchestrator

def ensure_context_files(project_root: str) -> None:
    """Create necessary context files if they don't exist."""
    # Create directories
    os.makedirs(os.path.join(project_root, "frontend"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "backend"), exist_ok=True)
    
    # Define context files and their default content
    context_files = {
        "frontend/agent_definition.json": {
            "role": "frontend",
            "responsibilities": [
                "Implement user interface components",
                "Handle client-side state management",
                "Implement user interactions and events"
            ],
            "working_directory": "frontend/",
            "file_patterns": ["*.tsx", "*.jsx", "*.css", "*.html"]
        },
        "frontend/agent_history.json": {
            "completed_tasks": [],
            "current_context": {"active_components": []},
            "learning_history": []
        },
        "backend/agent_definition.json": {
            "role": "backend",
            "responsibilities": [
                "Implement API endpoints",
                "Handle data persistence",
                "Implement business logic"
            ],
            "working_directory": "backend/",
            "file_patterns": ["*.py", "*.sql", "*.yaml"]
        },
        "backend/agent_history.json": {
            "completed_tasks": [],
            "current_context": {"active_endpoints": []},
            "learning_history": []
        },
        "planner_context.json": {
            "role": "planner",
            "project_structure": {
                "frontend": {"path": "frontend/", "tech_stack": ["React"]},
                "backend": {"path": "backend/", "tech_stack": ["FastAPI"]}
            }
        },
        "librarian_context.json": {
            "role": "librarian",
            "knowledge_bases": {
                "codebase": {"root_path": "./"},
                "documentation": {"paths": ["docs/", "README.md"]}
            }
        }
    }
    
    # Create each context file if it doesn't exist
    for rel_path, content in context_files.items():
        file_path = os.path.join(project_root, rel_path)
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(content, f, indent=2)

async def main():
    # Setup example project structure
    project_root = "examples/app"
    ensure_context_files(project_root)
    
    # Initialize the orchestrator with project root
    orchestrator = Orchestrator(project_root)
    
    # Example task: Create a hello world app
    task = "Create a hello world app with frontend and backend"
    
    print("Starting task:", task)
    print("-" * 50)
    
    # Process the task
    result = await orchestrator.process_task(task)
    
    # Print results
    print("\nTask Results:")
    print("-" * 50)
    if result["status"] == "success":
        print("Task completed successfully!")
        print("\nAgent Results:")
        for task_result in result["results"]:
            print(f"\nAgent: {task_result['agent']}")
            print(f"Task: {task_result['task']}")
            print(f"Status: {task_result['status']}")
            if task_result.get('output_files'):
                print("Output files:")
                for file in task_result['output_files']:
                    print(f"  - {file}")
    else:
        print("Task failed!")
        print("Error:", result["error"])
    
    # Print final project status
    print("\nFinal Project Status:")
    print("-" * 50)
    project_status = orchestrator.get_project_overview()
    print(f"Status: {project_status['status']}")
    print("\nAgent Statuses:")
    for agent, status in project_status['agent_statuses'].items():
        print(f"\n{agent}:")
        for key, value in status.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main()) 