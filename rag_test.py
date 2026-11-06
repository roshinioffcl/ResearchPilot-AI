import chromadb
from sentence_transformers import SentenceTransformer
from answer_generator import generate_answer

# 1. Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Connect to ChromaDB
client = chromadb.PersistentClient(path="data/vector_db")

collection = client.get_collection(
    name="researchpilot_book"
)

# 3. Get user's question
question = input("\nAsk ResearchPilot: ").strip()

if not question:
    print("Please enter a question.")
    raise SystemExit

# 4. Convert question into embedding
query_embedding = model.encode(
    question,
    convert_to_numpy=True
)

# 5. Retrieve relevant chunks
results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=10
)

# Check retrieval relevance
best_distance = results["distances"][0][0]

RELEVANCE_THRESHOLD = 1.2

print(f"\nBest retrieval distance: {best_distance:.4f}")

if best_distance > RELEVANCE_THRESHOLD:
    print("\nResearchPilot Answer:")
    print("I couldn't find sufficiently relevant information in your documents.")
    raise SystemExit
print("\nRetrieval Results:\n")

for i in range(len(results["ids"][0])):
    metadata = results["metadatas"][0][i]

    print(f"Rank: {i + 1}")
    print(f"Distance: {results['distances'][0][i]:.4f}")
    print(f"Document: {metadata['document']}")
    print(f"Page: {metadata['page']}")
    print(f"Full Text:\n{results['documents'][0][i]}")
    print("-" * 50)

# 6. Prepare retrieved passages
retrieved_chunks = []

for i in range(len(results["ids"][0])):
    metadata = results["metadatas"][0][i]

    retrieved_chunks.append({
        "document": metadata["document"],
        "page": metadata["page"],
        "text": results["documents"][0][i]
    })

# 7. Generate answer using Gemini
print("\nResearchPilot is thinking...\n")

answer = generate_answer(
    question,
    retrieved_chunks
)

print("ResearchPilot Answer:\n")
print(answer)