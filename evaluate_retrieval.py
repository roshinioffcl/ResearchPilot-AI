
import json
import chromadb
from sentence_transformers import SentenceTransformer

# Load evaluation questions
with open(
    "evaluation/retrieval_questions.json",
    "r",
    encoding="utf-8"
) as file:
    questions = json.load(file)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path="data/vector_db")
collection = client.get_collection(name="researchpilot_book")

TOP_K_VALUES = [3, 5, 10]

print("\n===== RESEARCHPILOT RETRIEVAL EVALUATION =====")

for item in questions:
    question = item["question"]
    expected_pages = set(item["expected_pages"])

    # Convert question into embedding
    query_embedding = model.encode(
        question,
        convert_to_numpy=True
    )

    # Retrieve up to 10 chunks
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=10
    )

    print(f"\nQuestion: {question}")
    print(f"Expected pages: {sorted(expected_pages)}")

    print("\nTop 10 retrieved pages:")

    for rank, metadata in enumerate(results["metadatas"][0], start=1):
        print(
            f"Rank {rank}: "
            f"Page {metadata['page']}"
        )


    for k in TOP_K_VALUES:

        # Get pages from the top K retrieved chunks
        retrieved_pages = {
            metadata["page"]
            for metadata in results["metadatas"][0][:k]
            if metadata["document"] == item["document"]
        }

        # Find correctly retrieved pages
        relevant_pages = expected_pages.intersection(
            retrieved_pages
        )

        # Calculate Recall@K
        recall = len(relevant_pages) / len(expected_pages)

        print(
            f"Recall@{k}: {recall:.2f} "
            f"({len(relevant_pages)}/{len(expected_pages)})"
        )

print("\n===== EVALUATION COMPLETE =====")
