#!/bin/bash

# Check for exactly two arguments: iteration number and domain name
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <num> <domain>"
    exit 1
fi

# Set variables
num=$1
domain=$2
prev_num=$((num - 1))

echo "Running positive-sample pipeline: iteration ${num}, domain '${domain}', using model from iteration ${prev_num}"

# Step 1: Generate positive prompts from question file
echo "Step 1: Generate positive prompts from questions."
python stl/pos_prompts.py \
  --questions_file playground/data/folder/questions_train_${domain}.jsonl \
  --output_file ./${domain}/ours/pos_prompts_it${num}.jsonl

# Step 2: Run VQA model from previous iteration on positive prompts
echo "Step 2: Run model from previous iteration on positive prompts."
python llava/eval/model_vqa.py \
  --model-path ./models/${domain}/ours/llava-v1.5-7b-lora-oursit${prev_num} \
  --question-file ./${domain}/ours/pos_prompts_it${num}.jsonl \
  --image-folder . \
  --answers-file ./${domain}/ours/response_pos_it${num}.jsonl

# Step 3: Extract answers from model responses
echo "Step 3: Extract model outputs (caption, explanation, choice) from responses."
python stl/extraction.py \
  --input_file ./${domain}/ours/response_pos_it${num}.jsonl \
  --extracted_output_file ./${domain}/ours/extracted_train_it${num}.json \
  --skipped_output_file ./${domain}/ours/skipped_train_it${num}.json

# Step 4: Split extractions into correct and incorrect predictions
echo "Step 4: Separate correct and incorrect model predictions."
python stl/correct_incorrect.py \
  --extracted_file ./${domain}/ours/extracted_train_it${num}.json \
  --correct_answers_file playground/data/folder/correct_answers_train.json \
  --correct_output_file ./${domain}/ours/correct_train_it${num}.json \
  --incorrect_output_file ./${domain}/ours/incorrect_train_it${num}.json

# Step 5: Generate final positive training samples from correct predictions
echo "Step 5: Build positive training samples from correct extractions."
python stl/pos_samples.py \
  --questions_file playground/data/folder/questions_train_${domain}.jsonl \
  --extractions_file ./${domain}/ours/correct_train_it${num}.json \
  --output_file ./${domain}/ours/pos_samples_train_it${num}.json

echo "Iteration ${num} for domain '${domain}' completed successfully ✅"
