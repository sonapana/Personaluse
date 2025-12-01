from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

# 1. Define the State (the data that flows between nodes)
class DataQualityState(TypedDict):
    df: pd.DataFrame # The input data
    profiling_report: ProfilingReport
    proposed_rule: ProposedRule
    validation_summary: ValidationSummary
    refinement_critique: str

# 2. Define the graph nodes (which execute the agent functions)
def node_profile(state: DataQualityState) -> DataQualityState:
    report = profile_data(state['df'])
    return {"profiling_report": report}

def node_generate_rule(state: DataQualityState) -> DataQualityState:
    rule = generate_rule_proposal(state['profiling_report'])
    return {"proposed_rule": rule}

def node_validate(state: DataQualityState) -> DataQualityState:
    summary = run_validation(state['df'], state['proposed_rule'])
    return {"validation_summary": summary}

def node_refine(state: DataQualityState) -> DataQualityState:
    critique = refine_llm_prompt(state['validation_summary'])
    return {"refinement_critique": critique}

def should_refine(state: DataQualityState) -> str:
    """Conditional Edge: Decides whether to loop back to generation."""
    if check_for_refinement(state['validation_summary']):
        return "refine"
    return "end"


# 3. Build the graph
workflow = StateGraph(DataQualityState)

# Add Nodes
workflow.add_node("profile", node_profile)
workflow.add_node("generate_rule", node_generate_rule)
workflow.add_node("validate", node_validate)
workflow.add_node("refine", node_refine)

# Set Edges (Sequential Flow)
workflow.set_entry_point("profile")
workflow.add_edge("profile", "generate_rule")
workflow.add_edge("generate_rule", "validate")

# Conditional Edge (The Adaptive Loop)
workflow.add_conditional_edges(
    "validate", # Source node
    should_refine, # Condition function
    {
        "refine": "refine", # If True, go to 'refine' node
        "end": END         # If False, end the graph
    }
)

# Refinement loop back to rule generation
workflow.add_edge("refine", "generate_rule")

# Compile the graph
app = workflow.compile()

# --- 4. Execution ---
if __name__ == "__main__":
    # Simulate the input data (as a streaming batch)
    data = {
        'Customer ID': ['CUST7890', 'CUST7891', 'CUST7892', 'CUST7890', 'CUST7894', 'CUST7895', 'CUST7896'],
        'Monthly Income': [6500.0, 4800.0, 7200.0, 9100.0, 5500.0, 12000.0, 999999.0], # R007 is the outlier
        'Country Code': ['US', 'US', 'MX', 'US', 'US', 'IR', 'CN']
    }
    input_df = pd.DataFrame(data)

    print("--- Starting AI Data Quality Pipeline ---")
    
    # Run the compiled graph
    final_state = app.invoke({"df": input_df})
    
    print("\n--- Pipeline Execution Complete ---")
    print(f"Final Validation Status: {'Refinement Loop was NOT triggered.' if not final_state.get('refinement_critique') else 'Refinement Loop was triggered.'}")
    print("\n[Profiling Report]")
    print(final_state['profiling_report'].model_dump_json(indent=2))
    print("\n[Proposed Rule]")
    print(final_state['proposed_rule'].model_dump_json(indent=2))
    print("\n[Validation Summary]")
    print(final_state['validation_summary'].model_dump_json(indent=2))
    if 'refinement_critique' in final_state:
        print("\n[Refinement Critique]")
        print(final_state['refinement_critique'])