from google import genai
from dotenv import load_dotenv
load_dotenv()

client = genai.Client()  # reads GEMINI_API_KEY from your .env
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Explain RAG in 3 sentences.",
)
print(response.text)