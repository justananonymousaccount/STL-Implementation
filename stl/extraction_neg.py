import json
import re
import argparse

# Updated regex patterns
caption_pattern = r"CAPTION:\s*(.*?)\s*(?:EXPLANATION:|$)"
explanation_pattern = r"EXPLANATION:\s*(.*)"
# Pattern to find choices in question block
choice_line_pattern = r"\(([a-z])\)\s*(.+)"
# Pattern to find 'Explain why...' incorrect choice
incorrect_choice_pattern = r"Explain why this answer is wrong:\s*(\([a-z]\))"

# Threshold for excessive zeros in explanation
ZERO_THRESHOLD = 50

def process_files(input_file, extracted_output_file, skipped_output_file=None):
    extracted = []
    skipped = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            qid = data.get('question_id')
            prompt_text = data.get('prompt', '')  # <-- FIXED: now correctly using 'prompt'
            resp = data.get('text', '')  # the model's response output

            # Extract CAPTION and EXPLANATION
            cap_m = re.search(caption_pattern, resp, re.DOTALL | re.IGNORECASE)
            expl_m = re.search(explanation_pattern, resp, re.DOTALL | re.IGNORECASE)

            caption = cap_m.group(1).strip() if cap_m else None
            explanation = expl_m.group(1).strip() if expl_m else None

            # Extract generated_choice (correct choice) from "The correct choice is ..."
            correct_choice = None
            if "The correct choice is" in prompt_text:
                lines = prompt_text.splitlines()
                for line in lines:
                    if line.startswith("The correct choice is"):
                        match = re.search(r"\(([a-z])\)", line)
                        if match:
                            correct_choice = f"({match.group(1)})"
                            break

            # Extract incorrect_choice from "Explain why this answer is wrong: (X)"
            incorrect_choice = None
            m = re.search(incorrect_choice_pattern, prompt_text, re.IGNORECASE)
            if m:
                incorrect_choice = m.group(1)

            # Skip if any important fields missing
            if not (caption and explanation and correct_choice and incorrect_choice):
                skipped.append(data)
                continue
            if explanation.count('0') > ZERO_THRESHOLD:
                skipped.append(data)
                continue

            extracted.append({
                'question_id': qid,
                'caption': caption,
                'explanation': explanation,
                'generated_choice': correct_choice,
                'incorrect_choice': incorrect_choice
            })

    # Write extracted and skipped records
    with open(extracted_output_file, 'w', encoding='utf-8') as out:
        json.dump(extracted, out, ensure_ascii=False, indent=2)

    if skipped_output_file:
        with open(skipped_output_file, 'w', encoding='utf-8') as skipf:
            json.dump(skipped, skipf, ensure_ascii=False, indent=2)

    print(f"Extracted {len(extracted)} entries to {extracted_output_file}")
    if skipped_output_file:
        print(f"Skipped {len(skipped)} entries to {skipped_output_file}")

def main():
    p = argparse.ArgumentParser(description="Extract caption, explanation, correct and incorrect choices from model outputs.")
    p.add_argument('-i', '--input_file', required=True, help='Path to input JSONL with model responses')
    p.add_argument('-e', '--extracted_output_file', required=True, help='Path to output JSON file (array)')
    p.add_argument('-s', '--skipped_output_file', required=False, help='Path to output JSON file for skipped entries (array)')
    args = p.parse_args()
    process_files(args.input_file, args.extracted_output_file, args.skipped_output_file)

if __name__ == '__main__':
    main()

