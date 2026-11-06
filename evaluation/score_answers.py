
import json
from pathlib import Path

results_path = Path("evaluation/answer_evaluation_results.json")

with open(results_path, "r", encoding="utf-8") as file:
    results = json.load(file)

if not results:
    print("No evaluation results found.")
    exit()

criteria = [
    "Answer accuracy",
    "Faithfulness",
    "Citation accuracy",
    "Context retention",
    "Abstention"
]

scores = []

for index, result in enumerate(results, start=1):
    print(f"\n{'=' * 50}")
    print(f"Question {index}: {result['question']}")
    print(f"\nAnswer:\n{result['answer']}")

    question_scores = {}

    for criterion in criteria:
        while True:
            try:
                score = int(input(f"{criterion} (1-5): "))

                if 1 <= score <= 5:
                    question_scores[criterion] = score
                    break

                print("Enter a score between 1 and 5.")

            except ValueError:
                print("Please enter a number.")

    scores.append({
        "question": result["question"],
        "scores": question_scores,
        "average": round(sum(question_scores.values()) / len(criteria), 2)
    })

output_path = Path("evaluation/evaluation_scores.json")

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(scores, file, ensure_ascii=False, indent=4)

overall = sum(item["average"] for item in scores) / len(scores)

print(f"\nOverall average score: {overall:.2f}/5")
print(f"Scores saved to: {output_path}")
