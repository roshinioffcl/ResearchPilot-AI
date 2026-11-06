
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from chunker import chunk_pages

# Load extracted PDF pages
with open(
    "data/processed/extracted_pages.json",
    "r",
    encoding="utf-8"
) as file:
    pages = json.load(file)

# Divide pages into chunks
chunks = chunk_pages(pages)

if not chunks:
    raise ValueError("No chunks available for embedding.")

print("Total chunks:", len(chunks))

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Extract text from every chunk
texts = [chunk["text"] for chunk in chunks]

# Generate embeddings
embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True
)

# Create output directory
output_folder = Path("data/processed")
output_folder.mkdir(parents=True, exist_ok=True)

# Save chunk metadata and text
with open(output_folder / "chunks.json", "w", encoding="utf-8") as file:
    json.dump(chunks, file, ensure_ascii=False, indent=4)

# Save numerical embeddings
np.save(output_folder / "chunk_embeddings.npy", embeddings)

print("\nEmbedding generation completed!")
print("Total chunks:", len(chunks))
print("Embedding shape:", embeddings.shape)
print("Dimensions per chunk:", embeddings.shape[1])
