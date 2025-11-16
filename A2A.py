import operator
from typing import Annotated, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# --- 1. Define the Shared Graph State ---
# The state is the information passed between all nodes/agents.
class AgentState(TypedDict):
    """
    Represents the state of the graph.
    - messages: A list of all messages (conversation history).
    - next_agent: A string indicating which agent should run next.
    """
    messages: Annotated[list[BaseMessage], operator.add]
    next_agent: str

# --- 2. Define Agents (Nodes) ---
# In a real application, these would use LLMs, tools, etc.
# For simplicity, these are mock functions.

# Initialize a chat model (replace with your actual LLM setup)
llm = fake_LLM 

def agent_router(state: AgentState) -> dict:
    """The supervisor or router that decides the next step/agent."""
    last_message = state["messages"][-1].content
    
    # Simple routing logic based on keywords
    if "code" in last_message.lower() or "python" in last_message.lower():
        next_agent = "coder"
    elif "document" in last_message.lower() or "explain" in last_message.lower():
        next_agent = "documenter"
    else:
        next_agent = "end" # Default response
        
    print(f"--- Router decided: {next_agent} ---")
    return {"next_agent": next_agent}

def coder_agent(state: AgentState) -> dict:
    """A specialized agent for generating code."""
    # Logic to use LLM to generate code based on state["messages"]
    code_task = state["messages"][-1].content
    response_content = f"CODE GENERATOR: I'm writing a Python script for '{code_task}'..."
    return {"messages": [HumanMessage(content=response_content)], "next_agent": "documenter"}

def documenter_agent(state: AgentState) -> dict:
    """A specialized agent for writing documentation."""
    # Logic to use LLM to document the work done
    previous_output = state["messages"][-1].content
    response_content = f"DOCUMENTER: I'm documenting the previous step: '{previous_output}'"
    return {"messages": [HumanMessage(content=response_content)], "next_agent": "end"}

# --- 3. Define the Conditional Edge Logic ---
def route_agents(state: AgentState) -> Literal["coder", "documenter", END]:
    """Determines the next node based on the state's 'next_agent' key."""
    if state["next_agent"] == "coder":
        return "coder"
    if state["next_agent"] == "documenter":
        return "documenter"
    return END

# --- 4. Build and Compile the Graph ---
workflow = StateGraph(AgentState)

# Add nodes (our agents/functions)
workflow.add_node("router", agent_router)
workflow.add_node("coder", coder_agent)
workflow.add_node("documenter", documenter_agent)

# Set entry point
workflow.set_entry_point("router")

# Router determines the next step conditionally
workflow.add_conditional_edges(
    "router", 
    route_agents,
    {
        "coder": "coder",
        "documenter": "documenter",
        END: END
    }
)

# Coder passes control to the Documenter
workflow.add_edge("coder", "documenter")

# Documenter finishes the workflow and sends the state back to the router for a final response, or ENDs.
workflow.add_edge("documenter", END)

# Compile the graph
app = workflow.compile()

# --- 5. Run the Multi-Agent Workflow ---
initial_message = HumanMessage(content="I need Python code to connect to a database and write documentation for it.")

result = app.invoke({"messages": [initial_message]})

# Print the final conversation history
print("\n=== Final Conversation Log ===")
for message in result["messages"]:
    print(f"[{message.type.upper()}]: {message.content}")