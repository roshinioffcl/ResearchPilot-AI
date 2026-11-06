import chromadb
from embedding_model import get_embeddings
from chunker import chunk_pages
from storage import VECTOR_DB_DIR



# Connect to the existing persistent database
client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))

collection = client.get_or_create_collection(
    name="researchpilot_book_gemini"
)


def index_documents(pages):

    if not pages:
        raise ValueError("No pages available for indexing.")

    # Step 1: Convert pages into chunks
    chunks = chunk_pages(pages)

    if not chunks:
        raise ValueError("No text chunks found in the uploaded documents.")

    # Step 2: Generate Gemini embeddings
    texts = [chunk["text"] for chunk in chunks]
    embeddings = get_embeddings(texts)

    # Step 3: Identify the uploaded documents
    document_names = set(
        chunk["document"] for chunk in chunks
    )

    # Replace old chunks belonging to these documents only
    for document_name in document_names:
        collection.delete(
            where={"document": document_name}
        )

    # Step 4: Store the new chunks and embeddings
    batch_size = 100

    for start in range(0, len(chunks), batch_size):

        end = start + batch_size

        batch_chunks = chunks[start:end]
        batch_embeddings = embeddings[start:end]

        collection.upsert(
            ids=[chunk["chunk_id"] for chunk in batch_chunks],

            embeddings=batch_embeddings,

            documents=[chunk["text"] for chunk in batch_chunks],

            metadatas=[
                {
                    "document": chunk["document"],
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"]
                }
                for chunk in batch_chunks
            ]
        )

    return len(chunks)

def delete_document_from_index(filename):

    # Find all chunks belonging to this document
    existing = collection.get(
        where={"document": filename}
    )

    chunk_ids = existing["ids"]

    if not chunk_ids:
        return 0

    # Delete only this document's chunks
    collection.delete(
        ids=chunk_ids
    )

    return len(chunk_ids)
