import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

BASE_MODEL_DIR = os.path.join(ROOT_DIR, "qwen2.5-1.5b-base").replace("\\", "/")
LORA_DIR = os.path.join(ROOT_DIR, "qwen2.5-1.5b-wanju").replace("\\", "/")

class LLMService:
    def __init__(self):
        print("[LLM] base 모델 로딩 중:", BASE_MODEL_DIR)
        print("[LLM] LoRA 로딩 중:", LORA_DIR)

        self.tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL_DIR,
            local_files_only=True,
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_DIR,
            dtype=torch.float16,
            device_map="auto",
            local_files_only=True,
        )

        self.model = PeftModel.from_pretrained(
            base_model,
            LORA_DIR,
            local_files_only=True,
        )

        self.model.eval()
        print("[LLM] 모델 로딩 완료")

    def generate_answer(self, user_text: str) -> str:
        user_text = (user_text or "").strip()
        if not user_text:
            return "질문을 잘 듣지 못했어요. 다시 말씀해 주세요."

        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 안내 키오스크 AI입니다. "
                    "사용자의 질문에 한국어로 자연스럽고 100자 이내로 간결하게 답변하세요. "
                    "모르는 내용은 지어내지 말고 담당자에게 문의하라고 안내하세요."
                ),
            },
            {"role": "user", "content": user_text},
        ]

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=128,
                do_sample=False,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        input_length = inputs["input_ids"].shape[-1]
        new_tokens = output_ids[0][input_length:]
        answer = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        if len(answer) > 120:
            answer = answer[:120].strip() + "..."

        return answer if answer else "답변을 생성하지 못했습니다."