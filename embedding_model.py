
import os

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


def get_embeddings(texts):
    """Generate Gemini embeddings for a list of text inputs."""

    if isinstance(texts, str):
        texts = [texts]

    if not texts:
        return []

    embeddings = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]

        contents = [
            types.Content(
                parts=[types.Part(text=text)]
            )
            for text in batch
        ]

        response = client.models.embed_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.EmbedContentConfig(
                output_dimensionality=EMBEDDING_DIMENSION
            )
        )

        embeddings.extend(
            embedding.values
            for embedding in response.embeddings
        )

    if len(embeddings) != len(texts):
        raise RuntimeError("Gemini returned an unexpected number of embeddings.")

    return embeddings
