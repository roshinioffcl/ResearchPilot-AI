
import json
import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

# Load evaluation questions
with open("evaluation/retrieval_questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

# Load embedding model and ChromaDB
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="data/vector_db")
collection = client.get_collection(name="researchpilot_book")

TOP_K_VALUES = [3, 5, 10]
LAMBDA_VALUES = [0.5, 0.7, 0.9]
CANDIDATE_COUNT = 30


def normalize(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.maximum(norms, 1e-12)


def retrieve_mmr(question, top_k, lambda_value):
    query_embedding = model.encode(question, convert_to_numpy=True)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=CANDIDATE_COUNT,
        include=["documents", "metadatas", "embeddings"]
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    embeddings = np.asarray(results["embeddings"][0])

    query_vector = normalize(query_embedding.reshape(1, -1))[0]
    candidate_vectors = normalize(embeddings)

    relevance = candidate_vectors @ query_vector

    selected = []
    remaining = list(range(len(documents)))

    while len(selected) < top_k and remaining:
        best_score = float("-inf")
        best_index = None

        for index in remaining:
            if selected:
                similarities = candidate_vectors[selected] @ candidate_vectors[index]
                diversity_penalty = np.max(similarities)
            else:
                diversity_penalty = 0

            score = (
                lambda_value * relevance[index]
                - (1 - lambda_value) * diversity_penalty
            )

            if score > best_score:
                best_score = score
                best_index = index

        selected.append(best_index)
        remaining.remove(best_index)

    return [metadatas[index] for index in selected]


def calculate_recall(retrieved, expected_pages, document):
    retrieved_pages = {
        item["page"]
        for item in retrieved
        if item["document"] == document
    }

    found = retrieved_pages.intersection(expected_pages)

    return len(found) / len(expected_pages)


print("\n===== RETRIEVAL EVALUATION =====")

for item in questions:
    question = item["question"]
    document = item["document"]
    expected_pages = set(item["expected_pages"])

    print(f"\nQuestion: {question}")
    print(f"Expected pages: {sorted(expected_pages)}")

    query_embedding = model.encode(question, convert_to_numpy=True)

    baseline_results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=max(TOP_K_VALUES)
    )

    baseline_metadata = baseline_results["metadatas"][0]

    for k in TOP_K_VALUES:
        baseline_recall = calculate_recall(
            baseline_metadata[:k], expected_pages, document
        )

        print(f"Normal Top-{k}: {baseline_recall:.2f}")

    for lambda_value in LAMBDA_VALUES:
        print(f"\nMMR (lambda={lambda_value}):")

        mmr_results = retrieve_mmr(
            question,
            max(TOP_K_VALUES),
            lambda_value
        )

        for k in TOP_K_VALUES:
            recall = calculate_recall(
                mmr_results[:k], expected_pages, document
            )

            print(f"  Recall@{k}: {recall:.2f}")
