#!/bin/bash
# This script runs the training and evaluation pipeline for a given iteration and domain.
# Usage: ./run_pipeline.sh <num> <domain>

# Validate input arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <num> <domain>"
    exit 1
fi

# Set variables
num=$1
domain=$2
prev_num=$((num - 1))

# Set Hugging Face cache directory locally
export HF_HOME=.

echo "Starting training for iteration ${num}, domain '${domain}'"

# ============================
# Step 1: Train the model
# ============================
echo "Step 1: Training the model with DeepSpeed"
deepspeed llava/train/train_xformers.py \
    --lora_enable True --lora_r 128 --lora_alpha 256 --mm_projector_lr 2e-5 \
    --deepspeed ./scripts/zero3.json \
    --model_name_or_path ./models/llava-v1.5-7b \
    --version v1 \
    --data_path ./${domain}/ours/training_set_it${num}.json \
    --image_folder . \
    --vision_tower openai/clip-vit-large-patch14-336 \
    --mm_projector_type mlp2x_gelu \
    --mm_vision_select_layer -2 \
    --mm_use_im_start_end False \
    --mm_use_im_patch_token False \
    --image_aspect_ratio pad \
    --group_by_modality_length True \
    --bf16 False \
    --output_dir ./results/${domain}/ours/llava-v1.5-7b-lora-oursit${num} \
    --num_train_epochs 1 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 1000 \
    --save_total_limit 1 \
    --learning_rate 2e-4 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --tf32 False \
    --model_max_length 1024 \
    --gradient_checkpointing True \
    --dataloader_num_workers 4 \
    --lazy_preprocess True \
    --report_to wandb

# ============================
# Step 2: Merge LoRA weights
# ============================
echo "Step 2: Merging LoRA weights into base model"
python scripts/merge_lora_weights.py \
  --model-path ./results/${domain}/ours/llava-v1.5-7b-lora-oursit${num} \
  --model-base ./models/llava-v1.5-7b \
  --save-model-path ./models/${domain}/ours/llava-v1.5-7b-lora-oursit${num}

# ============================
# Step 3: Run model on test set
# ============================
echo "Step 3: Running model on test set"
python llava/eval/model_vqa.py \
  --model-path ./models/${domain}/ours/llava-v1.5-7b-lora-oursit${num} \
  --question-file ./playground/data/folder/formatted_questions_test_${domain}.jsonl \
  --image-folder . \
  --answers-file ./${domain}/ours/response_test_it${num}.jsonl

# ============================
# Step 4: Extract predictions
# ============================
echo "Step 4: Extracting predictions from model responses"
python stl/extraction.py \
  --input_file ./${domain}/ours/response_test_it${num}.jsonl \
  --extracted_output_file ./${domain}/ours/extracted_test_it${num}.json \
  --skipped_output_file ./${domain}/ours/skipped_test_it${num}.json

# ============================
# Step 5: Compute accuracy
# ============================
echo "Step 5: Computing accuracy on test set"
python stl/accuracy.py \
  --extracted_file ./${domain}/ours/extracted_test_it${num}.json \
  --correct_answers_file ./playground/data/folder/correct_answers_test.json

echo "Pipeline completed successfully for iteration ${num}, domain '${domain}' ✅"
