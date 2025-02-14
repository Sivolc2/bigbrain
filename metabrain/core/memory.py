from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime
from dataclasses import dataclass
import json
import os

T = TypeVar('T')

@dataclass
class MemoryEntry(Generic[T]):
    """Base class for memory entries"""
    content: T
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict:
        return {
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry[T]':
        return cls(
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )

class VectorDB:
    """Simple vector database for semantic storage and retrieval"""
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.entries: List[MemoryEntry] = []
        # TODO: Implement actual vector storage and similarity search
        
    def add(self, entry: MemoryEntry) -> None:
        """Add entry to vector store"""
        self.entries.append(entry)
        
    def search(self, query: Any, top_k: int = 5) -> List[MemoryEntry]:
        """Search for similar entries"""
        # TODO: Implement actual similarity search
        return self.entries[:top_k]

class HierarchicalMemory:
    """Multi-level memory system"""
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/memory.json"
        self.episodic: List[MemoryEntry] = []  # Short-term experience log
        self.semantic = VectorDB()  # Long-term conceptual knowledge
        self.procedural: Dict[str, Any] = {}  # Skill/workflow performance stats
        
        self._load_memory()
        
    def _load_memory(self) -> None:
        """Load memory from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.episodic = [MemoryEntry.from_dict(e) for e in data.get('episodic', [])]
                    self.procedural = data.get('procedural', {})
                    # Note: Semantic memory (VectorDB) needs special handling
            except Exception as e:
                print(f"Error loading memory: {e}")
                
    def save(self) -> None:
        """Save memory to storage"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = {
            'episodic': [e.to_dict() for e in self.episodic],
            'procedural': self.procedural
            # Note: Semantic memory (VectorDB) needs special handling
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def add_episodic(self, entry: MemoryEntry) -> None:
        """Add episodic memory entry"""
        self.episodic.append(entry)
        if len(self.episodic) > 1000:  # Basic memory management
            self._consolidate_memory()
            
    def add_semantic(self, entry: MemoryEntry) -> None:
        """Add semantic memory entry"""
        self.semantic.add(entry)
        
    def update_procedural(self, key: str, value: Any) -> None:
        """Update procedural memory"""
        self.procedural[key] = value
        
    def _consolidate_memory(self) -> None:
        """Consolidate episodic memories into semantic memory"""
        # TODO: Implement smart memory consolidation
        # For now, just keep recent memories
        self.episodic = self.episodic[-500:]  # Keep last 500 entries
        
    def search_semantic(self, query: Any, top_k: int = 5) -> List[MemoryEntry]:
        """Search semantic memory"""
        return self.semantic.search(query, top_k)
        
    def get_recent_episodic(self, limit: int = 10) -> List[MemoryEntry]:
        """Get recent episodic memories"""
        return self.episodic[-limit:]
        
    def get_procedural(self, key: str) -> Optional[Any]:
        """Get procedural memory value"""
        return self.procedural.get(key) 