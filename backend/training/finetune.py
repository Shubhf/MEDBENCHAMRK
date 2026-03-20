"""LoRA Fine-tuning Script for MedResearchSLM-7B.

Compatible with Google Colab T4 (free tier).
Base model: mistralai/Mistral-7B-Instruct-v0.3
Training: QLoRA (4-bit quantization)

To run on Colab:
1. Upload this file
2. pip install peft trl transformers bitsandbytes datasets accelerate
3. Set HF_TOKEN environment variable
4. Run: python finetune.py
"""

from __future__ import annotations

import os

import torch
from datasets import load_dataset, Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer


# Configuration
BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
OUTPUT_DIR = "./medresearchslm-7b-lora"
HF_REPO = os.getenv("HF_MODEL_REPO", "shubhgarg/MedResearchSLM-7B")
MAX_SEQ_LENGTH = 2048
NUM_EPOCHS = 3
BATCH_SIZE = 4
LEARNING_RATE = 2e-4
LORA_RANK = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05


def load_training_data(path: str = "training_data.jsonl") -> Dataset:
    """Load training data from JSONL file or Supabase export."""
    if os.path.exists(path):
        return load_dataset("json", data_files=path, split="train")

    # Fallback: create sample data
    samples = [
        {
            "instruction": "Identify research gaps in the following medical AI papers on retinal imaging.",
            "input": "Paper 1: U-Net for retinal vessel segmentation on DRIVE (Dice: 0.82). Paper 2: ResNet50 for DR grading on EyePACS (AUC: 0.95).",
            "output": "Gap 1: No transformer-based approaches have been applied to retinal vessel segmentation. Gap 2: No OCT imaging modality explored alongside fundus photography. Gap 3: Both papers use single-center datasets with no multi-center validation.",
        },
        {
            "instruction": "Extract medical entities from this paper abstract.",
            "input": "We propose a Vision Transformer for brain tumor segmentation on BraTS 2021 achieving Dice score of 0.91 using MRI T1 and FLAIR sequences.",
            "output": '{"imaging_modalities": ["MRI"], "anatomies": ["brain"], "conditions": ["brain tumor"], "architectures": ["ViT"], "datasets": ["BraTS"], "metrics": ["Dice"], "techniques": ["segmentation"]}',
        },
    ]
    return Dataset.from_list(samples)


def format_prompt(example: dict) -> str:
    """Format training example into instruction-following format."""
    return f"""<s>[INST] {example['instruction']}

{example['input']} [/INST]

{example['output']}</s>"""


def main():
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    print("Loading model with 4-bit quantization...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    print("Applying LoRA...")
    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    print("Loading training data...")
    dataset = load_training_data()

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=4,
        learning_rate=LEARNING_RATE,
        weight_decay=0.01,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        logging_steps=10,
        save_strategy="epoch",
        fp16=True,
        optim="paged_adamw_8bit",
        max_grad_norm=0.3,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        tokenizer=tokenizer,
        args=training_args,
        max_seq_length=MAX_SEQ_LENGTH,
        formatting_func=format_prompt,
    )

    print("Starting training...")
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"Model saved to {OUTPUT_DIR}")

    # Push to HuggingFace
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        print(f"Pushing to HuggingFace: {HF_REPO}")
        model.push_to_hub(HF_REPO, token=hf_token)
        tokenizer.push_to_hub(HF_REPO, token=hf_token)
        print("Upload complete!")


if __name__ == "__main__":
    main()
