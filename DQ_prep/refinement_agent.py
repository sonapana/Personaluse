def check_for_refinement(summary: ValidationSummary) -> bool:
    """Determines if the LLM should be re-engaged for prompt refinement."""
    # Simple logic: If too many records failed the new rule, the rule might be too strict.
    if summary.failed_records_count > 1 and summary.rule_performance.get("stricter_income_bound", 1.0) < 0.9:
        print("\n[Refinement Agent] High failure rate detected. Triggering refinement...\n")
        return True
    return False

def refine_llm_prompt(summary: ValidationSummary) -> str:
    """Mocks generating a better prompt for the next iteration."""
    
    # In a real setup, this would use a separate LLM call to critique the prompt/rule.
    critique = (
        f"Validation of the last batch failed {summary.failed_records_count} times. "
        "The new rule appears to have a high false-positive rate. "
        "The next rule proposal should slightly relax the 'Monthly Income' upper bound. "
        "Ensure the new rule is more permissive."
    )
    return critique