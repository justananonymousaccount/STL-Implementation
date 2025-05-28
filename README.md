# STL-Implementation
Implementation of See-Think-Learn (STL) Self-Training Framework for Multimodal Large Language Models

## 🛠️ Setup Instructions

To run this STL implementation, follow these steps:

### 1. Clone the LLaVA Repository

This STL framework builds on top of the [LLaVA](https://github.com/haotian-liu/LLaVA) codebase. First, clone the official LLaVA repo:

```sh
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA
```

### 2. Add STL Components

Place the following folders into the cloned LLaVA directory:

- `stl/` — contains the STL training logic and scripts.
- `playground/data/folder/` — contains the data files (`questions`, `answers`, etc.).
- `scripts/` — contains bash scripts for training and inference

Make sure to add the images from the [M3CoT](https://github.com/LightChen233/M3CoT) to the `playground/data/m3cot/images/` folder inside your cloned LLaVA directory.

### 3. Setup Environment

To run this project, begin by following the environment setup instructions provided in the official LLaVA repository. This includes installing required dependencies and setting up the training environment.

We provide a helper script to set up your Conda environment, project path, and CUDA paths.

Open [`scripts/start.sh`](scripts/start.sh) and configure the following:

```sh
# Activate Conda environment
source /your/conda/path/bin/activate
conda activate lava

# Navigate to the LLaVA project directory
cd /your/path/to/LLaVA

# CUDA path configuration (modify as per your installation)
export PATH=/your/cuda/path/bin:$PATH
export LD_LIBRARY_PATH=/your/cuda/path/lib64:$LD_LIBRARY_PATH

# (Optional) Weights & Biases API Key
# export WANDB_API_KEY=your_wandb_api_key_here
```
Run the script 

```sh
sh scripts/start.sh
```

All experiments were conducted on a single NVIDIA A6000 GPU (48GB VRAM) using CUDA 12.4. Further, xformers implementation is used for Lora finetuning instead of flash-attention.


### 4. Download the LLaVA-v1.5-7B Model

Download the LLaVA-v1.5-7B .zip file from the provided Google Drive link.
👉 [Download from Google Drive](https://drive.google.com/drive/folders/1hS2nfKXMhsBy8DmrMP7IytcmT-g6bI1K?usp=sharing)

Once downloaded, extract the content and place it inside the models/ folder within the LLaVA directory:

```sh
LLaVA/
├── models/
│   └── llava-v1.5-7b
```

## 🚀 Training through STL framework

This guide describes how to run the **See-Think-Learn (STL)** self-training pipeline on various domains of the **M3CoT** dataset using the `ours.sh` script.

### Domains Covered

We have conducted experiments on the following four domains from the M3CoT dataset:

- `commonsense`
- `science_natural`
- `science_social`
- `science_language`

---

### Running the STL Training Pipeline

To perform training and evaluation with the STL framework, execute the script `scripts/ours.sh` with the desired domain and maximum number of iterations.

### Script Overview

The `ours.sh` script automates the full STL process for each iteration. Internally, it sequentially runs:

1. `ours-part1.sh`: Positive sample generation  
2. `ours-neg.sh`: Negative sample generation  
3. `ours-part2.sh`: Model training and evaluation

### Usage

```bash
bash scripts/ours.sh <domain> <max_iteration>
```

- `<domain>`: One of the supported domains (`commonsense`, `science_natural`, `science_social`, `science_language`)
- `<max_iteration>`: Total number of STL iterations to perform (e.g., `5`)

### Example

To train on the `commonsense` domain for 5 STL iterations:

```bash
bash scripts/ours.sh commonsense 5
```

This will run all STL phases for 5 iterations on the specified domain.

