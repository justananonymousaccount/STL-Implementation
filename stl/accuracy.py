import json
import argparse

def main(extracted_file, correct_answers_file):
    # Load the extracted responses and the correct answers
    with open(extracted_file, "r", encoding="utf-8") as f:
        extracted_entries = json.load(f)

    with open(correct_answers_file, "r", encoding="utf-8") as f:
        correct_answers = json.load(f)

    # Initialize counters
    total = 0
    correct = 0

    # Iterate over each extracted response
    for entry in extracted_entries:
        qid = entry["question_id"]
        generated_choice = entry["generated_choice"].strip()

        # Only consider if the question id exists in the correct answers
        if qid in correct_answers:
            total += 1
            correct_choice = correct_answers[qid].strip()
            if generated_choice == correct_choice:
                correct += 1

    # Calculate accuracy
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"Accuracy: {accuracy:.2f}% ({correct}/{total})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate accuracy from extracted responses and correct answers.")
    parser.add_argument("--extracted_file", help="Path to the extracted responses JSON file.")
    parser.add_argument("--correct_answers_file", help="Path to the correct answers JSON file.")

    args = parser.parse_args()
    main(args.extracted_file, args.correct_answers_file)

