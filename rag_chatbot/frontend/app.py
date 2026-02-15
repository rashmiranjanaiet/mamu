import os
import time

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ENABLE_ADMIN_UI = os.getenv("ENABLE_ADMIN_UI", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

st.set_page_config(page_title="Book RAG Chatbot", page_icon=":book:", layout="wide")
st.title("Book RAG Chatbot")
st.caption("Answers are generated only from the uploaded PDF book.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Admin")
    if ENABLE_ADMIN_UI:
        local_pdf_path = st.text_input(
            "Local PDF path",
            value="",
            placeholder=r"c:\Users\It Computer Point\Downloads\book.pdf",
        )
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
        force_reindex = st.checkbox("Replace existing index", value=False)
        if st.button("Index Local Path", disabled=not local_pdf_path.strip()):
            body = {"pdf_path": local_pdf_path.strip(), "force": force_reindex}
            res = requests.post(f"{API_URL}/admin/index-local", json=body, timeout=60)
            if res.status_code >= 400:
                st.error(res.json().get("detail", "Local indexing failed"))
            else:
                payload = res.json()
                job_id = payload["job_id"]
                st.info(f"Job {job_id} started. Waiting for completion...")
                while True:
                    status_res = requests.get(f"{API_URL}/admin/status/{job_id}", timeout=30)
                    status = status_res.json()
                    if status["status"] in {"completed", "failed"}:
                        if status["status"] == "completed":
                            st.success(status["detail"])
                        else:
                            st.error(status["detail"])
                        break
                    time.sleep(2)
        if st.button("Upload and Index", disabled=pdf_file is None):
            files = {"file": (pdf_file.name, pdf_file.getvalue(), "application/pdf")}
            params = {"force": str(force_reindex).lower()}
            res = requests.post(f"{API_URL}/admin/upload", files=files, params=params, timeout=120)
            if res.status_code >= 400:
                st.error(res.json().get("detail", "Upload failed"))
            else:
                payload = res.json()
                job_id = payload["job_id"]
                st.info(f"Job {job_id} started. Waiting for completion...")
                while True:
                    status_res = requests.get(f"{API_URL}/admin/status/{job_id}", timeout=30)
                    status = status_res.json()
                    if status["status"] in {"completed", "failed"}:
                        if status["status"] == "completed":
                            st.success(status["detail"])
                        else:
                            st.error(status["detail"])
                        break
                    time.sleep(2)
    else:
        st.info("Upload is disabled for web users. Admin must index the book locally.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("meta"):
            st.caption(msg["meta"])

question = st.chat_input("Ask a question from the uploaded book")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the book..."):
            res = requests.post(f"{API_URL}/chat", json={"question": question}, timeout=120)
        if res.status_code >= 400:
            answer_text = res.json().get("detail", "Request failed")
            meta = ""
        else:
            payload = res.json()
            answer_text = payload["answer"]
            confidence = payload["confidence"]
            pages = sorted({str(item["page"]) for item in payload.get("sources", [])})
            pages_text = ", ".join(pages) if pages else "-"
            meta = f"Confidence: {confidence:.2f} | Source pages: {pages_text}"
        st.markdown(answer_text)
        if meta:
            st.caption(meta)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer_text, "meta": meta}
    )
