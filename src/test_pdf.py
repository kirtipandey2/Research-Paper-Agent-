from tools import download_paper, pdf_to_text

path = download_paper("2007.06081v1")
text = pdf_to_text(path)
print(len(text), "characters")
print(text[:500])