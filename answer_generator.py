import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

MODEL_NAME = "gemini-3.5-flash-lite"  # confirm in Google AI Studio
MAX_HISTORY_MESSAGES = 6
NOT_FOUND_MESSAGE = (
    "The provided documents do not contain enough information to answer this."
)

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
)


def _format_history(conversation_history):
    if not conversation_history:
        return ""
    recent = conversation_history[-MAX_HISTORY_MESSAGES:]
    return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in recent)


def generate_answer(question, retrieved_chunks, conversation_history=None):
    if not retrieved_chunks:
        return "I couldn't find relevant information in your documents."

    context = "\n".join(
        f"Source {i}\n"
        f"Document: {c.get('document', 'unknown')}\n"
        f"Page: {c.get('page', '?')}\n"
        f"Content: {c.get('text', '')}\n"
        for i, c in enumerate(retrieved_chunks, start=1)
    )

    prompt = f"""You are ResearchPilot AI, a research assistant.

Answer the question using ONLY the DOCUMENT CONTEXT below.

Rules:
1. Answer using ONLY the provided document context.
2. Give the single best, most relevant answer.
3. Keep answers concise (2–5 sentences).
4. Use simple language.
5. Include a short code example only when requested.
6. Do not include document names, page numbers, citations, or source references in the answer.
7. If the context doesn't contain the answer, say so.
8. Avoid repetition and unnecessary explanations.
9. When asked for a code example, prefer a complete,
   minimal example that demonstrates inherited behaviour.
10. Show how the subclass uses an inherited method or variable.
11. Avoid examples that only show class declarations.
12. Keep code examples minimal (ideally 2 classes).
13. Include only the code needed to demonstrate the concept.
14. Explain inherited behaviour in one short sentence.
15. Do not include a main method unless necessary.
16. Do not copy long code examples verbatim from the documents.
17. Simplify examples while preserving the concept's correctness.
18. For simple examples, use at most 2 classes and avoid
    unnecessary constructors, getters, and main methods.
19. Show only the essential code and one short explanation.
20. Start every conceptual answer with a clear,
    beginner-friendly definition. Avoid vague wording.
    Explain technical terms briefly when first used.
21. For questions about fictional characters, identify
    the character and their role in the story first.
22. For relationship questions, state the relationship
    directly before giving supporting context.
23. Combine information from multiple retrieved passages
    into one coherent answer.
24. Avoid unnecessary plot details and spoilers unless requested.
25. Adapt your answer to the subject and type of document.
26. Do not assume the document is about programming or technology.
27. For historical questions, explain relevant people, events,
    dates and historical context.
28. For scientific questions, explain concepts and evidence.
29. For fictional works, explain characters, relationships
    and story context.
30. For general knowledge questions, answer using the
    provided document evidence.
31. Always prioritize the user's actual question.
32. Never introduce information that is not supported
    by the retrieved document context.

PREVIOUS CONVERSATION (use only to understand follow-up references):
{_format_history(conversation_history)}

DOCUMENT CONTEXT:
{context}

QUESTION:
{question}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )

    return response.text or "The model returned an empty response. Please try again."


def rewrite_question(question, conversation_history=None):
    if not conversation_history:
        return question

    prompt = f"""You are a search query rewriting assistant.

Rewrite the latest question into a standalone search query for technical
documents. Use the conversation to resolve references such as "it", "that",
"the example", and "explain more".

Do not answer the question. Return only the rewritten query on one line.

CONVERSATION:
{_format_history(conversation_history)}

LATEST QUESTION:
{question}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0),
        )
        rewritten = (response.text or "").strip().strip('"')
        return rewritten or question
    except Exception:
        return question  # never let query rewriting break the app