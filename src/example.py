from typing import TypedDict, Annotated
from langgraph.graph import Graph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# Define our state
class AgentState(TypedDict):
    messages: list[HumanMessage | AIMessage]
    current_step: int

# Create a simple math solver agent
def create_agent():
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    # Define the agent function
    def solve_math(state: AgentState) -> AgentState:
        messages = state["messages"]
        response = llm.invoke(messages)
        # Return the complete state, not just messages
        return {
            "messages": messages + [response],
            "current_step": state["current_step"] + 1
        }
    
    # Create the graph
    workflow = Graph()
    
    # Add the node
    workflow.add_node("solve", solve_math)
    
    # Set up the edges - we need to connect solve to END
    workflow.set_entry_point("solve")
    workflow.add_edge("solve", END)
    
    # Compile the graph
    chain = workflow.compile()
    
    return chain

# Example usage
if __name__ == "__main__":
    chain = create_agent()
    
    # Initial state
    state = {
        "messages": [
            HumanMessage(content="What is 123 + 456?")
        ],
        "current_step": 0
    }
    
    # Run the chain
    result = chain.invoke(state)
    
    # Print the result
    if result and "messages" in result:
        for message in result["messages"]:
            print(f"{message.type}: {message.content}")
    else:
        print("No response received") 