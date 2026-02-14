from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Chunk:
    text: str
    page: int


def split_words(text: str) -> List[str]:
    return [token for token in text.split() if token]


def chunk_page_text(page_text: str, page_number: int, chunk_size_words: int) -> Iterable[Chunk]:
    words = split_words(page_text)
    if not words:
        return
    for idx in range(0, len(words), chunk_size_words):
        chunk_words = words[idx : idx + chunk_size_words]
        if not chunk_words:
            continue
        yield Chunk(text=" ".join(chunk_words), page=page_number)

