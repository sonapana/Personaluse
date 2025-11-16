from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import StdioServerParameters
import asyncio
from dotenv import load_dotenv # Load your API keys

load_dotenv() # Ensure OPENAI_API_KEY is set

async def run_mcp_agent():
    # 1. Define the connection parameters for the MCP server
    # We use StdioServerParameters since our server runs as a local process
    server_config = {
        "math_service": {
            "transport": "stdio",
            # The command to execute to start the server
            "command": "python", 
            # Path to your math_server.py file
            "args": ["math_server.py"], 
        }
    }

    # 2. Initialize the MultiServerMCPClient
    # This client handles the protocol communication
    mcp_client = MultiServerMCPClient(server_config)
    
    # 3. Connect to the server(s) and discover the tools
    # The tools are loaded into a format LangChain understands
    print("Connecting to MCP server and loading tools...")
    async with mcp_client.session("math_service") as session:
        mcp_tools = await load_mcp_tools(session)
        print(f"Discovered tools: {[t.name for t in mcp_tools]}")

        # 4. Initialize the LLM and create the Agent
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # We use a pre-built agent creator (ReAct style) from LangGraph
        # This agent automatically handles the tool-calling loop (Model -> Tool -> Model)
        agent_executor = create_react_agent(
            model=llm,
            tools=mcp_tools,
            # Pass the loaded tools to the agent's executor
            name="MathAgentExecutor"
        )

        # 5. Invoke the agent with a task
        print("\n--- Invoking Agent ---")
        user_query = "What is the result of (30 + 15) multiplied by 2?"
        
        result = await agent_executor.ainvoke(
            {"messages": [("user", user_query)]}
        )

        print("\n--- Final Answer ---")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    # You must run the client with an asyncio event loop
    # Ensure your `math_server.py` is in the same directory or adjust the path
    asyncio.run(run_mcp_agent())