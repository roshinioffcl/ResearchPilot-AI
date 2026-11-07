
import chromadb
from embedding_model import get_embeddings
from storage import VECTOR_DB_DIR

# Connect to the persistent vector database
client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))

collection = client.get_or_create_collection(
    name="researchpilot_book_gemini"
)


def retrieve_chunks(question, top_k=10):
    """
    Retrieve the most relevant chunks for a question.
    """
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    query_embedding = get_embeddings(question)[0]

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    print("CHROMA COUNT:", collection.count())
    print("CHROMA RESULTS:", results["ids"])

    print("RETRIEVAL DISTANCES:", results["distances"])

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