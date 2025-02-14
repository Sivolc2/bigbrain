from collections import OrderedDict, defaultdict
from typing import Any, Dict, List, Optional, Set
import copy
from .interfaces import Node, NodeContext

class Workflow(Node):
    """A workflow is itself a node that contains and orchestrates other nodes"""
    def __init__(self, name: str, description: Optional[str] = None):
        super().__init__(name)
        self.name = name
        self.description = description
        self.nodes: OrderedDict[str, Node] = OrderedDict()
        self.entry_nodes: Set[str] = set()  # Support multiple entry points
        self.tags: List[str] = []
        self.version: float = 1.0
        
    def add_node(self, node: Node, is_entry: bool = False) -> None:
        """Add a node to the workflow"""
        self.nodes[node.id] = node
        if is_entry:
            self.entry_nodes.add(node.id)
            
    def process(self, input_data: Any, context: NodeContext) -> tuple[Any, bool]:
        """Execute the workflow"""
        if not self.entry_nodes:
            raise ValueError("Workflow has no entry nodes")
            
        current_nodes = list(self.entry_nodes)
        context.workflow_id = self.id
        
        while current_nodes:
            next_nodes: Set[str] = set()
            
            for node_id in current_nodes:
                node = self.nodes[node_id]
                output, should_continue = node.process(input_data, context)
                
                if not should_continue:
                    return output, False
                    
                # Propagate output to connected nodes
                for output_slot, targets in node.connections.items():
                    next_nodes.update(t_id for t_id in targets if t_id in self.nodes)
                    
            current_nodes = list(next_nodes)
            
        return input_data, True  # Return final state when no more nodes to process

class WorkflowLibrary:
    """Manages and stores workflow definitions"""
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.version_history: Dict[str, List[Dict]] = defaultdict(list)
        
    def register_workflow(self, workflow: Workflow) -> None:
        """Register a new workflow or update existing one"""
        self.workflows[workflow.name] = workflow
        self.version_history[workflow.name].append({
            'version': len(self.version_history[workflow.name]) + 1,
            'workflow': copy.deepcopy(workflow)
        })
        
    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get a workflow by name"""
        return self.workflows.get(name)
        
    def get_workflows_by_tags(self, tags: List[str]) -> List[Workflow]:
        """Get all workflows that match all given tags"""
        return [
            wf for wf in self.workflows.values()
            if all(tag in wf.tags for tag in tags)
        ]
        
    def get_workflow_version(self, name: str, version: int) -> Optional[Workflow]:
        """Get a specific version of a workflow"""
        history = self.version_history.get(name, [])
        for entry in history:
            if entry['version'] == version:
                return entry['workflow']
        return None 