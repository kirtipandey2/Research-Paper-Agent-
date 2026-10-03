import json, sys

data = json.load(open("eval_results.json", encoding="utf-8"))
r = data["results"][int(sys.argv[1]) - 1]

print("QUESTION:", r["question"], "\n")
print("ANSWER:\n", r.get("answer", r.get("error")), "\n")
for n, p in enumerate(r.get("passages", []), 1):
    print(f"--- passage {n} [{p['paper_id']}] ---\n{p['text']}\n")