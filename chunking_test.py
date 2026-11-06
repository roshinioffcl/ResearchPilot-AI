
import json
from chunker import chunk_pages

with open("data/processed/extracted_pages.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

chunks = chunk_pages(pages)

print("Total PDF pages:", len(pages))
print("Total chunks:", len(chunks))

for chunk in chunks[:3]:
    print("\n-------------------------")
    print("Chunk ID:", chunk["chunk_id"])
    print("Document:", chunk["document"])
    print("Page:", chunk["page"])
    print("Text:", chunk["text"][:200])
