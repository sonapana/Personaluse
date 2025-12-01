# export LANGCHAIN_TRACING_V2="true" (This enables the V2 tracing protocol).

# export LANGCHAIN_API_KEY="your_langsmith_api_key"

# export LANGCHAIN_PROJECT="Banking_DataQuality_Hackathon" (This names your project in the LangSmith UI).

from langsmith import Client

# Initialize the client (requires LANGCHAIN_API_KEY to be set)
client = Client()

# Get the latest run ID from the LangGraph execution (requires custom integration)
# For the hackathon, you could manually log the run_id after execution.
latest_run_id = "..." 

# Get the trace details
run = client.read_run(latest_run_id)

# Iterate through the run to find the Rule Generation Agent's output (The LLM Justification)
# This will depend on the exact structure of your LangGraph nodes.
llm_output = next(
    (node.outputs['proposed_rule']['llm_justification'] 
     for node in run.child_runs if node.name == "generate_rule"), 
    "Justification not found."
)

# Send llm_output to your UI rendering system (e.g., Streamlit, Flask, or web service)