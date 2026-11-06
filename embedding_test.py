from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "Machine learning enables computers to learn from data.",
    "Artificial intelligence allows machines to perform intelligent tasks.",
    "I love eating pizza."
]

query = "How do computers learn?"

# Convert documents and query into embeddings
document_embeddings = model.encode(documents)
query_embedding = model.encode(query)

# Calculate similarity
scores = util.cos_sim(query_embedding, document_embeddings)[0]

# Rank results from highest similarity to lowest
ranked_results = scores.argsort(descending=True)

print("Search query:", query)
print("\nSearch results:\n")

for index in ranked_results:
    print(f"Score: {scores[index]:.4f}")
    print(f"Document: {documents[index]}")
    print()