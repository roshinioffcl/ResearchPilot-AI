import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from your .env file.")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-embedding-2"
EMBEDDING_DIMENSION = 768
BATCH_SIZE = 16

# Free tier: 100 embedding requests per minute.
# 16 texts every ~10 seconds is about 96 per minute.
MIN_SECONDS_PER_BATCH = 10
MAX_RETRIES = 6


def _retry_delay(error, default=30):
    """Read 'Please retry in 29.3s' from the error text if present."""
    match = re.search(r"retry in ([\d.]+)s", str(error))
    return float(match.group(1)) + 2 if match else default


def _embed_batch(batch):
    contents = [
        types.Content(parts=[types.Part(text=text)])
        for text in batch
    ]

    for attempt in range(MAX_RETRIES):
        try:
            return client.models.embed_content(
                model=MODEL_NAME,
                contents=contents,
                config=types.EmbedContentConfig(
                    output_dimensionality=EMBEDDING_DIMENSION
                ),
            )
        except Exception as error:
            is_quota = "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error)

            if is_quota and attempt < MAX_RETRIES - 1:
                wait = _retry_delay(error)
                print(f"Embedding quota hit, waiting {wait:.0f}s...")
                time.sleep(wait)
                continue

            raise


def get_embeddings(texts):
    """Generate Gemini embeddings for a list of text inputs."""

    if isinstance(texts, str):
        texts = [texts]

    if not texts:
        return []

    embeddings = []
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    for number, start in enumerate(range(0, len(texts), BATCH_SIZE), start=1):
        batch = texts[start:start + BATCH_SIZE]
        began = time.time()

        response = _embed_batch(batch)

        embeddings.extend(
            embedding.values
            for embedding in response.embeddings
        )

        print(f"Embedded batch {number}/{total_batches}")

        # Pace requests so we stay under the per-minute limit
        elapsed = time.time() - began
        if number < total_batches and elapsed < MIN_SECONDS_PER_BATCH:
            time.sleep(MIN_SECONDS_PER_BATCH - elapsed)

    if len(embeddings) != len(texts):
        raise RuntimeError("Gemini returned an unexpected number of embeddings.")

    return embeddings