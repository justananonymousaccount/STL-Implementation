import json
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Rewrite JSONL questions into QA prompts."
    )
    parser.add_argument(
        '--questions_file', '-q',
        required=True,
        help='Path to the input JSONL file containing questions'
    )
    parser.add_argument(
        '--output_file', '-o',
        required=True,
        help='Path where the rewritten JSONL will be written'
    )
    args = parser.parse_args()

    # Prompt template
    prompt_template = (
        "You are an image based question-answering expert. "
        "Given an image along with a multiple choice question, your task is to select the correct choice based on the image. "
        "Your response should strictly follow the format with three specific sections: CAPTION, REASONING and CONCLUSION. Response:\n"
        "###CAPTION:[Provide a detailed description of the image, particularly emphasizing the aspects related to the question.]\n\n"
        "###REASONING:[Provide a detailed thought process to answer the question.]\n\n"
        "###CONCLUSION:[Provide the correct choice based on the reasoning.]\n\n\n"
        "Question: {question_and_choices}\n"
        "Response:\n"
    )

    with open(args.questions_file, 'r', encoding='utf-8') as qfile, \
         open(args.output_file, 'w', encoding='utf-8') as outfile:
        for line in qfile:
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            question_and_choices = data.get("text", "").strip()

            # Build the formatted prompt
            formatted_prompt = prompt_template.format(
                question_and_choices=question_and_choices
            )

            # Update and write out the record
            data["text"] = formatted_prompt
            outfile.write(json.dumps(data, ensure_ascii=False) + "\n")

    print(f"✅ Rewritten prompts written to {args.output_file}")

if __name__ == "__main__":
    main()

