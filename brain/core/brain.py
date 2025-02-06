from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from .steward import Steward
from .agent import Agent
from .schemas import ActionType, ExecutionResult, WorkflowConfig

class BrainCore:
    def __init__(self, data_dir: str = "data"):
        self.steward = Steward(data_dir)
        self.console = Console()
        
    def pre_phase(self) -> None:
        """Load and display current brain state."""
        stats = self.steward.get_stats()
        recent_tasks = self.steward.get_recent_tasks()
        
        # Display stats
        stats_table = Table(title="Brain Statistics")
        stats_table.add_column("Metric")
        stats_table.add_column("Value")
        
        stats_table.add_row("Total Cost", f"${stats.total_cost:.3f}")
        stats_table.add_row("Tasks Run", str(stats.tasks_run))
        stats_table.add_row("Success Rate", f"{(stats.successes/max(1, stats.tasks_run))*100:.1f}%")
        
        self.console.print(stats_table)
        
        # Display recent tasks
        if recent_tasks:
            task_table = Table(title="Recent Tasks")
            task_table.add_column("ID")
            task_table.add_column("Result")
            task_table.add_column("Success")
            task_table.add_column("Cost")
            
            for task_id, task in recent_tasks.items():
                task_table.add_row(
                    task_id,
                    str(task.result)[:50] + "..." if len(str(task.result)) > 50 else str(task.result),
                    "✅" if task.success else "❌",
                    f"${task.cost:.3f}"
                )
            
            self.console.print(task_table)
    
    def action_phase(self) -> Optional[ExecutionResult]:
        """Handle user interaction and execute chosen action."""
        action = Prompt.ask(
            "[bold]Choose action[/]",
            choices=[e.value for e in ActionType]
        )
        
        if action == ActionType.EXIT:
            return None
            
        elif action == ActionType.AGENT:
            agent_type = Prompt.ask("Enter agent type")
            tools = Prompt.ask("Enter tools (comma-separated)").split(",")
            objective = Prompt.ask("Enter objective")
            
            agent = Agent(agent_type.strip(), [t.strip() for t in tools])
            return agent.run(objective)
            
        elif action == ActionType.WORKFLOW:
            workflow_names = list(self.steward.brain_memory.workflows.keys())
            if not workflow_names:
                self.console.print("[yellow]No workflows registered. Create an agent instead.[/yellow]")
                return self.action_phase()
                
            workflow_name = Prompt.ask(
                "Choose workflow",
                choices=workflow_names
            )
            
            workflow = self.steward.get_workflow(workflow_name)
            if not workflow:
                self.console.print(f"[red]Workflow {workflow_name} not found![/red]")
                return self.action_phase()
                
            return self._execute_workflow(workflow)
    
    def _execute_workflow(self, workflow: WorkflowConfig) -> ExecutionResult:
        """Execute a predefined workflow."""
        self.console.print(f"[bold]Executing workflow: {workflow.name}[/bold]")
        
        total_cost = 0.0
        all_results = []
        success = True
        
        for step in workflow.steps:
            agent = Agent(step.agent_type, step.tools)
            result = agent.run(f"Workflow step for {workflow.name}")
            
            total_cost += result.cost
            all_results.append(result)
            if not result.success:
                success = False
                break
        
        return ExecutionResult(
            result=all_results,
            cost=total_cost,
            success=success,
            action_type=ActionType.WORKFLOW,
            metadata={
                "workflow_name": workflow.name,
                "steps_completed": len(all_results)
            }
        )
    
    def conclusion_phase(self, result: ExecutionResult) -> None:
        """Process and store execution results."""
        self.steward.add_execution_result(result)
        
        # Display result summary
        if result.success:
            self.console.print(f"[green]Success![/green] Cost: ${result.cost:.3f}")
        else:
            self.console.print(f"[red]Failed![/red] Cost: ${result.cost:.3f}")
        
        self.console.print("Result:", str(result.result)) 