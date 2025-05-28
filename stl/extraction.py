import json
import re
import argparse

# Regex patterns for sections
caption_pattern = r"CAPTION:\s*(.*?)\s*(?:REASONING:|$)"
reasoning_pattern = r"REASONING:\s*(.*?)\s*(?:CONCLUSION:|$)"
conclusion_pattern = r"CONCLUSION:\s*(.*)"
# Patterns for Method2 & Method3
letter_pattern = r"\(([a-z])\)"
choice_line_pattern = r"\(([a-z])\)\s*(.+)"

# Threshold for excessive zeros (optional)
ZERO_THRESHOLD = 50


def extract_using_methods(conclusion_text, prompt_text):
    """
    Attempt Method3 and Method2 on the conclusion text if Method1 failed.
    """
    # Method3: single letter in conclusion text only
    matches = re.findall(letter_pattern, conclusion_text)
    if matches and len(set(matches)) == 1:
        return f"({list(set(matches))[0]})"  # Method3

    # Method2: map prompt choices to occurrences in conclusion text
    choices_mapping = {}
    prompt_block = prompt_text.split("Question:")[-1]
    for line in prompt_block.splitlines():
        m = re.match(choice_line_pattern, line.strip())
        if m:
            choices_mapping[m.group(1)] = m.group(2).strip()

    found = {}
    for letter, text in choices_mapping.items():
        if re.search(re.escape(text), conclusion_text, re.IGNORECASE):
            found[letter] = text
    if len(found) == 1:
        return f"({list(found.keys())[0]})"  # Method2

    return None


def process_files(input_file, extracted_output_file, skipped_output_file=None):
    extracted = []
    skipped = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            qid = data.get('question_id')
            prompt_text = data.get('prompt', '')
            resp = data.get('text', '')

            # Extract sections
            cap_m = re.search(caption_pattern, resp, re.DOTALL|re.IGNORECASE)
            reason_m = re.search(reasoning_pattern, resp, re.DOTALL|re.IGNORECASE)
            concl_m = re.search(conclusion_pattern, resp, re.DOTALL|re.IGNORECASE)

            caption = cap_m.group(1).strip() if cap_m else None
            rationale = reason_m.group(1).strip() if reason_m else None

            # Extract conclusion text if present
            conclusion_text = concl_m.group(1).strip() if concl_m else ''

            # Method1: direct letter extraction from conclusion section
            choice = None
            if conclusion_text:
                m = re.search(letter_pattern, conclusion_text)
                if m:
                    choice = f"({m.group(1)})"

            # Fallbacks: Method3 then Method2, both using conclusion_text
            if not choice:
                choice = extract_using_methods(conclusion_text, prompt_text)

            # Skip if anything missing or bad
            if not (caption and rationale and choice):
                skipped.append(data)
                continue
            if rationale.count('0') > ZERO_THRESHOLD:
                skipped.append(data)
                continue

            extracted.append({
                'question_id': qid,
                'caption': caption,
                'rationale': rationale,
                'generated_choice': choice
            })

    # Write outputs as JSON arrays
    with open(extracted_output_file, 'w', encoding='utf-8') as out:
        json.dump(extracted, out, ensure_ascii=False, indent=2)

    if skipped_output_file:
        with open(skipped_output_file, 'w', encoding='utf-8') as skipf:
            json.dump(skipped, skipf, ensure_ascii=False, indent=2)

    print(f"Extracted {len(extracted)} entries to {extracted_output_file}")
    if skipped_output_file:
        print(f"Skipped {len(skipped)} entries to {skipped_output_file}")


def main():
    p = argparse.ArgumentParser(description="Extract caption, rationale, and choice with conclusion-based fallbacks")
    p.add_argument('-i','--input_file', required=True, help='Path to input JSONL with model responses')
    p.add_argument('-e','--extracted_output_file', required=True, help='Path to output JSON file (array)')
    p.add_argument('-s','--skipped_output_file', required=False, help='Path to output JSON file for skipped entries (array)')
    args = p.parse_args()
    process_files(args.input_file, args.extracted_output_file, args.skipped_output_file)

if __name__ == '__main__':
    main()

