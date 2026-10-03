import unicodedata
import chromadb
from tools import download_paper, pdf_to_text

db = chromadb.PersistentClient(path="db")
collection = db.get_or_create_collection("papers")


def chunk_text(text, size=900, step=800):
    text = " ".join(unicodedata.normalize("NFKC", text).split())
    return [text[i:i + size] for i in range(0, len(text), step)]


def index_paper(paper_id):
    path = download_paper(paper_id)
    chunks = chunk_text(pdf_to_text(path))
    collection.upsert(
        documents=chunks,
        ids=[f"{paper_id}-{i}" for i in range(len(chunks))],
        metadatas=[{"paper_id": paper_id, "chunk": i} for i in range(len(chunks))],
    )
    return f"Indexed {len(chunks)} chunks from {paper_id}"


def search_chunks(question, n_results=4):
    results = collection.query(query_texts=[question], n_results=n_results)
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"paper_id": meta["paper_id"], "text": doc, "distance": round(dist, 3)})
    return hits