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

    prompt = f"""You are ResearchPilot AI, an intelligent and thorough research assistant.

Your goal is to help users deeply understand information in their uploaded documents.

ANSWERING RULES:

1. Answer using ONLY the provided document context.
2. Start with a clear, direct answer to the user's question.
3. Provide detailed explanations instead of unnecessarily short summaries.
4. Explain the underlying concept, reasoning, and relevant details.
5. Break complex explanations into logical paragraphs.
6. Use headings and bullet points when they improve readability.
7. Explain technical terms in beginner-friendly language.
8. Include relevant examples or analogies when they help understanding.
9. When explaining a process, describe its steps in order.
10. When comparing concepts, explain their similarities and differences.
11. Combine information from multiple retrieved passages into one coherent explanation.
12. Adapt the depth and style to the question and document subject.
13. For simple factual questions, answer directly without unnecessary expansion.
14. For conceptual questions, explain what, how, and why.
15. For complex questions, provide enough detail for a beginner to understand.
16. Never add filler, repetitive statements, or irrelevant information.
17. Never invent facts or introduce unsupported information.
18. If the documents do not contain enough information, clearly say so.
19. Do not include document names, page numbers, citations, or source references in the answer.
20. Only provide source references if the user explicitly requests them.
21. Include code examples only when requested.
22. When providing code, use minimal, correct examples and explain the important parts.
23. For fictional works, identify characters and relationships before explaining their context.
24. Avoid unnecessary plot details and spoilers unless requested.
25. For historical and scientific questions, include relevant context and evidence available in the documents.
26. Always prioritize the user's actual question.

RESPONSE STYLE:
- Be informative, clear, and natural.
- Prefer complete explanations over arbitrary sentence limits.
- Use paragraphs for explanations and bullet points for lists.
- Do not force every answer into the same format.

ANSWER LENGTH AND DEPTH:
- Even simple questions must receive informative answers of at least 3–5 sentences.
- For "Who is..." questions, explain identity, background, and significance.
- For "What happened..." questions, explain the events in chronological order.
- For "Why..." questions, explain the causes and reasoning.
- For "Explain..." questions, provide a thorough beginner-friendly explanation.
- Avoid one-line answers unless the user explicitly asks for a short answer.
- Use only information supported by the provided document context.

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