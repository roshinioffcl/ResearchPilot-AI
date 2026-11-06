
import chromadb

client = chromadb.PersistentClient(path="data/vector_db")

collection = client.get_collection(
    name="researchpilot_book"
)

pages_to_inspect = [237, 239]

for page_number in pages_to_inspect:

    results = collection.get(
        where={"page": page_number},
        include=["documents", "metadatas"]
    )

    print(f"\n{'=' * 60}")
    print(f"PAGE {page_number}")
    print(f"{'=' * 60}")

    for i, text in enumerate(results["documents"], start=1):
        print(f"\nChunk {i}:")
        print(text)
        print("-" * 40)
