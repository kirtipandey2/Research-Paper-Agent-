import arxiv

def search_arxiv(query: str, max_results: int = 5):
    search = arxiv.Search(
        query=query,
        max_results=int(max_results),
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers = []
    for r in arxiv.Client().results(search):
        papers.append({
            "id": r.get_short_id(),
            "title": " ".join(r.title.split()),
            "authors": [a.name for a in r.authors][:3],
            "published": str(r.published.date()),
            "abstract": " ".join(r.summary.split()),
            "url": r.entry_id,
        })
    return papers