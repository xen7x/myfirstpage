# RunPod MLOps Deployment Guide

This guide maps out the high-throughput MLOps baton-relay for fine-tuning the "Key LLM" using our lightweight LoRA pipeline on a disposable spot-instance GPU on RunPod.

## 1. Launch RunPod Spot Instance

Launch a spot instance on RunPod (e.g., NVIDIA A100 or RTX 4090) to minimize costs.
Select a PyTorch base template or deploy our custom Docker image.

## 2. Environment Setup

Once the instance is running, connect via SSH or RunPod's web terminal.

```bash
# Clone the repository
git clone https://github.com/<org>/office20-unified-fortress.git
cd office20-unified-fortress

# (Optional) If not using our Dockerfile, build and run it:
docker build -t key-llm-trainer .
docker run --gpus all -it -v $(pwd):/workspace key-llm-trainer
```

## 3. Data Ingestion

Stream the cooked instruction dataset from our local NAS via rclone. Do NOT store raw data in the git repo.

```bash
# Example rclone command
rclone copy mynas:datasets/key_llm/train.jsonl /workspace/data/train.jsonl
```

## 4. Trigger Lightning-Fast Training Loop

Execute the training script to apply LoRA fine-tuning. Adjust the `--model_name_or_path` as needed (e.g., `Qwen/Qwen2.5-14B-Instruct` or `google/gemma-1.1-7b-it`).

```bash
python scripts/train_lora.py \
    --model_name_or_path Qwen/Qwen2.5-14B-Instruct \
    --dataset_path /workspace/data/train.jsonl \
    --output_dir ./lora_adapters_output \
    --batch_size 4 \
    --gradient_accumulation_steps 4
```

## 5. Exfiltrate LoRA Adapters

Download the resulting few-megabyte LoRA adapters back to your secure storage.

```bash
# Example rclone command to sync adapters back
rclone sync ./lora_adapters_output mynas:models/key_llm/adapters_v1
```

## 6. Terminate Instance

Immediately terminate/destroy the cloud billing node to ensure zero wasted cost.
