# MetaBrain

A flexible and extensible framework for building workflow-based cognitive systems.

## Core Features

- **Node-Based Architecture**: Everything is a node that can process data and connect to other nodes
- **Workflow Management**: Create, version, and execute complex workflows
- **Hierarchical Memory**: Multi-level memory system with episodic, semantic, and procedural storage
- **Extensible Design**: Easy to add new node types and workflows
- **Context Awareness**: Rich context objects for tracking state and metadata

## Project Structure

```
metabrain/
├── core/
│   ├── interfaces.py     # Base classes and interfaces
│   ├── workflow.py       # Workflow and WorkflowLibrary
│   ├── brain.py         # Central BrainCore orchestrator
│   └── memory.py        # Hierarchical memory system
├── examples/
│   └── basic_usage.py   # Example implementation
└── README.md
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the example:
```bash
python examples/basic_usage.py
```

## Creating Custom Nodes

Inherit from the base `Node` class to create custom processing nodes:

```python
from metabrain.core.interfaces import Node, NodeContext

class MyCustomNode(Node):
    def process(self, input_data: Any, context: NodeContext) -> Tuple[Any, bool]:
        # Process input_data
        result = do_something(input_data)
        return result, True
```

## Creating Workflows

Build workflows by connecting nodes:

```python
from metabrain.core.workflow import Workflow

def create_workflow():
    workflow = Workflow("my_workflow")
    
    # Add nodes
    node1 = MyCustomNode()
    node2 = AnotherNode()
    
    workflow.add_node(node1, is_entry=True)
    workflow.add_node(node2)
    
    # Connect nodes
    node1.add_connection("output", node2)
    
    return workflow
```

## Using the Brain

```python
from metabrain.core.brain import BrainCore

# Initialize
brain = BrainCore()

# Register workflow
workflow = create_workflow()
brain.workflow_lib.register_workflow(workflow)

# Process input
result = brain.process_input(
    input_data,
    workflow_filter=["my_tag"]
)
```

## Memory System

The system includes a hierarchical memory with three levels:

1. **Episodic Memory**: Short-term experience log
2. **Semantic Memory**: Long-term conceptual knowledge (vector store)
3. **Procedural Memory**: Workflow performance statistics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details 