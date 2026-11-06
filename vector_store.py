
import json
import numpy as np
import chromadb

# Load chunks
with open(
    "data/processed/chunks.json",
    "r",
    encoding="utf-8"
) as file:
    chunks = json.load(file)

# Load embeddings
embeddings = np.load("data/processed/chunk_embeddings.npy")

if len(chunks) != len(embeddings):
    raise ValueError("Number of chunks and embeddings do not match.")

# Create a persistent ChromaDB database
client = chromadb.PersistentClient(
    path="data/vector_db"
)

# Recreate the test collection for a clean run
collection_name = "researchpilot_book"

try:
    client.delete_collection(collection_name)
except Exception:
    pass

collection = client.create_collection(
    name=collection_name
)

# Store chunks in batches
batch_size = 100

for start in range(0, len(chunks), batch_size):
    end = start + batch_size

    batch_chunks = chunks[start:end]
    batch_embeddings = embeddings[start:end]

    collection.add(
        ids=[chunk["chunk_id"] for chunk in batch_chunks],
        embeddings=batch_embeddings.tolist(),
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

print("Vector database created successfully!")
print("Total stored chunks:", collection.count())
