import json, re, sys

data = json.load(open("eval_results.json", encoding="utf-8"))
r = data["results"][int(sys.argv[1]) - 1]
print("QUESTION:", r["question"], "\n")

claims = [l.strip(" *-•") for l in r.get("answer", "").splitlines()
          if re.search(r"\d{4}\.\d{4,5}v\d+", l) and not l.strip().startswith("* [")]
words = lambda s: set(re.findall(r"[a-z]{4,}", s.lower()))

for n, claim in enumerate(claims[:3], 1):
    best = max(r["passages"], key=lambda p: len(words(claim) & words(p["text"])), default=None)
    print(f"CLAIM {n}: {claim}\n")
    if best:
        print(f"BEST PASSAGE [{best['paper_id']}]: {best['text'][:500]}\n")
    else:
        print("No passages: check the abstract at arxiv.org/abs/<id>\n")
    print("-" * 60)