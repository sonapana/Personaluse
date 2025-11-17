PERSONA_PROMPTS = {
    "Sassy": "You are a **sassy, witty, and slightly sarcastic** assistant. Your responses must be brief, sharp, and use modern slang where appropriate. Do not apologize for your attitude.",
    "Academic": "You are a **highly knowledgeable and formal university professor**. Your responses must be structured, use sophisticated vocabulary, cite theoretical concepts, and maintain a serious, scholarly tone.",
    "Friendly": "You are an **enthusiastic and encouraging friend**. Respond with warmth, use positive language, and keep the tone light and supportive.",
    "Default": "You are a helpful and neutral AI assistant."
}

def generate_persona_response(user_query: str, selected_persona: str = "Default") -> str:
    """
    Constructs the model input using a dynamic System Prompt (Persona).
    
    Args:
        user_query: The text input from the user.
        selected_persona: The key from the PERSONA_PROMPTS dictionary.
        
    Returns:
        The generated response text from the LLM.
    """
    
    # 1. Retrieve the System Prompt based on the user's choice
    system_instruction = PERSONA_PROMPTS.get(selected_persona, PERSONA_PROMPTS["Default"])
    
    # 2. Build the messages array (Standard Chat API format)
    messages = [
        # The System message sets the role/persona for the entire conversation
        {"role": "system", "content": system_instruction},
        # The User's actual question
        {"role": "user", "content": user_query}
    ]
    
    # --- 3. Conceptual LLM API Call ---
    # NOTE: You would replace this with your actual LLM client code (e.g., OpenAI, Gemini)
    
    # Example using a mock client:
    # client = LLMClient() 
    # response = client.generate(messages=messages)
    # return response.content
    
    # Mocking the final input to show the construction:
    print(f"--- Input for '{selected_persona}' Persona ---")
    print(f"SYSTEM: {system_instruction}")
    print(f"USER: {user_query}")
    
    return f"Response generated with the '{selected_persona}' persona instruction."


# --- Example Usage ---
user_question = "Explain the concept of quantum entanglement."

# Example 1: Sassy Persona
generate_persona_response(user_question, selected_persona="Sassy")

# Example 2: Academic Persona
generate_persona_response(user_question, selected_persona="Academic")