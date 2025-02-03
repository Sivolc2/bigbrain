from operator import add
from typing import Annotated, Any, Dict, List, Literal, TypedDict, Union

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

load_dotenv()

# Initialize different models for different purposes
router_model = ChatOpenAI(
    model="gpt-4o-mini", temperature=0
)  # Fast, cheap model for routing
fast_model = ChatOpenAI(
    model="gpt-4o-mini", temperature=0.7
)  # Fast model for simple queries
slow_model = ChatOpenAI(
    model="gpt-4o", temperature=0.7
)  # Powerful model for complex queries

members = ["fast_thinker", "slow_thinker"]
options = members  # No FINISH needed since we use END directly


def format_message(msg: BaseMessage) -> str:
    """Format a message for display, handling different content types."""
    content = msg.content
    if isinstance(content, str):
        return f"{msg.type}: {content}"
    elif isinstance(content, list):
        # Handle list of strings/dicts (e.g., for multi-modal content)
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
        return f"{msg.type}: {''.join(parts)}"
    return f"{msg.type}: [Complex content]"


class RouterOutput(TypedDict):
    """The router's decision about which thinking style to use."""

    next: Literal["fast_thinker", "slow_thinker"]


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    next: str


def create_router():
    router_prompt = """You are a router that determines whether a query needs fast or slow thinking.
    
    For simple, straightforward queries that don't require deep analysis or complex reasoning, route to the fast_thinker.
    Examples of fast thinking queries:
    - Basic factual questions
    - Simple clarifications
    - Routine tasks
    - Quick calculations
    - Basic code formatting
    
    For complex queries that require deep analysis, creativity, or sophisticated reasoning, route to the slow_thinker.
    Examples of slow thinking queries:
    - Complex problem solving
    - System design questions
    - Code architecture decisions
    - Bug analysis and debugging
    - Performance optimization
    - Security considerations
    
    Based on the conversation above, which agent should handle this query?
    
    You must respond with a valid JSON object containing a 'next' field with either 'fast_thinker' or 'slow_thinker' as the value.
    """

    def route(state: AgentState) -> Command[Literal["fast_thinker", "slow_thinker"]]:
        messages = state["messages"]
        # Use structured output to ensure valid routing decision
        response = router_model.with_structured_output(RouterOutput).invoke(
            [
                HumanMessage(
                    content=router_prompt
                    + "\n\nCurrent conversation:\n"
                    + "\n".join(format_message(m) for m in messages)
                )
            ]
        )
        return Command(goto=response["next"])

    return route


def create_fast_thinker():
    fast_prompt = """You are a fast-thinking AI assistant optimized for quick, straightforward responses.
    Focus on providing direct, efficient answers without excessive analysis.
    
    Current conversation:
    {messages}
    
    Please provide a quick response to help the user."""

    def fast_think(state: AgentState) -> Dict:
        messages = state["messages"]
        response = fast_model.invoke(
            [
                HumanMessage(
                    content=fast_prompt.format(
                        messages="\n".join(format_message(m) for m in messages)
                    )
                )
            ]
        )
        return {"messages": [AIMessage(content=response.content)]}

    return fast_think


def create_slow_thinker():
    slow_prompt = """You are a slow-thinking AI assistant optimized for deep analysis and complex problem-solving.
    Take your time to think through problems carefully and provide comprehensive, well-reasoned responses.
    
    Current conversation:
    {messages}
    
    Please provide a thorough analysis and response to help the user."""

    def slow_think(state: AgentState) -> Dict:
        messages = state["messages"]
        response = slow_model.invoke(
            [
                HumanMessage(
                    content=slow_prompt.format(
                        messages="\n".join(format_message(m) for m in messages)
                    )
                )
            ]
        )
        return {"messages": [AIMessage(content=response.content)]}

    return slow_think


# Create the workflow
workflow = StateGraph(AgentState)

# Add the router node
workflow.add_node("router", create_router())

# Add agent nodes
workflow.add_node("fast_thinker", create_fast_thinker())
workflow.add_node("slow_thinker", create_slow_thinker())

# Add edges
workflow.add_edge("router", "fast_thinker")
workflow.add_edge("router", "slow_thinker")
workflow.add_edge("fast_thinker", END)
workflow.add_edge("slow_thinker", END)

# Set entry point
workflow.set_entry_point("router")

# Compile the graph
app = workflow.compile()


def main():
    # Initialize the state
    state = {"messages": [], "next": None}

    # Sample queries to test both fast and slow thinking
    test_queries = [
        "What is 2 + 2?",  # Should route to fast thinker
        "Can you help me design a scalable microservices architecture for a high-traffic e-commerce platform?",  # Should route to slow thinker
        "What time is it in UTC?",  # Should route to fast thinker
        "How can I optimize my PostgreSQL database for better query performance?",  # Should route to slow thinker
    ]

    print("🤖 Testing Multi-Agent Routing System\n")

    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query #{i}: {query}")
        print("-" * 80)

        # Add the new query to the conversation
        state["messages"].append(HumanMessage(content=query))

        # Process the query through the workflow
        result = app.invoke(state)

        # Get the last message (the agent's response)
        last_message = result["messages"][-1]
        formatted_response = format_message(last_message).split(": ", 1)[
            1
        ]  # Remove the type prefix
        print(f"\n🤔 Response: {formatted_response}\n")

        # Update the state with the new conversation
        state = result


if __name__ == "__main__":
    main()
