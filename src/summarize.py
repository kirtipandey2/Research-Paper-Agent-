from google import genai
from google.genai import types
from dotenv import load_dotenv
from tools import search_arxiv

load_dotenv()
client = genai.Client()

topic = input("Research topic: ")
papers = search_arxiv(topic, max_results=5)

text = ""
for i, p in enumerate(papers, 1):
    text += f"[{i}] {p['title']} ({p['published']})\nURL: {p['url']}\nAbstract: {p['abstract']}\n\n"

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=f"Topic: {topic}\n\nPapers:\n{text}\n\nWrite a short summary of what these papers say about the topic.",
    config=types.GenerateContentConfig(
        system_instruction="You are a research assistant. Summarize papers accurately using only the provided abstracts. Cite papers by their [number].",
    ),
)
print(response.text)