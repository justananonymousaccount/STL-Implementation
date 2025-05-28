#!/bin/sh

source /storage/miniconda3/bin/activate
conda activate lava

# Navigate to project directory
cd /storage/LLaVA

export PATH=/storage/cuda-12.4/bin:$PATH
export LD_LIBRARY_PATH=/storage/cuda-12.4/lib64:$LD_LIBRARY_PATH
#export WANDB_API_KEY=0ce5c0f....

