import os
from dotenv import load_dotenv
from utils import get_ai_question

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

print(f"Testing with API Key: {api_key[:5]}...")
print("Generating question...")
q = get_ai_question("Software Engineer", [], api_key, "Gemini")
print(f"Result: {q}")
