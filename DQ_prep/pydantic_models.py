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