import arxiv

def search_arxiv(query: str, max_results: int = 5):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers = []
    for r in arxiv.Client().results(search):
        papers.append({
            "title": r.title,
            "authors": [a.name for a in r.authors][:3],
            "published": str(r.published.date()),
            "abstract": r.summary,
            "url": r.entry_id,
        })
    return papers