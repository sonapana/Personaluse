from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- 1. Output from Profiling Agent ---
class ColumnProfile(BaseModel):
    name: str
    mean: float
    stdev: float
    missing_count: int
    is_drift_detected: bool = Field(default=False)

class ProfilingReport(BaseModel):
    data_id: str
    timestamp: str
    column_profiles: List[ColumnProfile]
    anomalies_detected: int

# --- 2. Output from Rule Generation Agent ---
class ProposedRule(BaseModel):
    rule_name: str
    rule_type: str = "GreatExpectations"
    expectation_kwargs: Dict[str, Any]
    llm_justification: str

# --- 3. Output from Validation Agent ---
class ValidationSummary(BaseModel):
    total_records: int
    failed_records_count: int
    failure_log: List[Dict[str, Any]] # e.g., [{"record_id": "R004", "rule": "unique_id_check"}]
    rule_performance: Dict[str, float] # Rule name -> Pass Rate

## with mcp 

from typing import TypedDict, List, Dict, Any

# 1. Define the Protocol Schema (The MCP)
class GraphState(TypedDict):
    """
    Represents the state of the adaptive data quality pipeline. 
    This is the Model Context Protocol (MCP).
    """
    
    # CORE DATA
    data_batch: List[Dict[str, Any]]  # The current segment of data being processed (The "data")
    
    # AGENT OUTPUT DATA
    profiling_report: str             # Output from the Profiling Agent (Statistical drift/anomalies)
    validation_summary: str           # Output from the Validation Agent (Pass/Fail logs, error rates)
    
    # PROMPT MANAGEMENT
    current_rule_prompt: str          # The LLM prompt used to generate the current rule (The "prompt")
    proposed_rule: str                # The executable rule (e.g., Great Expectations code snippet)
    
    # CONTROL & ADAPTATION
    max_retries: int                  # Max cycles allowed in the Refinement Loop
    retry_count: int                  # Counter for the current refinement attempts


#-------------------- example use 
def refinement_agent(state: GraphState):
    # 1. READ Data from MCP
    summary = state['validation_summary']
    
    # 2. LLM REASONING (Critique)
    critique = f"""
    Analyze the following validation summary where the AI-generated rule failed: 
    {summary} 
    Based on the failures (e.g., too many false positives), modify the prompt 
    to make the rule more tolerant or accurate.
    """
    
    # LLM processes the critique and outputs a refined instruction/prompt
    new_instruction = llm.invoke(critique).content
    
    # 3. WRITE Prompt and Control data back to MCP
    return {
        'current_rule_prompt': new_instruction,  # <-- Stores the new, refined prompt
        'retry_count': state['retry_count'] + 1
    }
