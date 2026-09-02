import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

response = llm.invoke([HumanMessage(content="Say: TathyaAI is online.")])
print(response.content)