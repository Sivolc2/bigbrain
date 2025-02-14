from metabrain.core.brain import BrainCore
from metabrain.core.workflow import Workflow
from metabrain.core.interfaces import Node, NodeContext
from typing import Any, Tuple

class TextProcessorNode(Node):
    """Example node that processes text input"""
    def process(self, input_data: Any, context: NodeContext) -> Tuple[Any, bool]:
        if not isinstance(input_data, str):
            return input_data, True
            
        # Simple text processing
        processed = input_data.upper()
        context.memory['last_processed_text'] = processed
        return processed, True

class AnalyzerNode(Node):
    """Example node that analyzes processed text"""
    def process(self, input_data: Any, context: NodeContext) -> Tuple[Any, bool]:
        if not isinstance(input_data, str):
            return input_data, True
            
        # Simple analysis
        result = {
            'length': len(input_data),
            'word_count': len(input_data.split()),
            'original': context.memory.get('last_processed_text', '')
        }
        
        return result, True

def create_text_processing_workflow() -> Workflow:
    """Create a simple text processing workflow"""
    workflow = Workflow("text_processor", "Simple text processing example")
    
    # Create nodes
    processor = TextProcessorNode()
    analyzer = AnalyzerNode()
    
    # Add nodes to workflow
    workflow.add_node(processor, is_entry=True)
    workflow.add_node(analyzer)
    
    # Connect nodes
    processor.add_connection("output", analyzer)
    
    # Add workflow tags
    workflow.tags = ["text", "processing", "example"]
    
    return workflow

def main():
    # Initialize brain
    brain = BrainCore()
    
    # Register workflow
    workflow = create_text_processing_workflow()
    brain.workflow_lib.register_workflow(workflow)
    
    # Process some input
    input_text = "Hello, MetaBrain! This is a test."
    result_context = brain.process_input(
        input_text,
        workflow_filter=["text"]  # Only use workflows tagged with "text"
    )
    
    # Print results
    print("Input:", input_text)
    print("Memory state:", result_context.memory)
    print("Processing metadata:", result_context.metadata)
    
if __name__ == "__main__":
    main() 