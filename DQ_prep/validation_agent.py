# Great Expectations setup is complex, so we mock the validation outcome
def run_validation(df: pd.DataFrame, rule: ProposedRule) -> ValidationSummary:
    """Mocks running Great Expectations on data using the proposed rule."""
    
    # Mocking failure based on the synthetic data
    failures = []
    
    # R004: Duplicate ID failure
    failures.append({"record_id": "R004", "rule": "hardcoded_unique_check"})
    
    # R007: Outlier/Anomaly failure (if the rule proposal caught it)
    if rule.rule_name == "stricter_income_bound":
         failures.append({"record_id": "R007", "rule": rule.rule_name})
    
    return ValidationSummary(
        total_records=len(df),
        failed_records_count=len(failures),
        failure_log=failures,
        rule_performance={rule.rule_name: (len(df) - len(failures)) / len(df)}
    )