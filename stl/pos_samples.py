import json
import argparse

# Prompt template matching the required format
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

# Load questions into a dict keyed by question_id
def load_questions(filename):
    questions = {}
    with open(filename, 'r', encoding='utf-8') as infile:
        for line in infile:
            record = json.loads(line.strip())
            qid = record.get('question_id')
            if qid is not None:
                questions[str(qid)] = record
    return questions

def generate_conversations(extractions, questions_dict):
    conversations = []
    for record in extractions:
        qid = str(record.get('question_id'))
        caption = record.get('caption', '').strip()
        rationale = record.get('rationale', '').strip()
        generated_choice = record.get('generated_choice')

        question_record = questions_dict.get(qid)
        if not question_record or not caption or not rationale or not generated_choice:
            continue

        question_text = question_record.get('text', '').strip()
        choices = question_record.get('choices') or []
        
        # Build question_and_choices string
        qc_lines = [question_text]
        for letter, choice_text in choices:
            qc_lines.append(f"({letter}) {choice_text}")
        question_and_choices = "\n".join(qc_lines)

        # Build human message
        human_value = "<image>\n" + prompt_template.format(question_and_choices=question_and_choices)

        # Build gpt message
        gpt_value = (
            f"CAPTION: {caption}\n\n"
            f"REASONING: {rationale}\n\n"
            f"CONCLUSION: {generated_choice}"
        )

        conversations.append({
            "id": int(qid) if qid.isdigit() else qid,
            "image": question_record.get('image', ''),
            "conversations": [
                {"from": "human", "value": human_value},
                {"from": "gpt", "value": gpt_value}
            ],
            "type": "1"
        })
    return conversations

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate human↔gpt conversation pairs using standardized prompt and extracted responses."
    )
    parser.add_argument('--questions_file', '-q', required=True,
                        help='Path to the questions JSONL file')
    parser.add_argument('--extractions_file', '-e', required=True,
                        help='Path to the JSON file with extracted caption, rationale, choice')
    parser.add_argument('--output_file', '-o', required=True,
                        help='Path for the output JSON file')
    args = parser.parse_args()

    questions = load_questions(args.questions_file)
    with open(args.extractions_file, 'r', encoding='utf-8') as ef:
        extractions = json.load(ef)

    convos = generate_conversations(extractions, questions)
    with open(args.output_file, 'w', encoding='utf-8') as outf:
        json.dump(convos, outf, indent=4)

    print(f"Total conversation objects generated: {len(convos)}")
