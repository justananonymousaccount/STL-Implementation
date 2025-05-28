# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import json
import re
import argparse

# Updated prompt template
prompt_template = (
    "You are an image based question-answering expert. "
    "Given an image along with a multiple choice question and an answer, your task is to explain why the answer is wrong. "
    "Your response should strictly follow the format with two specific sections: CAPTION and EXPLANATION. Response:\n"
    "###CAPTION:[Provide a detailed description of the image, particularly emphasizing the aspects related to the question.]\n\n"
    "###EXPLANATION:[Provide a detailed explanation for why the answer is wrong.]\n\n\n"
    "Question: {question}\n"
    "The correct choice is {correct_choice}.\n"
    "Explain why this answer is wrong: {incorrect_choice}\n"
    "Response:\n"
)

# Regex pattern to extract choices: lines like "(a) text"
choice_pattern = re.compile(r"^\(([a-z])\)\s*(.+)$")

def generate_prompts(correct_extractions_file, questions_file, output_file):
    # Load correct extractions into a dict keyed by question_id
    with open(correct_extractions_file, 'r', encoding='utf-8') as f:
        correct_extractions = json.load(f)
    correct_dict = {entry['question_id']: entry for entry in correct_extractions}

    # Load all questions into a dict keyed by question_id
    questions_dict = {}
    with open(questions_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            try:
                qdata = json.loads(line)
                qid = qdata.get('question_id')
                if qid:
                    questions_dict[qid] = qdata
            except json.JSONDecodeError:
                continue

    final_prompts = []

    # Iterate over each correctly extracted entry
    for qid, extraction in correct_dict.items():
        question_record = questions_dict.get(qid)
        if not question_record:
            continue  # skip if question not found

        question_text = question_record.get('text', '')

        # Extract correct choice
        correct_choice = extraction.get('generated_choice')
        if not correct_choice:
            continue  # skip incomplete extractions

        # Extract choices from question_text
        choices = {}
        for line in question_text.splitlines():
            m = choice_pattern.match(line.strip())
            if m:
                letter = f"({m.group(1)})"
                choices[letter] = m.group(2).strip()

        # Generate prompt for each incorrect option
        for letter in choices:
            if letter == correct_choice:
                continue

            prompt_text = prompt_template.format(
                question=question_text,
                correct_choice=correct_choice,
                incorrect_choice=letter
            )

            output_record = {
                'question_id': qid,
                'image': question_record.get('image'),
                'text': prompt_text,
                'category': question_record.get('category')
            }
            final_prompts.append(output_record)

    # Write out final prompts
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for rec in final_prompts:
            outfile.write(json.dumps(rec, ensure_ascii=False) + '\n')

    print(f"Total prompts generated: {len(final_prompts)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate negative explanation prompts from correct extractions and questions."
    )
    parser.add_argument(
        '--extractions_file', '-c',
        required=True,
        help='Path to the JSON file containing correct extractions.'
    )
    parser.add_argument(
        '--questions_file', '-q',
        required=True,
        help='Path to the JSONL file containing questions.'
    )
    parser.add_argument(
        '--output_file', '-o',
        required=True,
        help='Path to the output JSONL file for generated prompts.'
    )
    args = parser.parse_args()
    generate_prompts(
        args.extractions_file,
        args.questions_file,
        args.output_file
    )

