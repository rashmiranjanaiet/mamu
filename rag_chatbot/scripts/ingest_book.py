import argparse
from pathlib import Path

from backend.config import settings
from backend.rag.embedder import OpenAIEmbedder
from backend.rag.index_store import FaissStore
from backend.rag.ingestion import IngestionService


def main() -> None:
    parser = argparse.ArgumentParser(description="Index a PDF book into FAISS.")
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF file")
    args = parser.parse_args()

    store = FaissStore(base_dir=settings.app_data_dir)
    embedder = OpenAIEmbedder(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
        batch_size=settings.embedding_batch_size,
    )
    ingestion = IngestionService(
        store=store,
        embedder=embedder,
        chunk_size_words=settings.chunk_size_words,
    )

    result = ingestion.ingest_pdf(args.pdf_path)
    print(
        f"Index complete: {result['pages']} pages, {result['chunks']} chunks, "
        f"saved to {result['book_path']}"
    )


if __name__ == "__main__":
    main()

