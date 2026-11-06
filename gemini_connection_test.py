import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=15000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)

print("Checking Gemini API connection...\n")

try:
    for model in client.models.list():
        if "flash" in model.name.lower():
            print(model.name)

except Exception as error:
    print("Connection test failed:")
    print(type(error).__name__, error)

finally:
    client.close()