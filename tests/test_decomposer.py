import pytest
from brain.llm.decomposer import TaskDecomposer
from brain.llm.prompts import TaskAnalysis

@pytest.fixture
def decomposer():
    return TaskDecomposer()

def test_task_decomposition(decomposer):
    # Sample task and tools
    task = "Create a simple REST API with two endpoints and basic authentication"
    available_tools = ["code_generator", "test_runner", "dependency_manager"]
    
    # Run decomposition
    analysis = decomposer.decompose_task(task, available_tools)
    
    # Verify we got a result
    assert analysis is not None
    assert isinstance(analysis, TaskAnalysis)
    
    # Verify basic structure
    assert len(analysis.required_tools) > 0
    assert all(tool in available_tools for tool in analysis.required_tools)
    assert 1 <= analysis.complexity_score <= 5
    assert len(analysis.subtasks) > 0
    assert len(analysis.subtasks) <= 10  # Max subtasks rule
    
    # Verify subtask structure
    for subtask in analysis.subtasks:
        assert subtask.name
        assert subtask.tool in available_tools
        assert isinstance(subtask.dependencies, list)
        assert subtask.description

def test_invalid_tools_handling(decomposer):
    task = "Simple task"
    available_tools = ["tool1"]
    
    # Try with an analysis that requires unavailable tools
    analysis = decomposer.decompose_task(task, available_tools)
    
    # Should still get a valid result, but with warnings
    assert analysis is not None
    assert all(tool in available_tools for tool in analysis.required_tools)

def test_high_complexity_handling(decomposer):
    # Complex task that should get a high score
    task = """Build a distributed system with multiple microservices,
              authentication, database sharding, and real-time updates"""
    available_tools = ["code_generator", "test_runner", "dependency_manager"]
    
    analysis = decomposer.decompose_task(task, available_tools)
    
    # Should handle high complexity appropriately
    assert analysis is not None
    assert analysis.complexity_score > 3
    assert len(analysis.subtasks) <= 10  # Still respects max subtasks 