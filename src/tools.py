import arxiv
import os
from pypdf import PdfReader
import requests

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

def download_paper(paper_id: str, folder: str = "data"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{paper_id}.pdf")
    if not os.path.exists(path):
        response = requests.get(f"https://arxiv.org/pdf/{paper_id}", timeout=60)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
    return path

def pdf_to_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)