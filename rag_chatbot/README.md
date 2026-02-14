# Production RAG Chatbot (PDF Book QA)

This project builds a Retrieval-Augmented Generation chatbot that answers questions only from one uploaded PDF book.

## Features

- Admin uploads PDF once using `/admin/upload` (or CLI script).
- Text extraction via `pypdf`.
- Chunking into fixed 500-word chunks.
- Embeddings with OpenAI API.
- FAISS vector store with cosine similarity search.
- Retriever `top_k=5`.
- FastAPI backend + Streamlit frontend.
- Source page numbers in responses.
- Confidence score in responses.
- Fallback answer: `Not found in the book`.
- Optimized for large books using batched embeddings and persistent FAISS index.

## Folder Structure

```text
rag_chatbot/
  backend/
    main.py
    config.py
    schemas.py
    rag/
      chunking.py
      embedder.py
      index_store.py
      ingestion.py
      retrieval.py
  frontend/
    app.py
  scripts/
    ingest_book.py
  data/
    .gitkeep
  Dockerfile.backend
  Dockerfile.frontend
  docker-compose.yml
  .dockerignore
  requirements.txt
  .env.example
```

## Step-by-Step Run

1. Create and activate a virtual environment.
```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.
```bash
pip install -r rag_chatbot/requirements.txt
```

3. Create `.env` from example.
```bash
copy rag_chatbot\.env.example .env
```
Set `OPENAI_API_KEY` in `.env`.

4. Start FastAPI backend.
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --app-dir rag_chatbot
```

5. Start Streamlit frontend in a second terminal.
```bash
streamlit run rag_chatbot/frontend/app.py
```

6. In Streamlit sidebar:
- Upload your PDF.
- Wait for indexing completion.
- Ask questions in chat.

## Run With Docker Compose

1. Create `.env` in `rag_chatbot/`.
```bash
copy rag_chatbot\.env.example rag_chatbot\.env
```
Set `OPENAI_API_KEY` in `rag_chatbot/.env`.

2. Build and start services.
```bash
cd rag_chatbot
docker compose up --build -d
```

3. Open apps:
- Streamlit UI: `http://localhost:8501`
- FastAPI docs: `http://localhost:8000/docs`

4. Stop services.
```bash
docker compose down
```

## Run Locally (Windows, Recommended if Docker is off)

1. One-time setup:
```powershell
powershell -ExecutionPolicy Bypass -File rag_chatbot\scripts\setup.ps1
py -3.11 -m venv rag_chatbot\.venv311
rag_chatbot\.venv311\Scripts\pip install -r rag_chatbot\requirements.txt
```

2. Start backend + frontend:
```powershell
powershell -ExecutionPolicy Bypass -File rag_chatbot\scripts\start_local.ps1
```

3. Check status:
```powershell
powershell -ExecutionPolicy Bypass -File rag_chatbot\scripts\status_local.ps1
```

4. Stop:
```powershell
powershell -ExecutionPolicy Bypass -File rag_chatbot\scripts\stop_local.ps1
```

## Optional: CLI Ingestion (Admin One-Time)

```bash
python -m scripts.ingest_book "C:\path\to\book.pdf"
```
Run this from project root with `PYTHONPATH=rag_chatbot` or use:
```bash
set PYTHONPATH=rag_chatbot
python rag_chatbot/scripts/ingest_book.py "C:\path\to\book.pdf"
```

## API Endpoints

- `POST /admin/upload?force=false` - Upload and start indexing.
- `GET /admin/status/{job_id}` - Ingestion job status.
- `POST /chat` - Ask question.
- `GET /health` - Health check and index readiness.

## Performance Notes for 1000+ Page Books

- Embeddings are batched (`EMBEDDING_BATCH_SIZE`) to reduce API overhead.
- FAISS index is persisted to disk and loaded once on startup.
- PDF is parsed page-by-page.
- Metadata is stored in JSONL for scalable sequential reads.
