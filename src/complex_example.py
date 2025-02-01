from typing import TypedDict, Annotated, Literal
from langgraph.graph import Graph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from enum import Enum
import json

# Define our state
class AgentState(TypedDict):
    messages: list[HumanMessage | AIMessage | SystemMessage]
    current_step: int
    task_breakdown: list[str]
    solutions: list[str]
    validation_results: list[bool]
    next: str

class Agents(str, Enum):
    PLANNER = "planner"
    SOLVER = "solver"
    VALIDATOR = "validator"
    
def create_complex_agent():
    # Create different LLMs for each agent (could use different models or temperatures)
    planner_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    solver_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
    validator_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # Define the planner agent
    def planner(state: AgentState) -> AgentState:
        messages = state["messages"]
        system_message = SystemMessage(content="""
        You are a task planning agent. Break down the given problem into smaller steps.
        Return your response as a JSON array of steps.
        """)
        
        response = planner_llm.invoke([system_message] + messages)
        try:
            task_breakdown = json.loads(response.content)
            return {
                **state,
                "task_breakdown": task_breakdown,
                "next": Agents.SOLVER
            }
        except json.JSONDecodeError:
            return {
                **state,
                "task_breakdown": [response.content],
                "next": Agents.SOLVER
            }

    # Define the solver agent
    def solver(state: AgentState) -> AgentState:
        messages = state["messages"]
        tasks = state["task_breakdown"]
        
        system_message = SystemMessage(content="""
        You are a problem-solving agent. Solve each step of the task.
        Explain your solution clearly.
        """)
        
        solutions = []
        for task in tasks:
            task_message = HumanMessage(content=f"Solve this step: {task}")
            response = solver_llm.invoke([system_message, task_message])
            solutions.append(response.content)
        
        return {
            **state,
            "solutions": solutions,
            "next": Agents.VALIDATOR
        }

    # Define the validator agent
    def validator(state: AgentState) -> AgentState:
        original_problem = state["messages"][0].content
        solutions = state["solutions"]
        
        system_message = SystemMessage(content="""
        You are a validation agent. Verify if the solutions are correct and complete.
        Return your response as 'VALID' or 'INVALID' followed by your explanation.
        """)
        
        validation_message = HumanMessage(content=f"""
        Original problem: {original_problem}
        Solutions: {solutions}
        Are these solutions correct and complete?
        """)
        
        response = validator_llm.invoke([system_message, validation_message])
        is_valid = response.content.startswith("VALID")
        
        return {
            **state,
            "validation_results": [is_valid],
            "messages": state["messages"] + [AIMessage(content=f"""
            Task Breakdown: {state['task_breakdown']}
            Solutions: {solutions}
            Validation: {response.content}
            """)],
            "next": END
        }

    # Define the router
    def router(state: AgentState) -> Literal["planner", "solver", "validator"]:
        return state["next"]

    # Create the graph
    workflow = Graph()
    
    # Add the nodes
    workflow.add_node(Agents.PLANNER, planner)
    workflow.add_node(Agents.SOLVER, solver)
    workflow.add_node(Agents.VALIDATOR, validator)
    
    # Set up the edges
    workflow.set_entry_point(Agents.PLANNER)
    workflow.add_conditional_edges(
        "planner",
        router,
        {
            Agents.SOLVER: Agents.SOLVER,
        }
    )
    workflow.add_conditional_edges(
        "solver",
        router,
        {
            Agents.VALIDATOR: Agents.VALIDATOR,
        }
    )
    workflow.add_conditional_edges(
        "validator",
        router,
        {
            END: END,
        }
    )
    
    # Compile the graph
    chain = workflow.compile()
    return chain

if __name__ == "__main__":
    chain = create_complex_agent()
    
    # Initial state
    state = {
        "messages": [
            HumanMessage(content="""
            Design a simple web application that allows users to create and manage a todo list.
            Consider the database design and API endpoints needed.
            """)
        ],
        "current_step": 0,
        "task_breakdown": [],
        "solutions": [],
        "validation_results": [],
        "next": Agents.PLANNER
    }
    
    # Run the chain
    result = chain.invoke(state)
    
    # Print the final result
    if result and "messages" in result:
        print("\n=== Final Output ===")
        print(result["messages"][-1].content)
    else:
        print("No response received") 