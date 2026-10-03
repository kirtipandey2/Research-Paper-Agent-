from google import genai
from google.genai import types
from dotenv import load_dotenv
from tools import search_arxiv

load_dotenv()
client = genai.Client()
MODEL = "gemini-3.5-flash-lite"

# 1. Describe the tool to the model
search_declaration = {
    "name": "search_arxiv",
    "description": "Searches arXiv for research papers on a topic. Returns titles, authors, dates, abstracts and URLs.",
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

config = types.GenerateContentConfig(
    system_instruction=(
        "You are a research assistant. Use the search_arxiv tool when you need papers. "
        "Every factual claim must end with a citation in square brackets using the "
        "paper's arXiv id, like [2007.06081v1]. Only make claims that the paper's "
        "abstract directly states. Never put abstract text inside a citation. "
        "Do not add examples, definitions or background from your own knowledge; "
        "if the abstracts don't cover something, write 'Not covered in the retrieved papers.' "
        "At the end, list each cited id with its title and URL."
    ),
    tools=[types.Tool(function_declarations=[search_declaration])],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

# 2. Map tool names to your real Python functions
TOOL_FUNCTIONS = {"search_arxiv": search_arxiv}


def run_agent(question, max_steps=8):
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
            print(f"[step {step + 1}] model called {call.name} with {dict(call.args)}")
            try:
                result = TOOL_FUNCTIONS[call.name](**call.args)
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