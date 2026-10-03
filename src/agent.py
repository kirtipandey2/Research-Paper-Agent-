from google import genai
from google.genai import types
from dotenv import load_dotenv
from tools import search_arxiv
from rag import index_paper, search_chunks

load_dotenv()
client = genai.Client()
MODEL = "gemini-3.5-flash-lite"

# ---------- Tool descriptions (what the model sees) ----------
search_declaration = {
    "name": "search_arxiv",
    "description": "Searches arXiv for research papers on a topic. Returns id, title, authors, date, abstract and URL.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search keywords, e.g. 'federated learning UAV'",
            },
            "max_results": {
                "type": "integer",
                "description": "How many papers to return (1 to 10)",
            },
        },
        "required": ["query"],
    },
}

index_declaration = {
    "name": "index_paper",
    "description": "Downloads the full text of an arXiv paper and stores it so it can be searched. Use the paper id returned by search_arxiv, e.g. '2007.06081v1'.",
    "parameters": {
        "type": "object",
        "properties": {
            "paper_id": {"type": "string", "description": "The arXiv id of the paper"},
        },
        "required": ["paper_id"],
    },
}

passages_declaration = {
    "name": "search_papers_text",
    "description": "Searches the full text of all indexed papers and returns the most relevant passages with their paper id and a distance score (smaller means a closer match).",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "What to look for in the papers"},
        },
        "required": ["question"],
    },
}

# ---------- Model configuration ----------
config = types.GenerateContentConfig(
    system_instruction=(
        "You are a research assistant. Follow this workflow: "
        "(1) use search_arxiv to find relevant papers; "
        "(2) use index_paper on the 2 or 3 most relevant ones; "
        "(3) use search_papers_text to retrieve passages from their full text; "
        "(4) answer using only what the retrieved passages and abstracts say. "
        "Every factual claim must end with a citation in square brackets using the "
        "paper's arXiv id, like [2007.06081v1]. Never put paper text inside a citation. "
        "Do not add background from your own knowledge. If the passages do not "
        "answer something, write 'Not covered in the retrieved papers.' "
        "End with a list of cited ids with their titles and URLs."
    ),
    tools=[
        types.Tool(
            function_declarations=[
                search_declaration,
                index_declaration,
                passages_declaration,
            ]
        )
    ],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

# ---------- Map tool names to your real Python functions ----------
TOOL_FUNCTIONS = {
    "search_arxiv": search_arxiv,
    "index_paper": index_paper,
    "search_papers_text": search_chunks,
}


# ---------- The agent loop ----------
def run_agent(question, max_steps=12, trace=None):
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]

    for step in range(max_steps):  # safety limit on steps
        response = client.models.generate_content(
            model=MODEL, contents=contents, config=config
        )
        model_content = response.candidates[0].content
        parts = model_content.parts or []
        function_calls = [p.function_call for p in parts if p.function_call]

        # No tool requested -> the model is giving its final answer
        if not function_calls:
            return response.text

        # Keep the model's full reply in the history, unchanged
        contents.append(model_content)

        # Run each requested tool and send the results back
        response_parts = []
        for call in function_calls:
            args = dict(call.args or {})
            print(f"[step {step + 1}] model called {call.name} with {args}")
            try:
                result = TOOL_FUNCTIONS[call.name](**args)
                if trace is not None:
                    trace.append({"tool": call.name, "args": args, "result": result})
            except Exception as e:
                result = {"error": str(e)}
            response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=call.name,
                        response={"result": result},
                        id=call.id,
                    )
                )
            )
        contents.append(types.Content(role="user", parts=response_parts))

    return "Stopped: too many steps."


if __name__ == "__main__":
    question = input("Ask a research question: ")
    print("\n" + run_agent(question))