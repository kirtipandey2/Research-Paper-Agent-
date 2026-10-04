import json, re, sys

ID = re.compile(r"\d{4}\.\d{4,5}v\d+")
path = sys.argv[1] if len(sys.argv) > 1 else "eval_results.json"
data = json.load(open(path, encoding="utf-8"))


def body(answer):
    kept = []
    for line in answer.splitlines():
        if re.match(r"\s*(\*{3}|-{3}|#+\s*cited|\**\s*cited|\**\s*references)", line, re.I):
            break
        kept.append(line)
    return " ".join(kept)


sent_total = sent_cited = ids_total = ids_grounded = 0
for r in data["results"]:
    text = re.sub(r"[*#]", "", body(r["answer"]))
    sentences = [s for s in re.split(r"(?<=[.!?\]])\s+", text) if len(s.split()) >= 8]
    sent_total += len(sentences)
    sent_cited += sum(bool(ID.search(s)) for s in sentences)
    passage_ids = {p["paper_id"] for p in r.get("passages", [])}
    ids_total += len(r["cited_ids"])
    ids_grounded += len(set(r["cited_ids"]) & passage_ids)

print(f"Sentences with a citation: {sent_cited}/{sent_total} ({100 * sent_cited / max(1, sent_total):.0f}%)")
print(f"Cited papers with full-text passages: {ids_grounded}/{ids_total} ({100 * ids_grounded / max(1, ids_total):.0f}%)")