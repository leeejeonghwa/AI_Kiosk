import json
import os
from rank_bm25 import BM25Okapi

TRAIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "train_last.jsonl")


class RAGService:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        self.questions = []
        self.answers = []
        self._load_and_index()

    def _load_and_index(self):
        with open(TRAIN_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                messages = item.get("messages", [])
                q = next((m["content"] for m in messages if m["role"] == "user"), None)
                a = next((m["content"] for m in messages if m["role"] == "assistant"), None)
                if q and a:
                    self.questions.append(q)
                    self.answers.append(a)

        tokenized = [q.split() for q in self.questions]
        self.bm25 = BM25Okapi(tokenized)
        print(f"[RAG] {len(self.questions)}개 Q&A 인덱싱 완료")

    def retrieve(self, query: str) -> str:
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.top_k]

        context_parts = []
        for i in top_indices:
            if scores[i] > 0:
                context_parts.append(f"Q: {self.questions[i]}\nA: {self.answers[i]}")

        return "\n\n".join(context_parts)
