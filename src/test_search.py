from tools import search_arxiv

papers = search_arxiv("federated learning UAV", max_results=3)
for p in papers:
    print(p["title"])
    print(p["published"], "|", p["url"])
    print(p["abstract"][:200], "...")
    print()