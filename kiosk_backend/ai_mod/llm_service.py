import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
try:
    from .rag_service import RAGService
except ImportError:
    from rag_service import RAGService

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

        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        print(f"[LLM] device: {'CUDA' if torch.cuda.is_available() else 'CPU'}, dtype: {dtype}")

        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_DIR,
            torch_dtype=dtype,
            device_map="auto",
            local_files_only=True,
        )

        self.model = PeftModel.from_pretrained(
            base_model,
            LORA_DIR,
            local_files_only=True,
        ).merge_and_unload()

        self.model.eval()
        self.rag = RAGService()
        print("[LLM] 모델 로딩 완료")

    _FIXED_ANSWERS = [
        (["이름", "누구"], "저는 미라키입니다."),
        (["무슨 날", "무슨날", "오늘이 뭔", "오늘 뭔", "어떤 날"], "오늘은 어린이날입니다."),
    ]

    def generate_answer(self, user_text: str) -> str:
        user_text = (user_text or "").strip()
        if not user_text:
            return "질문을 잘 듣지 못했어요. 다시 말씀해 주세요."

        for keywords, answer in self._FIXED_ANSWERS:
            if any(kw in user_text for kw in keywords):
                return answer

        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 완주군 키오스크 AI 안내원 미라키입니다. "
                    "이름을 물으면 '저는 미라키입니다.'라고 답하세요. "
                    "오늘이 무슨 날이냐고 물으면 '오늘은 어린이날입니다.'라고 답하세요. "
                    "반드시 한국어로만 답변하고, 100자 이내로 간결하게 말하세요. "
                    "모르는 내용은 직원에게 문의하라고 안내하세요.\n\n"
                    f"참고 정보:\n{self.rag.retrieve(user_text)}"
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
            max_length=2048,
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

        # 한국어, 숫자, 공백, 기본 문장부호만 남김
        answer = re.sub(r"[^가-힣㄰-㆏ᄀ-ᇿ0-9\s.,!?~%\-]", "", answer).strip()

        if len(answer) > 120:
            answer = answer[:120].strip() + "..."

        return answer if answer else "답변을 생성하지 못했습니다."