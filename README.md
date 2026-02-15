# 🤖 ChartBot-AI – Book RAG Chatbot

ChartBot-AI is an AI chatbot that can answer questions from **1000+ books or PDFs** using Retrieval-Augmented Generation (RAG).
Built by **Rashmi Ranjan Behera** (CSE Student, Aryan Institute of Engineering & Technology, Bhubaneswar).

---

## 🚀 Features

* 📚 Train chatbot on books / PDFs
* 🧠 Uses RAG (vector search + LLM)
* 💬 ChatGPT-like interface
* ⚡ FastAPI backend + React frontend
* 🔍 Semantic search using embeddings
* 🆓 Can run locally for free
* 🌐 Deployable on Render / Vercel

---

## 🛠️ Tech Stack

**Frontend**

* React + TypeScript
* Vite
* Bootstrap / Tailwind (optional)

**Backend**

* Python FastAPI
* LangChain / Custom RAG pipeline
* OpenAI / Local LLM support
* FAISS / Chroma vector database

---

## 📂 Project Structure

```
chartbot-ai/
│
├── frontend/              # React chatbot UI
├── backend/               # FastAPI server
├── rag_chatbot/
│   ├── scripts/           # Book ingestion scripts
│   ├── backend/rag/       # Embedding & retrieval logic
│   └── config.py
├── data/                  # (ignored in git) books & indexes
├── .gitignore
├── package.json
└── README.md
```

---

## ⚙️ Installation (Local Setup)

### 1️⃣ Clone Repo

```bash
git clone https://github.com/rashmiranjanaiet/mamu.git
cd chartbot-ai
```

### 2️⃣ Backend Setup

```bash
cd rag_chatbot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

Run backend:

```bash
uvicorn backend.main:app --reload
```

---

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open 👉 [http://localhost:5173](http://localhost:5173)

---

## 📚 Add Books to Chatbot

Put your PDF in `rag_chatbot/data/` and run:

```bash
python scripts/ingest_book.py "your_book.pdf"
```

This will create vector index for chatbot search.

---

## 🌐 Deployment

**Backend:** Render / Railway / AWS
**Frontend:** Vercel / Netlify

Steps:

1. Push code to GitHub
2. Connect GitHub to Render/Vercel
3. Add environment variables
4. Deploy

---

## 💡 Future Plans

* Voice chatbot
* Multi-language support (English + Hindi + Odia + Korean)
* NGO medical knowledge chatbot
* E-learning integration for college hackathon project
* NASA Ingenuity-inspired robotics assistant AI

---

## 👨‍💻 Author

**Rashmi Ranjan Behera**
CSE Student – Aryan Institute of Engineering & Technology, Bhubaneswar
AI Robotics Developer | Animation Maker | E-commerce Entrepreneur

GitHub 👉 [https://github.com/rashmiranjanaiet](https://github.com/rashmiranjanaiet)

---

## ⭐ Support

If you like this project, give it a ⭐ on Git

