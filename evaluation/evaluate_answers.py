
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
from retriever import retrieve_chunks
from answer_generator import generate_answer, rewrite_question

RELEVANCE_THRESHOLD = 1.2

history = []
results = []

print("ResearchPilot AI - Answer Evaluation")
print("Type 'exit' to finish.\n")

while True:
    question = input("Your question: ").strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    try:
        search_query = rewrite_question(question, history)
        chunks = retrieve_chunks(search_query)

        if not chunks or chunks[0]["distance"] > RELEVANCE_THRESHOLD:
            answer = "Insufficient information in indexed documents."
        else:
            answer = generate_answer(
                search_query,
                chunks,
                history
            )

        print("\nResearchPilot:", answer, "\n")

        results.append({
            "question": question,
            "search_query": search_query,
            "answer": answer,
            "sources": [
                {
                    "document": chunk["document"],
                    "page": chunk["page"],
                    "distance": chunk["distance"],
                    "retrieved_text": chunk["text"]
                }
                for chunk in chunks
            ]
        })

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

    except Exception as error:
        print("Error:", error)

output_path = Path("evaluation/answer_evaluation_results.json")

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=4)

print(f"\nEvaluation results saved to: {output_path}")
