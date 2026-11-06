
def chunk_pages(pages, chunk_size=250, overlap=40):
    chunks = []

    for page in pages:
        text = page["text"].strip()

        if not text:
            continue

        words = text.split()
        start = 0
        chunk_index = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]

            chunks.append({
                "chunk_id": f"{page['document']}_page_{page['page']}_chunk_{chunk_index}",
                "document": page["document"],
                "page": page["page"],
                "chunk_index": chunk_index,
                "text": " ".join(chunk_words)
            })

            if end >= len(words):
                break

            start = end - overlap
            chunk_index += 1

    return chunks
