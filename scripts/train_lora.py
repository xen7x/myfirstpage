import os
import json
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
from datasets import load_dataset

def main():
    parser = argparse.ArgumentParser(description="LoRA fine-tuning for Key LLM")
    parser.add_argument("--model_name_or_path", type=str, required=True, help="Base model path or HuggingFace ID")
    parser.add_argument("--dataset_path", type=str, required=True, help="Path to jsonl dataset")
    parser.add_argument("--output_dir", type=str, default="./lora_adapters", help="Output directory for adapters")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size per device")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4, help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--num_train_epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--lora_r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=32, help="LoRA alpha")
    parser.add_argument("--lora_dropout", type=float, default=0.05, help="LoRA dropout")

    args = parser.parse_args()

    print(f"Loading model: {args.model_name_or_path}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Determine if we can use 4-bit quantization (useful for large models like Qwen 2.5 14B)
    use_4bit = torch.cuda.is_available()

    if use_4bit:
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            args.model_name_or_path,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        model = prepare_model_for_kbit_training(model)
    else:
        # Fallback for MLX/CPU/MPS if CUDA is not available
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        model = AutoModelForCausalLM.from_pretrained(
            args.model_name_or_path,
            torch_dtype=torch.float16 if device == "mps" else torch.float32,
            device_map=device,
            trust_remote_code=True
        )

    # Configure LoRA
    peft_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    )

    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Load dataset
    print(f"Loading dataset: {args.dataset_path}")
    dataset = load_dataset("json", data_files=args.dataset_path, split="train")

    def format_prompts(example):
        output_texts = []
        for i in range(len(example['messages'])):
            messages = example['messages'][i]
            # Use the tokenizer's chat template if available, else manual formatting
            try:
                formatted = tokenizer.apply_chat_template(messages, tokenize=False)
            except Exception:
                formatted = ""
                for msg in messages:
                    role = msg["role"]
                    content = msg["content"]
                    if role == "system":
                        formatted += f"<|system|>\n{content}</s>\n"
                    elif role == "user":
                        formatted += f"<|user|>\n{content}</s>\n"
                    elif role == "assistant":
                        formatted += f"<|assistant|>\n{content}</s>\n"
            output_texts.append(formatted)
        return output_texts

    # Set up SFT Trainer
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        logging_steps=10,
        max_steps=-1,
        num_train_epochs=args.num_train_epochs,
        save_strategy="epoch",
        optim="paged_adamw_32bit" if use_4bit else "adamw_torch",
        fp16=use_4bit,
        bf16=False,
        report_to="none", # Disable wandb for cleaner local runs
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        formatting_func=format_prompts,
        max_seq_length=2048,
        tokenizer=tokenizer,
        args=training_args,
    )

    print("Starting training...")
    trainer.train()

    print(f"Saving LoRA adapters to {args.output_dir}...")
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    print("Training complete!")

if __name__ == "__main__":
    main()
