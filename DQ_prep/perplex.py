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

Citations:
[1] Graphs - GitHub Pages https://langchain-ai.github.io/langgraph/reference/graphs/
[2] LangGraph: Multi-Agent Workflows https://blog.langchain.com/langgraph-multi-agent-workflows/
[3] LangGraph Tutorial with Practical Example https://www.gettingstarted.ai/langgraph-tutorial-with-example/
[4] How to Build Complex LLM Pipelines with LangGraph! https://aigents.co/data-science-blog/coding-tutorial/how-to-build-complex-llm-pipelines-with-langgraph
[5] Creating Multi-Agent Workflows Using LangGraph and ... https://www.linkedin.com/pulse/multiple-ai-agents-creating-multi-agent-workflows-using-kartha-23h1c
[6] How to define graph state https://langchain-ai.github.io/langgraphjs/how-tos/define-state/
[7] How to Build Ridiculously Complex LLM Pipelines with LangGraph! https://newsletter.theaiedge.io/p/how-to-build-ridiculously-complex
[8] 1000093327.jpg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/40752821/1163cb2e-c5cc-496f-b61f-a18b4ccc965a/1000093327.jpg
-------------------------------------

***

## State and SQLite setup

python
from typing import TypedDict, List, Dict, Any
import sqlite3
from datetime import datetime

class DQState(TypedDict, total=False):
    source_config: Dict[str, Any]
    raw_data_refs: Dict[str, Any]
    structured_sample: Any
    unstructured_sample: Any
    profiling_stats: Dict[str, Any]
    dq_rules: List[Dict[str, Any]]
    dq_issues: List[Dict[str, Any]]
    insights: Dict[str, Any]
    run_id: str

# --- SQLite helpers (SQLite as feedback + results DB) ---

def init_sqlite(db_path: str = "dq_results.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dq_runs (
            run_id TEXT PRIMARY KEY,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dq_rules (
            run_id TEXT,
            rule_id TEXT,
            column_name TEXT,
            expression TEXT,
            severity TEXT,
            rationale TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dq_issues (
            run_id TEXT,
            issue_id TEXT,
            rule_id TEXT,
            column_name TEXT,
            severity TEXT,
            description TEXT,
            sample_value TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dq_insights (
            run_id TEXT,
            persona TEXT,
            content TEXT
        )
    """)
    conn.commit()
    return conn

conn = init_sqlite()


You can add more tables later (feedback, lineage, etc.).

***

## LLM wrapper and prompts

python
# Simple LLM wrapper
def your_llm_call(system_prompt: str, user_prompt: str, output_json: bool = False):
    """
    Call your LLM provider here and return text or parsed JSON.
    """
    # pseudo:
    # resp = client.chat.completions.create(...)
    # txt = resp.choices[0].message.content
    # if output_json: return json.loads(txt)
    # else: return txt
    raise NotImplementedError


Judge and Storyteller agents will use structured prompts.

***

## Scout and Profiler agents (non‑LLM)

These are mostly your own data logic; here’s a stub:

python
def discover_and_sample(cfg: Dict[str, Any]):
    # TODO: implement real connectors (CSV, SQL, S3, etc.)
    # For now, assume cfg already contains a pandas DataFrame for demo.
    df = cfg["dataframe"]
    raw_refs = {"table": "in_memory_df"}
    structured = df
    unstructured = cfg.get("unstructured", [])
    return raw_refs, structured, unstructured

def run_profiling(df):
    stats = {}
    for col in df.columns:
        series = df[col]
        stats[col] = {
            "dtype": str(series.dtype),
            "non_null_pct": float(series.notnull().mean()),
            "unique_count": int(series.nunique()),
            "sample_values": [str(v) for v in series.dropna().unique()[:5]],
        }
    return stats


***

## Visionary agent prompt (unstructured quality)

python
def analyze_unstructured_with_llm(blobs: list) -> List[Dict[str, Any]]:
    system_prompt = (
        "You are a data quality specialist for unstructured content "
        "such as text snippets, documents, and logs. "
        "You detect quality problems, missing context, and policy violations."
    )
    user_prompt = f"""
    Analyze the following unstructured items for data quality issues.
    For each issue, produce JSON with:
      - issue_id
      - severity (LOW, MEDIUM, HIGH)
      - description
      - sample_value (a short excerpt or description)
    Items:
    {blobs}
    Return ONLY a JSON list.
    """
    return your_llm_call(system_prompt, user_prompt, output_json=True)
