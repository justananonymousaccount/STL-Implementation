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

echo "Running negative-sample pipeline: iteration ${num}, domain '${domain}', using model from iteration ${prev_num}"

# Step 1: Generate negative prompts from correct extractions
echo "Step 1: Create negative prompts from correct extractions of current iteration."
python stl/neg_prompts.py \
  --extractions_file ./${domain}/ours/correct_train_it${num}.json \
  --questions_file playground/data/folder/questions_train_${domain}.jsonl \
  --output_file ./${domain}/ours/neg_from_correct_prompts_it${num}.jsonl

# Step 2: Use model from previous iteration to generate answers to the negative prompts
echo "Step 2: Run model from previous iteration on the generated negative prompts."
python llava/eval/model_vqa.py \
  --model-path ./models/${domain}/ours/llava-v1.5-7b-lora-oursit${prev_num} \
  --question-file ./${domain}/ours/neg_from_correct_prompts_it${num}.jsonl \
  --image-folder . \
  --answers-file ./${domain}/ours/response_neg_train_it${num}.jsonl

# Step 3: Extract caption, explanation, and incorrect choice from responses
echo "Step 3: Extract training signals (caption, explanation, incorrect choice) from model responses."
python stl/extraction_neg.py \
  -i ./${domain}/ours/response_neg_train_it${num}.jsonl \
  -e ./${domain}/ours/extracted_train_neg_it${num}.jsonl \
  -s ./${domain}/ours/skipped_train_neg_it${num}.json

# Step 4: Generate final negative samples using those extractions
echo "Step 4: Construct negative training samples from extracted responses."
python stl/neg_samples.py \
  --extractions_file ./${domain}/ours/extracted_train_neg_it${num}.jsonl \
  --questions_file playground/data/folder/questions_train_${domain}.jsonl \
  --output_file ./${domain}/ours/neg_train_samples_it${num}.json

# Step 5: Merge positive and negative samples into final training set
echo "Step 5: Merge positive and negative samples into final training set for this iteration."
python stl/final_training_set.py \
  --input_files ./${domain}/ours/pos_samples_train_it${num}.json ./${domain}/ours/neg_train_samples_it${num}.json \
  --output_file ./${domain}/ours/training_set_it${num}.json

echo "Iteration ${num} for domain '${domain}' completed successfully ✅"

