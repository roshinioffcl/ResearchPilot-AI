
import json
from document_ingestor import index_documents

# Load extracted PDF pages
with open(
    "data/processed/extracted_pages.json",
    "r",
    encoding="utf-8"
) as file:
    pages = json.load(file)

print("Starting document indexing...")

total_chunks = index_documents(pages)

print("\nIndexing completed!")
print("Total chunks indexed:", total_chunks)
