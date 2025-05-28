# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import json
import argparse
import re

# Prompt template matching the required format
prompt_template = (
    "<image>\nYou are an image based question-answering expert. "
    "Given an image along with a multiple choice question and an answer, your task is to explain why the answer is wrong. "
    "Your response should strictly follow the format with two specific sections: CAPTION and EXPLANATION. Response:\n"
    "###CAPTION:[Provide a detailed description of the image, particularly emphasizing the aspects related to the question.]\n\n"
    "###EXPLANATION:[Provide a detailed explanation for why the answer is wrong.]\n\n\n"
    "Question: {question_text}\n"
    "Explain why this answer is wrong: {incorrect_choice}\n"
    "Response:\n"
)

# Load questions into a dict keyed by question_id
# Assumes question text already includes the choices but may contain a prompt line to remove

def load_questions(filename):
    questions = {}
    with open(filename, 'r', encoding='utf-8') as infile:
        for line in infile:
            record = json.loads(line.strip())
            qid = record.get('question_id') or record.get('id')
            if qid is not None:
                questions[str(qid)] = record
    return questions

# Generate standardized entries with the required format
def generate_entries(extractions, questions_dict):
    entries = []
    for record in extractions:
        qid = str(record.get('question_id'))
        caption = record.get('caption', '').strip()
        explanation = record.get('explanation', '').strip()
        incorrect_choice = record.get('incorrect_choice', '').strip()

        question_record = questions_dict.get(qid)
        if not question_record or not caption or not explanation or not incorrect_choice:
            continue

        # Clean question text
        raw_text = question_record.get('text', '').strip()
        question_text = "\n".join(raw_text.splitlines()).strip()

        # Build human prompt
        human_value = prompt_template.format(
            question_text=question_text,
            incorrect_choice=incorrect_choice
        )
        # Build GPT response
        gpt_value = (
            f"CAPTION: {caption}\n\n"
            f"EXPLANATION: {explanation}"
        )

        entry = {
            "id": qid,
            "image": question_record.get('image', ''),
            "conversations": [
                {"from": "human", "value": human_value},
                {"from": "gpt",   "value": gpt_value}
            ],
            "type": "2"
        }
        entries.append(entry)
    return entries

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate standardized JSON entries using prompt template and extracted responses."
    )
    parser.add_argument('--questions_file', '-q', required=True,
                        help='Path to the questions JSONL file (with choices included in text)')
    parser.add_argument('--extractions_file', '-e', required=True,
                        help='Path to the JSON file with extracted caption, explanation, and incorrect_choice')
    parser.add_argument('--output_file', '-o', required=True,
                        help='Path for the output JSON file')
    args = parser.parse_args()

    # Load data
    questions = load_questions(args.questions_file)
    with open(args.extractions_file, 'r', encoding='utf-8') as ef:
        extractions = json.load(ef)

    # Generate entries
    entries = generate_entries(extractions, questions)

    # Write output as JSON array
    with open(args.output_file, 'w', encoding='utf-8') as outf:
        json.dump(entries, outf, indent=4)

    print(f"Total entries generated: {len(entries)}")

