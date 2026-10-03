from rag import index_paper, search_chunks

print("Indexed chunks:", index_paper("2007.06081v1"))

for hit in search_chunks("How does the method handle intermittent client connectivity?"):
    print(f"[{hit['paper_id']}]", hit["text"][:300], "\n")
   