
import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path="data/vector_db")
collection = client.get_collection(name="researchpilot_book")

question = input("Ask ResearchPilot: ").strip()

if not question:
    raise ValueError("Question cannot be empty.")

# Generate query embedding
query_embedding = model.encode(
    question,
    convert_to_numpy=True
)

# Retrieve 30 candidate chunks
results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=30,
    include=["documents", "metadatas", "embeddings"]
)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
embeddings = np.asarray(results["embeddings"][0])

# Normalize vectors for cosine similarity
def normalize(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.maximum(norms, 1e-12)

query_vector = normalize(query_embedding.reshape(1, -1))[0]
candidate_vectors = normalize(embeddings)

# Calculate relevance to the question
relevance = candidate_vectors @ query_vector

# MMR selection
lambda_value = 0.9
top_k = 10

selected = []
remaining = list(range(len(documents)))

while len(selected) < top_k and remaining:

    mmr_scores = []

    for index in remaining:

        if not selected:
            diversity_penalty = 0
        else:
            similarities = candidate_vectors[selected] @ candidate_vectors[index]
            diversity_penalty = np.max(similarities)

        score = (
            lambda_value * relevance[index]
            - (1 - lambda_value) * diversity_penalty
        )

        mmr_scores.append((score, index))

    best_score, best_index = max(mmr_scores)

    selected.append(best_index)
    remaining.remove(best_index)

# Display MMR results
print("\n===== MMR RETRIEVAL RESULTS =====")

for rank, index in enumerate(selected, start=1):

    metadata = metadatas[index]

    print(f"\nRank: {rank}")
    print(f"Document: {metadata['document']}")
    print(f"Page: {metadata['page']}")
    print(f"Relevance: {relevance[index]:.4f}")
    print(f"Text: {documents[index][:400]}")
    print("-" * 50)
