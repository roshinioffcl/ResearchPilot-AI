
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="data/vector_db")
collection = client.get_collection(name="researchpilot_book")

question = input("Ask ResearchPilot: ").strip()

if not question:
    raise ValueError("Question cannot be empty.")

query_embedding = model.encode(question, convert_to_numpy=True)

# Retrieve 30 candidate chunks
results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=30
)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]

# Keep a maximum of 2 chunks from each page
MAX_CHUNKS_PER_PAGE = 2
TOP_K = 10

page_counts = {}
selected = []

for i in range(len(documents)):
    metadata = metadatas[i]
    page_key = (metadata["document"], metadata["page"])

    count = page_counts.get(page_key, 0)

    if count < MAX_CHUNKS_PER_PAGE:
        selected.append(i)
        page_counts[page_key] = count + 1

    if len(selected) == TOP_K:
        break

print("\n===== PAGE-AWARE RETRIEVAL =====")

for rank, index in enumerate(selected, start=1):
    metadata = metadatas[index]

    print(f"\nRank: {rank}")
    print(f"Document: {metadata['document']}")
    print(f"Page: {metadata['page']}")
    print(f"Distance: {distances[index]:.4f}")
    print(f"Text: {documents[index][:400]}")
    print("-" * 50)
