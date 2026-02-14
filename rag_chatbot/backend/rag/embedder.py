from typing import Iterable, List

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential


class OpenAIEmbedder:
    def __init__(self, api_key: str, model: str, batch_size: int = 128):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.batch_size = batch_size

    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(5))
    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        text_list = list(texts)
        vectors: List[List[float]] = []
        for i in range(0, len(text_list), self.batch_size):
            vectors.extend(self._embed_batch(text_list[i : i + self.batch_size]))
        return vectors

    def embed_query(self, text: str) -> List[float]:
        return self._embed_batch([text])[0]

