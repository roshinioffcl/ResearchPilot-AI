
from retriever import retrieve_chunks

question = input("Ask ResearchPilot: ").strip()

chunks = retrieve_chunks(question)

print("\n===== RETRIEVED CHUNKS =====")

for rank, chunk in enumerate(chunks, start=1):
    print(f"\nRank: {rank}")
    print(f"Document: {chunk['document']}")
    print(f"Page: {chunk['page']}")
    print(f"Distance: {chunk['distance']:.4f}")
    print(f"Text: {chunk['text'][:400]}")
    print("-" * 50)
