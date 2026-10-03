import json
import re
import time
from agent import run_agent

# Delete some questions if you want a shorter, faster run
QUESTIONS = [
    "How does vertical asynchronous federated learning handle clients that disconnect?",
    "What are the main types of federated learning?",
    "How is federated learning used in UAV or drone networks?",
    "What are common privacy attacks on federated learning?",
    "How do CNN-LSTM models detect network intrusions?",
    "What is ADMM and how is it used in distributed optimization?",
    "How can blockchain be used to coordinate UAV swarms?",
    "What are the challenges of non-IID data in federated learning?",
    "How does retrieval-augmented generation reduce hallucinations?",
    "What are the main approaches to energy-efficient UAV communication?",
]

ID_PATTERN = re.compile(r"\d{4}\.\d{4,5}v\d+")


def retrieved_ids(trace):
    """Every paper id the agent actually saw during this run."""
    ids = set()
    for step in trace:
        if step["tool"] == "index_paper":
            ids.add(step["args"].get("paper_id"))
        if isinstance(step["result"], list):
            for item in step["result"]:
                if isinstance(item, dict):
                    ids.add(item.get("id") or item.get("paper_id"))
    ids.discard(None)
    return ids


def evaluate(question):
    trace = []
    try:
        answer = run_agent(question, trace=trace)
    except Exception as e:
        return {"question": question, "error": str(e)}

    body = re.split(r"(?i)cited papers|references", answer)[0]
    bullets = [l for l in body.splitlines() if l.strip().startswith(("*", "-", "•"))]
    cited_bullets = [l for l in bullets if ID_PATTERN.search(l)]

    cited = set(ID_PATTERN.findall(answer))
    seen = retrieved_ids(trace)
    passages = [
        {"paper_id": h["paper_id"], "text": h["text"]}
        for s in trace
        if s["tool"] == "search_papers_text" and isinstance(s["result"], list)
        for h in s["result"]
    ]
    return {
        "question": question,
        "tools_used": [s["tool"] for s in trace],
        "cited_ids": sorted(cited),
        "invalid_citations": sorted(cited - seen),
        "bullets": len(bullets),
        "bullets_with_citation": len(cited_bullets),
        "answer": answer,
        "passages": passages,
    }


if __name__ == "__main__":
    results = []
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n[{i}/{len(QUESTIONS)}] {q}")
        r = evaluate(q)
        results.append(r)
        print({k: v for k, v in r.items() if k not in ("answer", "passages")})
        time.sleep(15)  # stay under free-tier rate limits

    ok = [r for r in results if "error" not in r]
    with_bullets = [r for r in ok if r["bullets"] > 0]
    summary = {
        "questions_run": len(results),
        "completed": len(ok),
        "used_full_text_retrieval": sum("search_papers_text" in r["tools_used"] for r in ok),
        "total_citations": sum(len(r["cited_ids"]) for r in ok),
        "invalid_citations": sum(len(r["invalid_citations"]) for r in ok),
        "avg_bullets_with_citation_pct": round(
            100 * sum(r["bullets_with_citation"] for r in with_bullets)
            / max(1, sum(r["bullets"] for r in with_bullets)), 1),
    }
    print("\nSUMMARY:", summary)
    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2, ensure_ascii=False)