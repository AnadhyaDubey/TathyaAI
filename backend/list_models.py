import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print(f"Key loaded, length: {len(key) if key else 0}")

genai.configure(api_key=key)

for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)