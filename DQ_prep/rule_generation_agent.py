from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Using a simplified Mock LLM for structure, replace with your actual ChatModel
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

def generate_rule_proposal(report: ProfilingReport) -> ProposedRule:
    """Uses LLM to propose a new Great Expectations rule based on profile."""
    
    # 1. Define the desired output schema for the LLM
    parser = JsonOutputParser(pydantic_object=ProposedRule)

    # 2. Craft a system prompt that gives the LLM its persona and goal
    system_prompt = (
        "You are an expert Data Quality Engineer. Analyze the Profiling Report and generate ONE new "
        "Great Expectations rule to proactively address data drift or anomalies. "
        "Your output MUST be a valid JSON object matching the ProposedRule schema."
    )

    # 3. Create the prompt with context
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", 
         f"Current Data Profile:\n{report.model_dump_json(indent=2)}\n\n"
         "The goal is to increase the integrity of the Monthly Income column. "
         "If the mean is > 7000, propose a stricter upper bound rule. "
         "Output the rule as JSON for the Validation Agent."
        )
    ])
    
    # 4. Chain the components
    chain = prompt | llm | parser
    
    # 5. Invoke the chain
    try:
        proposal_dict = chain.invoke({"report": report.model_dump_json()})
        return ProposedRule(**proposal_dict)
    except Exception as e:
        print(f"LLM Rule Generation Failed: {e}")
        # Return a fallback or a default rule
        return ProposedRule(rule_name="fallback_unique_id", rule_type="GreatExpectations", 
                            expectation_kwargs={'column': 'Customer ID', 'mostly': 0.99}, 
                            llm_justification="Fallback rule due to LLM error.")