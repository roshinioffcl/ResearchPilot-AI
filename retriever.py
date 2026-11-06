
import chromadb
from embedding_model import get_embedding_model
from storage import VECTOR_DB_DIR

# Connect to the persistent vector database
client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))

collection = client.get_collection(name="researchpilot_book")


def retrieve_chunks(question, top_k=10):
    """
    Retrieve the most relevant chunks for a question.
    """
    model = get_embedding_model()
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    # Convert question into an embedding
    query_embedding = model.encode(
        question,
        convert_to_numpy=True
    )

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )

    # Format retrieved results
    retrieved_chunks = []

    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]

        retrieved_chunks.append({
            "document": metadata["document"],
            "page": metadata["page"],
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i]
        })

    return retrieved_chunks
