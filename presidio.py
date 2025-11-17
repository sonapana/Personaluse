from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# 1. Initialize the engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# The text containing PII
text_to_anonymize = "My name is George Washington, and my email is g.washington@usa.gov. My phone number is 212-555-5555."

# 2. Analyze the text to find PII entities
analyzer_results = analyzer.analyze(
    text=text_to_anonymize,
    language='en'
)

# 3. Define the Anonymization Operators (how to anonymize each entity)
# Mask PHONE_NUMBER, Redact EMAIL_ADDRESS, and replace everything else (DEFAULT)
operators = {
    "PHONE_NUMBER": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 4, "from_end": True}),
    "EMAIL_ADDRESS": OperatorConfig("redact"),
    "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED_ENTITY>"})
}

# 4. Anonymize the text using the analyzer results and defined operators
anonymized_results = anonymizer.anonymize(
    text=text_to_anonymize,
    analyzer_results=analyzer_results,
    operators=operators
)

print(f"Original Text:\n{text_to_anonymize}\n")
print(f"Anonymized Text:\n{anonymized_results.text}")

# Example Output:
# Anonymized Text:
# My name is <ANONYMIZED_ENTITY>, and my email is . My phone number is ***-***-5555.