
from retriever import retrieve_chunks
from answer_generator import generate_answer

question = input("\nAsk ResearchPilot: ").strip()

if not question:
    raise ValueError("Question cannot be empty.")

# Step 1: Retrieve relevant chunks
print("\nResearchPilot is searching your documents...")

retrieved_chunks = retrieve_chunks(question)

# Step 2: Check retrieval relevance
RELEVANCE_THRESHOLD = 1.2

if not retrieved_chunks or retrieved_chunks[0]["distance"] > RELEVANCE_THRESHOLD:
    print("\nResearchPilot Answer:")
    print("I couldn't find sufficiently relevant information in your documents.")
    raise SystemExit

# Step 3: Generate an answer using Gemini
print("\nResearchPilot is generating your answer...\n")

answer = generate_answer(question, retrieved_chunks)

print("===== RESEARCHPILOT ANSWER =====\n")
print(answer)
