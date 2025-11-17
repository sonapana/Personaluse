import spacy
from spacy.tokens import DocBin
import random
import os

# 1. Define the Data
# Structure: (text, {"cats": {"LABEL_NAME": 1.0/0.0}})
TRAIN_DATA = [
    # --- CODE Examples (Label: CODE) ---
    ("How do I reverse a string in Python using slicing?", {"cats": {"CODE": 1.0, "OFF_TOPIC": 0.0}}),
    ("Explain the difference between SQL JOIN types.", {"cats": {"CODE": 1.0, "OFF_TOPIC": 0.0}}),
    ("Write a JavaScript function to validate an email format.", {"cats": {"CODE": 1.0, "OFF_TOPIC": 0.0}}),
    ("What is the Big O notation for bubble sort?", {"cats": {"CODE": 1.0, "OFF_TOPIC": 0.0}}),
    ("Troubleshoot: my docker-compose build fails with error 404.", {"cats": {"CODE": 1.0, "OFF_TOPIC": 0.0}}),
    ("What are decorators in Python and how do they work?", {"cats": {"CODE": 1.0, "OFF_TOPIC": 0.0}}),

    # --- OFF_TOPIC Examples (Label: OFF_TOPIC) ---
    ("What is the current weather forecast for London?", {"cats": {"CODE": 0.0, "OFF_TOPIC": 1.0}}),
    ("Tell me about the history of the Roman Empire.", {"cats": {"CODE": 0.0, "OFF_TOPIC": 1.0}}),
    ("What is a good recipe for apple pie?", {"cats": {"CODE": 0.0, "OFF_TOPIC": 1.0}}),
    ("Who won the last FIFA World Cup?", {"cats": {"CODE": 0.0, "OFF_TOPIC": 1.0}}),
    ("Where should I go for vacation next summer?", {"cats": {"CODE": 0.0, "OFF_TOPIC": 1.0}}),
    ("What is the capital city of Australia?", {"cats": {"CODE": 0.0, "OFF_TOPIC": 1.0}}),
]

# 2. Split Data (Training is essential for evaluation)
random.shuffle(TRAIN_DATA)
TRAIN_SPLIT = 0.8
train_set = TRAIN_DATA[:int(len(TRAIN_DATA) * TRAIN_SPLIT)]
dev_set = TRAIN_DATA[int(len(TRAIN_DATA) * TRAIN_SPLIT):]

# 3. Create DocBin Files
def create_docbin(data, file_path):
    # Load a blank English language model for tokenization
    nlp = spacy.blank("en")
    db = DocBin()
    
    for text, annotations in data:
        doc = nlp(text)
        # Apply the category labels to the Doc object
        doc.cats = annotations["cats"]
        db.add(doc)
    
    # Save the DocBin object to disk
    with open(file_path, "wb") as f:
        f.write(db.to_bytes())
    
    print(f"✅ Successfully created {file_path} with {len(data)} examples.")

# Execute the creation
create_docbin(train_set, "train.spacy")
create_docbin(dev_set, "dev.spacy")

# python -m spacy init config --lang en --pipeline textcat config_base.cfg
# python -m spacy init fill-config config_base.cfg config.cfg
# python -m spacy train config.cfg --output ./output --paths.train ./train.spacy --paths.dev ./dev.spacy

import spacy
# Import the LLM library you are using (e.g., openai, google-genai)
# import openai 

# --- STEP 1: LOAD THE SPACY INTENT MODEL ---
try:
    # Load your custom trained model from its saved path
    # Replace './output/model-best' with your actual path
    nlp_intent = spacy.load("./output_model/model-best") 
    print("✅ spaCy Intent Checker Loaded.")
except OSError:
    print("🛑 ERROR: Could not load spaCy model. Check the path and ensure training was successful.")
    # Exit or handle the error gracefully
    
# Define the confidence threshold required for a 'CODE' classification
CONFIDENCE_THRESHOLD = 0.85

def check_query_intent(query: str) -> str:
    """
    Classifies the user query using the trained spaCy TextCategorizer.
    
    Returns: 'CODE' if intent is high-confidence, otherwise 'OFF_TOPIC'.
    """
    doc = nlp_intent(query)
    
    # Get the score for the 'CODE' label
    code_score = doc.cats.get("CODE", 0.0)
    
    if code_score >= CONFIDENCE_THRESHOLD:
        return "CODE"
    else:
        return "OFF_TOPIC"