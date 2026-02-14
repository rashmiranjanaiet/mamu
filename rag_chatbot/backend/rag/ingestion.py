import json
import shutil
from pathlib import Path
from typing import List

import faiss
import numpy as np
from pypdf import PdfReader

from backend.rag.chunking import chunk_page_text
from backend.rag.embedder import OpenAIEmbedder
from backend.rag.index_store import ChunkRecord, FaissStore


class IngestionService:
    def __init__(self, store: FaissStore, embedder: OpenAIEmbedder, chunk_size_words: int):
        self.store = store
        self.embedder = embedder
        self.chunk_size_words = chunk_size_words

    def ingest_pdf(self, pdf_path: Path) -> dict:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        reader = PdfReader(str(pdf_path))
        index = None
        total_chunks = 0
        batch_texts: List[str] = []
        batch_records: List[ChunkRecord] = []
        temp_meta_path = self.store.meta_path.with_suffix(".tmp.jsonl")

        def flush_batch(meta_handle) -> None:
            nonlocal index, total_chunks, batch_texts, batch_records
            if not batch_texts:
                return
            vectors = self.embedder.embed_texts(batch_texts)
            matrix = np.array(vectors, dtype=np.float32)
            faiss.normalize_L2(matrix)
            if index is None:
                index = faiss.IndexFlatIP(matrix.shape[1])
            index.add(matrix)
            for rec in batch_records:
                meta_handle.write(json.dumps({"text": rec.text, "page": rec.page}, ensure_ascii=True) + "\n")
            total_chunks += len(batch_records)
            batch_texts = []
            batch_records = []

        with temp_meta_path.open("w", encoding="utf-8") as meta_handle:
            for page_idx, page in enumerate(reader.pages, start=1):
                raw_text = page.extract_text() or ""
                for chunk in chunk_page_text(raw_text, page_idx, self.chunk_size_words):
                    batch_texts.append(chunk.text)
                    batch_records.append(ChunkRecord(text=chunk.text, page=chunk.page))
                    if len(batch_texts) >= self.embedder.batch_size:
                        flush_batch(meta_handle)
            flush_batch(meta_handle)

        if index is None or total_chunks == 0:
            temp_meta_path.unlink(missing_ok=True)
            raise ValueError("No text was extracted from this PDF.")

        faiss.write_index(index, str(self.store.index_path))
        temp_meta_path.replace(self.store.meta_path)

        shutil.copy2(pdf_path, self.store.book_path)
        return {
            "pages": len(reader.pages),
            "chunks": total_chunks,
            "book_path": str(self.store.book_path),
        }
