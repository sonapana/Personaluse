
## Graph state  

python
from typing import List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class DQState(TypedDict, total=False):
    source_config: Dict[str, Any]
    raw_data_refs: Dict[str, Any]
    structured_sample: Any
    unstructured_sample: Any
    profiling_stats: Dict[str, Any]
    dq_rules: List[Dict[str, Any]]
    dq_issues: List[Dict[str, Any]]
    insights: Dict[str, Any]


DQState is the single source of truth that every node reads and updates, which is the recommended pattern in LangGraph. [1][3]  

***

## Agent nodes (functions)  

python
# SCOUT: connectors & discovery
def scout_agent(state: DQState) -> DQState:
    cfg = state["source_config"]
    raw_refs, structured, unstructured = discover_and_sample(cfg)  # your code
    return {
        **state,
        "raw_data_refs": raw_refs,
        "structured_sample": structured,
        "unstructured_sample": unstructured,
    }

# PROFILER: structured stats
def profiler_agent(state: DQState) -> DQState:
    df = state["structured_sample"]
    stats = run_profiling(df)          # nulls, uniques, drift, etc.
    return {**state, "profiling_stats": stats}

# VISIONARY: unstructured / multimodal
def visionary_agent(state: DQState) -> DQState:
    blobs = state.get("unstructured_sample")
    if not blobs:
        return state
    issues = analyze_unstructured_with_llm(blobs)  # returns list of issues
    merged = state.get("dq_issues", []) + issues
    return {**state, "dq_issues": merged}

# JUDGE: rule generation + validation
def judge_agent(state: DQState) -> DQState:
    stats = state["profiling_stats"]
    df = state["structured_sample"]
    rules = generate_rules_with_llm(stats)          # list of rules
    violations = apply_rules(df, rules)            # list of issues
    merged_issues = state.get("dq_issues", []) + violations
    return {**state, "dq_rules": rules, "dq_issues": merged_issues}

# STORYTELLER: persona views & reporting
def storyteller_agent(state: DQState) -> DQState:
    views = build_persona_views(
        issues=state.get("dq_issues", []),
        stats=state.get("profiling_stats", {}),
        rules=state.get("dq_rules", []),
    )  # {executive: ..., steward: ..., ds: ...}
    write_views_to_db(views)          # dashboards consume this
    return {**state, "insights": views}


Each node is a pure function on DQState, which fits LangGraph’s design for robust, inspectable workflows. [1][4]

***

## Wiring the LangGraph  

python
from langgraph.graph import StateGraph

def build_dq_graph() -> Any:
    graph = StateGraph(DQState)

    graph.add_node("scout", scout_agent)
    graph.add_node("profiler", profiler_agent)
    graph.add_node("visionary", visionary_agent)
    graph.add_node("judge", judge_agent)
    graph.add_node("storyteller", storyteller_agent)

    # Entry + flow (scout → profiler & visionary in parallel → judge → storyteller)
    graph.add_edge(START, "scout")
    graph.add_edge("scout", "profiler")
    graph.add_edge("scout", "visionary")
    graph.add_edge("profiler", "judge")
    graph.add_edge("visionary", "judge")
    graph.add_edge("judge", "storyteller")
    graph.add_edge("storyteller", END)

    return graph.compile()


This mirrors your architecture: Scout fans out to Profiler and Visionary, both feed Judge, and Storyteller is the final node for persona-based views. [5][2]

***

## Running with config and adding human-in-the-loop  

python
dq_graph = build_dq_graph()

initial_state: DQState = {
    "source_config": {
        "files": ["s3://bucket/table.csv"],
        "sql": {"dsn": "..."},
        "objects": ["s3://images/"],
    }
}

# Batch execution
final_state = dq_graph.invoke(initial_state)

# Optional: pause after judge for approval
def needs_approval(state: DQState) -> bool:
    return has_high_risk_issues(state.get("dq_issues", []))

# In LangGraph you can use conditional edges / checkpoints to route
# judge -> human_review -> storyteller when approval is required.


LangGraph supports conditional edges and loops, so you can add a human_review node between judge and storyteller that waits for steward feedback before continuing, enabling the “human-in-the-loop feedback” shown on your diagram. [6][7]

If you tell the target stack (Postgres vs Snowflake, vector DB choice, LLM provider), a next step can be fully fleshed helper implementations for discover_and_sample, run_profiling, and the LLM prompts for Judge/Storyteller.

