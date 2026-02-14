import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Sequence

import faiss
import numpy as np


@dataclass
class ChunkRecord:
    text: str
    page: int


class FaissStore:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.base_dir / "book.index"
        self.meta_path = self.base_dir / "book_meta.jsonl"
        self.book_path = self.base_dir / "book.pdf"

    def exists(self) -> bool:
        return self.index_path.exists() and self.meta_path.exists()

    def save(self, vectors: Sequence[Sequence[float]], records: Sequence[ChunkRecord]) -> None:
        if not vectors or not records or len(vectors) != len(records):
            raise ValueError("Vectors and records must be non-empty and have the same length.")

        matrix = np.array(vectors, dtype=np.float32)
        faiss.normalize_L2(matrix)
        dim = matrix.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(matrix)
        faiss.write_index(index, str(self.index_path))

        with self.meta_path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(asdict(record), ensure_ascii=True) + "\n")

    def load(self) -> tuple[faiss.Index, List[ChunkRecord]]:
        if not self.exists():
            raise FileNotFoundError("FAISS index or metadata does not exist.")
        index = faiss.read_index(str(self.index_path))
        records: List[ChunkRecord] = []
        with self.meta_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                payload = json.loads(line)
                records.append(ChunkRecord(text=payload["text"], page=payload["page"]))
        return index, records

