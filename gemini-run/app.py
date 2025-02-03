from operator import Add
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

load_dotenv()

model = ChatOpenAI()


class State(TypedDict):
    """Represents the graph state."""

    messages: Annotated[list[BaseMessage], add_messages]
    memory: list[str]


# Define tools
@tool
def simple_tool(info: str) -> str:
    """This is a simple tool."""
    return f"Used simple tool with info: {info}"


tool_node = ToolNode([simple_tool])


def fast_thinking(state: State) -> dict:
    """Use the most recent message to decide whether to take an action or engage in slow thinking"""
    last_message = state["messages"][-1]
    if isinstance(last_message, HumanMessage) and last_message.content.startswith(
        "fast"
    ):
        return {"messages": [simple_tool.invoke("fast thinking message")]}
    return {}  # This will route to the slow thinking node.


def slow_thinking(state: State) -> Command[Literal["action", "__end__"]]:
    """Use the memory and the prompt to decide whether to take an action or end."""

    message_text = state["messages"][-1].content
    response = model.invoke(
        f"""
        Use the following information as context: {state.get("memory", "")}

        Based on the user message: {message_text}, decide what to do next.
        If there is more information needed from the user reply with "action". 
        If you are done reply with "__end__" and return the same information that is in the user message.
        """
    )

    if response.content == "action":
        return Command("action", {"messages": [response]})

    return Command(END, {"messages": [response]})


def memory_update(state: State) -> dict:
    """Add information about the state to memory."""
    messages = state.get("messages", [])
    new_memories = [m.content for m in messages if m.type != "tool"]
    return {"memory": new_memories + state.get("memory", [])}


# Build workflow
workflow = StateGraph(State)

# Add nodes to graph
workflow.add_node("fast_thinking", fast_thinking)
workflow.add_node("slow_thinking", slow_thinking)
workflow.add_node("action", tool_node)
workflow.add_node("memory_update", memory_update)

# Add edges to graph
workflow.add_edge(START, "fast_thinking")
workflow.add_conditional_edges(
    "fast_thinking",
    lambda x: True if x else "slow_thinking",
    {"slow_thinking": "slow_thinking"},
)
workflow.add_conditional_edges(
    "slow_thinking", lambda x: x, {"action": "action", END: END}
)
workflow.add_edge("action", "memory_update")
workflow.add_edge("memory_update", "slow_thinking")

# Compile the workflow
app = workflow.compile(checkpointer=MemorySaver())
