
import json
import chromadb
from sentence_transformers import SentenceTransformer

with open("evaluation/retrieval_questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="data/vector_db")
collection = client.get_collection(name="researchpilot_book")

TOP_K_VALUES = [3, 5, 10]
MAX_CHUNKS_PER_PAGE = 2


def calculate_recall(metadata, expected_pages, document):
    retrieved_pages = {
        item["page"]
        for item in metadata
        if item["document"] == document
    }

    return len(retrieved_pages.intersection(expected_pages)) / len(expected_pages)


print("\n===== NORMAL VS PAGE-AWARE EVALUATION =====")

for item in questions:
    question = item["question"]
    document = item["document"]
    expected_pages = set(item["expected_pages"])

    query_embedding = model.encode(question, convert_to_numpy=True)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=30
    )

    metadata = results["metadatas"][0]

    # Normal retrieval
    normal_results = metadata[:10]

    # Page-aware retrieval
    page_counts = {}
    page_aware_results = []

    for result in metadata:
        page_key = (result["document"], result["page"])

        count = page_counts.get(page_key, 0)

        if count < MAX_CHUNKS_PER_PAGE:
            page_aware_results.append(result)
            page_counts[page_key] = count + 1

        if len(page_aware_results) == 10:
            break

    print(f"\nQuestion: {question}")

    for k in TOP_K_VALUES:
        normal_recall = calculate_recall(
            normal_results[:k], expected_pages, document
        )

        page_recall = calculate_recall(
            page_aware_results[:k], expected_pages, document
        )

        print(
            f"Recall@{k} | "
            f"Normal: {normal_recall:.2f} | "
            f"Page-aware: {page_recall:.2f}"
        )
