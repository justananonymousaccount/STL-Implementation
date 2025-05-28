# -*- coding: utf-8 -*-
import json
import argparse

def main(args):
    # Load extracted responses
    with open(args.extracted_file, "r", encoding="utf-8") as f:
        extracted_data = json.load(f)

    # Load correct answers
    with open(args.correct_answers_file, "r", encoding="utf-8") as f:
        correct_answers = json.load(f)

    correct_extractions = []
    incorrect_extractions = []

    # Compare each extracted response with the correct answer
    for entry in extracted_data:
        # Ensure the question id is a string so it matches the keys in correct_answers
        qid = str(entry.get("question_id"))
        generated_choice = entry.get("generated_choice")
        correct_choice = correct_answers.get(qid)

        if correct_choice and generated_choice == correct_choice:
            correct_extractions.append(entry)
        else:
            incorrect_extractions.append(entry)

    # Write correct extractions to a JSON file
    with open(args.correct_output_file, "w", encoding="utf-8") as f:
        json.dump(correct_extractions, f, indent=4)

    # Write incorrect extractions to a JSON file
    with open(args.incorrect_output_file, "w", encoding="utf-8") as f:
        json.dump(incorrect_extractions, f, indent=4)

    # Print counts for correct and incorrect answers
    print(f"Correct extractions count: {len(correct_extractions)}")
    print(f"Incorrect extractions count: {len(incorrect_extractions)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare extracted responses with correct answers and split into correct and incorrect extractions."
    )

    parser.add_argument(
        "--extracted_file",
        type=str,
        required=True,
        help="Path to the JSON file with extracted responses"
    )
    parser.add_argument(
        "--correct_answers_file",
        type=str,
        required=True,
        help="Path to the JSON file with correct answers"
    )
    parser.add_argument(
        "--correct_output_file",
        type=str,
        required=True,
        help="Path to the JSON file to write the correct extractions"
    )
    parser.add_argument(
        "--incorrect_output_file",
        type=str,
        required=True,
        help="Path to the JSON file to write the incorrect extractions"
    )
    args = parser.parse_args()
    main(args)


