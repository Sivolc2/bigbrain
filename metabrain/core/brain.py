from typing import Any, Dict, List, Optional
from weakref import WeakValueDictionary
from .workflow import Workflow, WorkflowLibrary
from .interfaces import NodeContext
from .memory import HierarchicalMemory

class CognitiveOverflow(Exception):
    """Raised when brain processing capacity is exceeded"""
    pass

class BrainCore:
    """Central orchestrator for the metabrain system"""
    def __init__(self):
        self.workflow_lib = WorkflowLibrary()
        self.active_contexts: WeakValueDictionary = WeakValueDictionary()
        self.memory = HierarchicalMemory()
        self._init_core_workflows()
        
    def _init_core_workflows(self) -> None:
        """Initialize essential system workflows"""
        # Meta-cognitive workflow for system monitoring
        meta_workflow = Workflow("meta_cognition", "System monitoring and resource management")
        # TODO: Add system monitoring nodes
        self.workflow_lib.register_workflow(meta_workflow)
        
    def process_input(self, 
                     input_data: Any, 
                     workflow_filter: Optional[List[str]] = None) -> NodeContext:
        """
        Process input through appropriate workflows
        
        Args:
            input_data: The input to process
            workflow_filter: Optional list of workflow tags to filter by
            
        Returns:
            NodeContext: The context containing processing results
        """
        context = self._create_context()
        workflows = self._select_workflows(input_data, workflow_filter)
        
        if not workflows:
            raise ValueError("No matching workflows found")
            
        try:
            for workflow in workflows:
                result, should_continue = workflow.process(input_data, context)
                if not should_continue:
                    break
                input_data = self._merge_results(input_data, result)
                
        except Exception as e:
            self._handle_error(e, context)
            if isinstance(e, CognitiveOverflow):
                self._fallback_procedure(context)
            else:
                raise
            
        return context
        
    def _create_context(self) -> NodeContext:
        """Create a new processing context"""
        context = NodeContext()
        self.active_contexts[context.context_id] = context
        return context
        
    def _select_workflows(self, 
                         input_data: Any, 
                         workflow_filter: Optional[List[str]] = None) -> List[Workflow]:
        """Select appropriate workflows based on input and filter"""
        if workflow_filter:
            return self.workflow_lib.get_workflows_by_tags(workflow_filter)
        # TODO: Implement smart workflow selection based on input_data
        return list(self.workflow_lib.workflows.values())
        
    def _merge_results(self, existing: Any, new_data: Any) -> Any:
        """Merge processing results intelligently"""
        if isinstance(existing, dict) and isinstance(new_data, dict):
            return {**existing, **new_data}
        return new_data
        
    def _handle_error(self, error: Exception, context: NodeContext) -> None:
        """Handle processing errors"""
        context.metadata['last_error'] = str(error)
        # TODO: Implement error logging and recovery strategies
        
    def _fallback_procedure(self, context: NodeContext) -> None:
        """Execute fallback procedure when cognitive overflow occurs"""
        # TODO: Implement graceful degradation and resource management
        context.metadata['fallback_triggered'] = True 