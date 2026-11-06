
import chromadb
from sentence_transformers import SentenceTransformer

# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to our existing database
client = chromadb.PersistentClient(
    path="data/vector_db"
)

# Access the existing collection
collection = client.get_collection(
    name="researchpilot_book"
)

print("ResearchPilot - ChromaDB Search")
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

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=5
    )

    print("\nMost relevant passages:\n")

    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        document = results["documents"][0][i]
        distance = results["distances"][0][i]

        print(f"Rank: {i + 1}")
        print(f"Document: {metadata['document']}")
        print(f"Page: {metadata['page']}")
        print(f"Distance: {distance:.4f}")
        print(f"Text: {document[:500]}")
        print("-" * 60)
