import json
from datasets import Dataset
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig

MAX_SEQ_LENGTH = 512
MODEL_NAME = "unsloth/Qwen2.5-3B-Instruct"
OUTPUT_DIR = "./output"
GGUF_DIR = "./qwen2.5-3b-wanju-gguf"


def load_jsonl(path):
    data = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data


def format_chat(example, tokenizer):
    text = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}


def main():
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    train_raw = load_jsonl("train_last.jsonl")
    valid_raw = load_jsonl("valid_last.jsonl")

    train_dataset = Dataset.from_list(
        [format_chat(d, tokenizer) for d in train_raw]
    )
    valid_dataset = Dataset.from_list(
        [format_chat(d, tokenizer) for d in valid_raw]
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        args=SFTConfig(
            dataset_text_field="text",
            max_seq_length=MAX_SEQ_LENGTH,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            num_train_epochs=3,
            learning_rate=2e-4,
            fp16=True,
            logging_steps=10,
            eval_strategy="steps",
            eval_steps=50,
            save_steps=100,
            output_dir=OUTPUT_DIR,
            warmup_ratio=0.1,
            lr_scheduler_type="cosine",
        ),
    )

    trainer.train()

    # Ollama에서 사용할 수 있는 GGUF 포맷으로 저장
    model.save_pretrained_gguf(GGUF_DIR, tokenizer, quantization_method="q4_k_m")
    print(f"[완료] GGUF 모델 저장: {GGUF_DIR}")


if __name__ == "__main__":
    main()
