import re
import unicodedata

def normalize_and_clean_query(raw_text: str) -> str:
    """Performs common text cleaning and normalization for LLM input."""
    
    # 1. Unicode Normalization (Standardize characters)
    # NFKC is a common form for consistency
    text = unicodedata.normalize("NFKC", raw_text)
    
    # 2. Case Folding (Lowercasing)
    text = text.lower()
    
    # 3. Remove/Replace Unwanted Elements using Regex
    # Remove HTML tags (simple version)
    text = re.sub(r'<.*?>', '', text)
    
    # Remove URLs and email addresses (replace with a marker or remove)
    text = re.sub(r'http\S+|www\S+|\S+@\S+', ' ', text)
    
    # Remove excessive punctuation and special characters (keep only letters, numbers, and basic punc)
    # This step is task-dependent; be cautious about removing periods.
    text = re.sub(r'[^\w\s.?!,-]', '', text) 

    # 4. Whitespace Normalization (Replace multiple spaces with a single space)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# --- Test ---
raw_input = "YoU WOn't BelieVe this!!! WhAt's the code 4 a loop? (Visit http://www.example.com!)"
cleaned_output = normalize_and_clean_query(raw_input)

print(f"Original: {raw_input}")
print(f"Cleaned:  {cleaned_output}")