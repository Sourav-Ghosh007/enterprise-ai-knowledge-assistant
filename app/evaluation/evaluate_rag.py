import json
from pathlib import Path

from app.search.rag_service import ask_question


# Evaluation dataset
DATASET = Path("data/evaluation/questions.jsonl")


def normalize(text):
    """Convert text to lowercase and remove extra spaces."""
    return " ".join(text.lower().strip().split())


def evaluate():

    total = 0
    answer_matches = 0
    source_matches = 0

    with open(DATASET, "r", encoding="utf-8") as file:

        for line in file:

            item = json.loads(line)

            question = item["question"]
            expected_answer = item["answer"]
            expected_source = item["source"]

            print("\n" + "=" * 70)
            print("Question:", question)

            # Run our RAG system
            actual_answer, actual_sources = ask_question(question)

            print("Expected answer:", expected_answer)
            print("Actual answer:", actual_answer)

            print("Expected source:", expected_source)
            print("Actual sources:", actual_sources)

            # Answer evaluation
            if normalize(expected_answer) in normalize(actual_answer):
                answer_matches += 1

            # Source evaluation
            if expected_source in actual_sources:
                source_matches += 1

            total += 1

    print("\n" + "=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)

    answer_accuracy = (answer_matches / total) * 100
    source_accuracy = (source_matches / total) * 100

    print(f"Total questions: {total}")
    print(f"Answer accuracy: {answer_accuracy:.2f}%")
    print(f"Source accuracy: {source_accuracy:.2f}%")


if __name__ == "__main__":
    evaluate()