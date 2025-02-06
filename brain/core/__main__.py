from pathlib import Path
from rich.console import Console

from .brain import BrainCore
from .schemas import WorkflowConfig, WorkflowStep

def main():
    console = Console()
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize brain
    brain = BrainCore(str(data_dir))
    
    # Register some example workflows
    research_workflow = WorkflowConfig(
        name="research",
        description="Basic research workflow",
        steps=[
            WorkflowStep(
                agent_type="researcher",
                tools=["web_search", "document_reader"]
            ),
            WorkflowStep(
                agent_type="analyst",
                tools=["calculator", "summarizer"]
            )
        ]
    )
    brain.steward.register_workflow(research_workflow)
    
    # Main loop
    console.print("[bold blue]Brain Core Initialized[/bold blue]")
    console.print("Type 'exit' to quit\n")
    
    while True:
        try:
            # Pre-phase
            brain.pre_phase()
            
            # Action phase
            result = brain.action_phase()
            if result is None:  # User chose to exit
                break
                
            # Conclusion phase
            brain.conclusion_phase(result)
            
            console.print("\n---\n")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down gracefully...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            continue

if __name__ == "__main__":
    main() 