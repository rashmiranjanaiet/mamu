from typing import List

import faiss
import numpy as np
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from backend.rag.embedder import OpenAIEmbedder
from backend.rag.index_store import ChunkRecord


class RetrievalService:
    def __init__(
        self,
        *,
        client: OpenAI,
        chat_model: str,
        embedder: OpenAIEmbedder,
        index: faiss.Index,
        records: List[ChunkRecord],
        min_confidence: float,
    ):
        self.client = client
        self.chat_model = chat_model
        self.embedder = embedder
        self.index = index
        self.records = records
        self.min_confidence = min_confidence

    def _confidence_from_score(self, score: float) -> float:
        # Scores are cosine similarities after vector normalization.
        return max(0.0, min(1.0, (score + 1.0) / 2.0))

    def search(self, question: str, top_k: int) -> List[dict]:
        query_vector = np.array([self.embedder.embed_query(question)], dtype=np.float32)
        faiss.normalize_L2(query_vector)
        scores, indices = self.index.search(query_vector, top_k)
        results: List[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.records):
                continue
            confidence = self._confidence_from_score(float(score))
            item = self.records[idx]
            results.append(
                {
                    "page": item.page,
                    "score": float(score),
                    "confidence": confidence,
                    "text": item.text,
                    "snippet": item.text[:220].strip(),
                }
            )
        return results

    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(4))
    def _answer_with_context(self, question: str, contexts: List[dict]) -> str:
        context_block = "\n\n".join(
            [f"[Page {c['page']}]\n{c['text']}" for c in contexts]
        )
        prompt = (
            "You are a strict retrieval QA assistant. "
            "Answer only with facts present in the provided context. "
            "If the answer is not in the context, output exactly: Not found in the book.\n\n"
            f"Question: {question}\n\nContext:\n{context_block}"
        )
        response = self.client.chat.completions.create(
            model=self.chat_model,
            temperature=0,
            messages=[
                {"role": "system", "content": "Answer from context only."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    def ask(self, question: str, top_k: int) -> dict:
        retrieved = self.search(question=question, top_k=top_k)
        if not retrieved:
            return {"answer": "Not found in the book", "confidence": 0.0, "sources": []}

        best_conf = max(r["confidence"] for r in retrieved)
        if best_conf < self.min_confidence:
            return {"answer": "Not found in the book", "confidence": best_conf, "sources": []}

        answer = self._answer_with_context(question=question, contexts=retrieved)
        if answer.strip().lower() == "not found in the book":
            return {"answer": "Not found in the book", "confidence": best_conf, "sources": []}

        sources = [
            {"page": r["page"], "score": r["confidence"], "snippet": r["snippet"]}
            for r in retrieved
        ]
        return {"answer": answer, "confidence": best_conf, "sources": sources}

