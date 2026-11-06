import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)

try:
    print("Sending request to Gemini...\n")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="In one sentence, what is RAG in AI?"
    )

    print("Gemini Response:")
    print(response.text)

except Exception as error:
    print("Gemini request failed:")
    print(type(error).__name__, error)

finally:
    client.close()