import shutil
import threading
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from backend.config import settings
from backend.rag.embedder import OpenAIEmbedder
from backend.rag.index_store import FaissStore
from backend.rag.ingestion import IngestionService
from backend.rag.retrieval import RetrievalService
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    JobStatus,
    LocalIndexRequest,
    UploadResponse,
)

app = FastAPI(title="Book RAG Chatbot", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = FaissStore(base_dir=settings.app_data_dir)
embedder = OpenAIEmbedder(
    api_key=settings.openai_api_key,
    model=settings.embedding_model,
    batch_size=settings.embedding_batch_size,
)
ingestion_service = IngestionService(
    store=store, embedder=embedder, chunk_size_words=settings.chunk_size_words
)

_jobs_lock = threading.Lock()
_jobs: dict[str, dict] = {}
_retrieval_lock = threading.Lock()
_retrieval_service: RetrievalService | None = None


def _load_retrieval_service() -> None:
    global _retrieval_service
    if not store.exists():
        _retrieval_service = None
        return
    index, records = store.load()
    client = OpenAI(api_key=settings.openai_api_key)
    _retrieval_service = RetrievalService(
        client=client,
        chat_model=settings.chat_model,
        embedder=embedder,
        index=index,
        records=records,
        min_confidence=settings.min_confidence,
    )


def _set_job(job_id: str, status: str, detail: str) -> None:
    with _jobs_lock:
        _jobs[job_id] = {"status": status, "detail": detail}


def _run_ingestion_job(job_id: str, file_path: Path, cleanup_file: bool = True) -> None:
    _set_job(job_id, "running", "Indexing started")
    try:
        result = ingestion_service.ingest_pdf(file_path)
        with _retrieval_lock:
            _load_retrieval_service()
        _set_job(
            job_id,
            "completed",
            f"Indexed {result['pages']} pages into {result['chunks']} chunks.",
        )
    except Exception as exc:  # noqa: BLE001
        _set_job(job_id, "failed", str(exc))
    finally:
        if cleanup_file and file_path.exists():
            file_path.unlink()


@app.on_event("startup")
def startup_event() -> None:
    # Auto-index a configured local book once if index is missing.
    if not store.exists() and settings.default_book_pdf_path:
        auto_path = Path(settings.default_book_pdf_path).expanduser()
        if auto_path.exists() and auto_path.is_file() and auto_path.suffix.lower() == ".pdf":
            try:
                ingestion_service.ingest_pdf(auto_path)
            except Exception:  # noqa: BLE001
                pass
    with _retrieval_lock:
        _load_retrieval_service()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "indexed": store.exists()}


@app.post("/admin/upload", response_model=UploadResponse)
async def upload_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    force: bool = Query(default=False),
) -> UploadResponse:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")
    if store.exists() and not force:
        raise HTTPException(
            status_code=409,
            detail="A book is already indexed. Use force=true to replace it.",
        )

    temp_dir = settings.app_data_dir / "tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{uuid.uuid4()}.pdf"
    with temp_path.open("wb") as handle:
        shutil.copyfileobj(file.file, handle)

    job_id = str(uuid.uuid4())
    _set_job(job_id, "queued", "Upload accepted")
    background_tasks.add_task(_run_ingestion_job, job_id, temp_path)
    return UploadResponse(job_id=job_id, status="queued", message="Ingestion started.")


@app.post("/admin/index-local", response_model=UploadResponse)
def index_local_book(
    payload: LocalIndexRequest,
    background_tasks: BackgroundTasks,
) -> UploadResponse:
    pdf_path = Path(payload.pdf_path).expanduser()
    if not pdf_path.exists() or not pdf_path.is_file():
        raise HTTPException(status_code=400, detail="PDF path does not exist.")
    if pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="File must be a .pdf")
    if store.exists() and not payload.force:
        raise HTTPException(
            status_code=409,
            detail="A book is already indexed. Set force=true to replace it.",
        )

    job_id = str(uuid.uuid4())
    _set_job(job_id, "queued", "Local indexing accepted")
    background_tasks.add_task(_run_ingestion_job, job_id, pdf_path, False)
    return UploadResponse(job_id=job_id, status="queued", message="Local indexing started.")


@app.get("/admin/status/{job_id}", response_model=JobStatus)
def upload_status(job_id: str) -> JobStatus:
    with _jobs_lock:
        data = _jobs.get(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JobStatus(job_id=job_id, status=data["status"], detail=data["detail"])


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    with _retrieval_lock:
        if _retrieval_service is None:
            raise HTTPException(status_code=503, detail="No indexed book available.")
        service = _retrieval_service
    result = service.ask(question=payload.question, top_k=payload.top_k or settings.top_k)
    return ChatResponse(**result)
