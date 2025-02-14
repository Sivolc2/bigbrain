from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional
from uuid import UUID
import uuid
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class NodeContext:
    """Context object passed between nodes during processing"""
    context_id: UUID = field(default_factory=uuid.uuid4)
    workflow_id: Optional[UUID] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)

class Node(ABC):
    """Base class for all processing nodes in the system"""
    def __init__(self, node_id: Optional[str] = None):
        self.id = node_id or str(uuid.uuid4())
        self.connections: Dict[str, List[str]] = {}
        self._state: Dict[str, Any] = {}
        
    @abstractmethod
    def process(self, input_data: Any, context: NodeContext) -> Tuple[Any, bool]:
        """
        Process input data and return output along with continuation flag
        
        Args:
            input_data: Input data to process
            context: Processing context
            
        Returns:
            Tuple[Any, bool]: (output_data, should_continue)
        """
        raise NotImplementedError
        
    def add_connection(self, output_slot: str, target_node: 'Node') -> None:
        """Add a connection from this node to another node"""
        if not isinstance(target_node, Node):
            raise ValueError(f"Target must be a Node instance, got {type(target_node)}")
        self.connections.setdefault(output_slot, []).append(target_node.id)
        
    def get_state(self, key: str) -> Any:
        """Get node state value"""
        return self._state.get(key)
        
    def set_state(self, key: str, value: Any) -> None:
        """Set node state value"""
        self._state[key] = value 