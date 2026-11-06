
import json
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load chunks
with open(
    "data/processed/chunks.json",
    "r",
    encoding="utf-8"
) as file:
    chunks = json.load(file)

# Load embeddings
embeddings = np.load("data/processed/chunk_embeddings.npy")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

print("ResearchPilot Book Search")
print("Type 'exit' to stop.")

while True:
    query = input("\nAsk a question: ").strip()

    if query.lower() == "exit":
        break

    if not query:
        print("Please enter a question.")
        continue

    # Convert question into an embedding
    query_embedding = model.encode(
        query,
        convert_to_numpy=True
    )

    # Compare question with all book chunks
    scores = util.cos_sim(
        query_embedding,
        embeddings
    )[0]

    # Get top 5 matching chunks
    top_results = scores.argsort(descending=True)[:5]

    print("\nMost relevant passages:\n")

    for rank, index in enumerate(top_results, start=1):
        chunk = chunks[index]

        print(f"Rank: {rank}")
        print(f"Similarity: {scores[index].item():.4f}")
        print(f"Document: {chunk['document']}")
        print(f"Page: {chunk['page']}")
        print(f"Text: {chunk['text'][:500]}")
        print("-" * 60)
