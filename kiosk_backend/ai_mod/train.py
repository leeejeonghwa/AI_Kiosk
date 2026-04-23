import os
import json
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
)
from trl import SFTTrainer, SFTConfig

MAX_SEQ_LENGTH = 256
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
OUTPUT_DIR = "./output"
SAVE_DIR = "./qwen2.5-1.5b-wanju"


def load_jsonl(path):
    data = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def format_chat(example, tokenizer):
    text = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}


def main():
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU를 찾지 못했습니다. GPU 환경에서 실행하세요.")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(base_dir, "train_last.jsonl")
    valid_path = os.path.join(base_dir, "valid_last.jsonl")

    if not os.path.exists(train_path):
        raise FileNotFoundError(f"학습 파일을 찾을 수 없습니다: {train_path}")
    if not os.path.exists(valid_path):
        raise FileNotFoundError(f"검증 파일을 찾을 수 없습니다: {valid_path}")

    if torch.cuda.is_bf16_supported():
        compute_dtype = torch.bfloat16
        use_bf16 = True
        use_fp16 = False
    else:
        compute_dtype = torch.float16
        use_bf16 = False
        use_fp16 = True

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        dtype=compute_dtype,
    )

    model.config.use_cache = False
    model.config.pad_token_id = tokenizer.pad_token_id

    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    train_raw = load_jsonl(train_path)
    valid_raw = load_jsonl(valid_path)

    train_dataset = Dataset.from_list(
        [format_chat(d, tokenizer) for d in train_raw]
    )
    valid_dataset = Dataset.from_list(
        [format_chat(d, tokenizer) for d in valid_raw]
    )

    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        dataset_text_field="text",

        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8,

        num_train_epochs=3,
        learning_rate=2e-4,
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",

        logging_steps=10,
        eval_steps=50,
        save_steps=50,
        save_strategy="steps",

        save_total_limit=2,

        fp16=use_fp16,
        bf16=use_bf16,

        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        args=training_args,
    )
    trainer.train()

    model.save_pretrained(SAVE_DIR)
    tokenizer.save_pretrained(SAVE_DIR)
    print(f"[완료] 모델 저장: {SAVE_DIR}")


if __name__ == "__main__":
    main()