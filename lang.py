from langdetect import detect
from langdetect import detect_langs # For probabilities

def check_language(text: str):
    try:
        # Detect the single most probable language
        detected_code = detect(text)
        print(f"Detected Language Code: {detected_code}") 
        
        # Detect all probable languages with their confidence scores
        probable_langs = detect_langs(text)
        print(f"Probabilities: {probable_langs}")

    except Exception as e:
        # This handles errors, typically raised if the text is too short or empty
        print(f"Error: Could not detect language. Reason: {e}")
        detected_code = 'unknown'
        
    return detected_code

# --- Test Cases ---
english_text = "Language detection is a very useful preprocessing step for LLM applications."
german_text = "Ein, zwei, drei, vier. Die Katze schläft."
short_text = "XYZ"

print("--- English Test ---")
check_language(english_text)

print("\n--- German Test ---")
check_language(german_text)

print("\n--- Short Text Test ---")
check_language(short_text)

##########################################

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

TARGET_LANGUAGE = 'en'
FALLBACK_RESPONSE = "I am a specialized assistant trained only to process questions in English. Please translate your query and try again."

def process_query_safely(cleaned_query: str):
    try:
        # 1. Check Language
        detected_lang = detect(cleaned_query)
        
        if detected_lang != TARGET_LANGUAGE:
            print(f"🛑 Query blocked. Detected language: {detected_lang}")
            return FALLBACK_RESPONSE
        
        # 2. Proceed with English Query (Your main logic)
        return call_main_llm(cleaned_query) # Call your main LLM or spaCy Intent Checker
        
    except LangDetectException:
        # Handle inputs too short or ambiguous (e.g., "???", "hello")
        print("⚠️ Query blocked. Language detection failed (too short/ambiguous).")
        return FALLBACK_RESPONSE

# (Assuming call_main_llm is defined elsewhere)