import operator
from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# --- 1. Define the Shared Graph State ---
class AgentState(TypedDict):
    """The state holds the conversation history."""
    messages: Annotated[List[BaseMessage], operator.add]

# --- 2. Define the Specialized Agents (as callable functions) ---

def coder_agent_function(prompt: str) -> str:
    """A specialized function that simulates the Coder Agent's work."""
    # In a real setup, this would be an LLM call or complex logic
    return f"CODE GENERATED: Here is the Python boilerplate for: {prompt[:50]}..."

def documenter_agent_function(text_to_document: str) -> str:
    """A specialized function that simulates the Documenter Agent's work."""
    # In a real setup, this would be an LLM call or complex logic
    return f"DOCUMENTATION COMPLETE: The previous output was summarized and documented."

# --- 3. Wrap Agents as Tools ---

# LangChain's @tool decorator makes the functions callable by the LLM
@tool
def code_generator(prompt: str) -> str:
    """
    Call this tool when you need to generate Python or other code.
    Input: The user request for code.
    """
    return coder_agent_function(prompt)

@tool
def document_writer(text_to_document: str) -> str:
    """
    Call this tool to write documentation for a piece of code or text.
    Input: The text/code that needs to be documented.
    """
    return documenter_agent_function(text_to_document)

# List of tools available to the Executor Agent
available_tools = [code_generator, document_writer]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(available_tools)

# --- 4. The Central Execution Node (The Agent) ---

def executor_agent_node(state: AgentState) -> dict:
    """
    This is the main Agent that uses its LLM to decide
    whether to respond directly or use an Agent-Tool.
    """
    last_message = state["messages"][-1]
    
    # Check if the last message was a ToolMessage (i.e., output from another agent)
    if isinstance(last_message, ToolMessage):
        # If it was tool output, simply pass it to the LLM to process
        response = llm.invoke(state["messages"])
    else:
        # If it was a HumanMessage, invoke the LLM with the history
        response = llm.invoke(state["messages"])

    # If the LLM decided to call a tool (another agent), return the call
    if response.tool_calls:
        print(f"--- Executor Agent decided to call a tool: {response.tool_calls[0].name} ---")
        return {"messages": [response]}
    else:
        # If the LLM decided to respond directly, return the response
        print("--- Executor Agent decided to finish and respond directly ---")
        return {"messages": [response]}

# --- 5. The Tool Execution Node (The Handover) ---

def tool_executor_node(state: AgentState) -> dict:
    """
    Executes the tool call (i.e., runs the targeted Agent-Function).
    """
    tool_calls = state["messages"][-1].tool_calls
    
    # Assuming one tool call for simplicity
    tool_call = tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    
    # Map the tool name back to the actual function
    tool_map = {t.name: t for t in available_tools}
    
    # Execute the tool function (the other agent)
    output = tool_map[tool_name].invoke(tool_args)
    
    # Return the result as a ToolMessage so the Executor Agent can see it
    print(f"--- Tool Execution complete (from Agent {tool_name}): {output[:40]}... ---")
    
    return {"messages": [ToolMessage(content=output, tool_call_id=tool_call["id"])]}

# --- 6. Build the Graph ---

workflow = StateGraph(AgentState)
workflow.add_node("executor", executor_agent_node)
workflow.add_node("tool_executor", tool_executor_node)

# Start always goes to the main Executor Agent
workflow.set_entry_point("executor")

# Define the routing logic (always check the last AIMessage for tool calls)
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "continue_tool" # Go to tool_executor
    return "end" # Finish

# Add edges
workflow.add_conditional_edges("executor", should_continue, {"continue_tool": "tool_executor", "end": END})
workflow.add_edge("tool_executor", "executor") # After tool execution, go back to the Executor

app = workflow.compile()

# --- 7. Run the Multi-Agent Workflow ---
initial_message = HumanMessage(content="First, write me a small Python function for array sorting, and then document the function.")
print("Starting Workflow...")

# The LLM will decide to call the `code_generator` tool first.
# The tool_executor runs `coder_agent_function`.
# The result goes back to the executor, which then sees the code and calls `document_writer`.
result = app.invoke({"messages": [initial_message]})

print("\n=== Final Response ===")
print(result["messages"][-1].content)