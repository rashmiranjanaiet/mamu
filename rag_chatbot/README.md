# Production RAG Chatbot (PDF Book QA)

This project builds a Retrieval-Augmented Generation chatbot that answers questions only from one indexed PDF book.

## Features

- Admin indexes PDF locally (CLI/startup path). Web users only ask questions.
- Text extraction via `pypdf`.
- Chunking into fixed 500-word chunks.
- Embeddings and chat via OpenAI-compatible API (OpenAI or Gemini endpoint).
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

3. Create `rag_chatbot/.env` from example.
```bash
copy rag_chatbot\.env.example rag_chatbot\.env
```
Set your API settings in `rag_chatbot/.env`.

4. Start FastAPI backend.
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --app-dir rag_chatbot
```

5. Start Streamlit frontend in a second terminal.
```bash
streamlit run rag_chatbot/frontend/app.py
```

6. Streamlit web app:
- Upload is disabled by default (`ENABLE_ADMIN_UI=false`).
- Users can only ask questions in chat.

## Provider Setup

Use one provider style in `rag_chatbot/.env`.

OpenAI example:
```env
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_BATCH_SIZE=128
```

Gemini (OpenAI-compatible) example:
```env
OPENAI_API_KEY=your_gemini_key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
CHAT_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_BATCH_SIZE=100
```

Note: for Gemini embeddings, keep `EMBEDDING_BATCH_SIZE` at `100` or lower.

## Run With Docker Compose

1. Create `.env` in `rag_chatbot/`.
```bash
copy rag_chatbot\.env.example rag_chatbot\.env
```
Set provider settings in `rag_chatbot/.env` (see Provider Setup above).

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

## Deploy On Render

This repo includes a Render Blueprint file: `render.yaml` (at repo root).

1. Push code to GitHub.
2. In Render, create a new Blueprint and select this repo.
3. Render will create:
- `rag-chatbot-backend` (FastAPI)
- `rag-chatbot-frontend` (Streamlit)
4. Set secrets in Render:
- Backend: `OPENAI_API_KEY`
- Frontend: `API_URL` = your backend public URL (example: `https://rag-chatbot-backend.onrender.com`)
5. Deploy both services.

Important for Render:
- `APP_DATA_DIR` is set to `/var/data` with a persistent disk.
- `ENABLE_ADMIN_UI=false` and `ALLOW_ADMIN_INGESTION_API=false` by default.
- If you need first-time indexing on Render, temporarily set `ALLOW_ADMIN_INGESTION_API=true`, upload/index once, then set it back to `false`.

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

## Optional: Auto Index On Startup (Admin One-Time)

Set this in `rag_chatbot/.env`:
```env
DEFAULT_BOOK_PDF_PATH=C:\path\to\book.pdf
```
On backend startup, if no index exists, the PDF is indexed automatically.

## API Endpoints

- `POST /admin/upload?force=false` - Upload and start indexing (disabled by default unless `ALLOW_ADMIN_INGESTION_API=true`).
- `POST /admin/index-local` - Index local file path (disabled by default unless `ALLOW_ADMIN_INGESTION_API=true`).
- `GET /admin/status/{job_id}` - Ingestion job status (disabled by default unless `ALLOW_ADMIN_INGESTION_API=true`).
- `POST /chat` - Ask question.
- `GET /health` - Health check and index readiness.

## Performance Notes for 1000+ Page Books

- Embeddings are batched (`EMBEDDING_BATCH_SIZE`) to reduce API overhead.
- FAISS index is persisted to disk and loaded once on startup.
- PDF is parsed page-by-page.
- Metadata is stored in JSONL for scalable sequential reads.
