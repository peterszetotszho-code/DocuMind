"""Streamlit entry point for the RAG knowledge-base assistant."""

import streamlit as st

from rag_dialogue.config import settings
from rag_dialogue.knowledge_base import update_knowledge_base
from rag_dialogue.rag_service import RAGService

st.set_page_config(
    page_title="RAG Knowledge Base Assistant",
    page_icon="📚",
    layout="wide",
)

st.title("RAG Knowledge Base Assistant")

# Sidebar: upload documents and refresh the knowledge base.
with st.sidebar:
    st.header("Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload documents (.txt, .md, .pdf)",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        for uploaded in uploaded_files:
            target = settings.upload_dir / uploaded.name
            target.write_bytes(uploaded.getvalue())
        st.success(
            f"Received {len(uploaded_files)} file(s). Click below to index them."
        )

    if st.button("Update knowledge base"):
        with st.spinner("Indexing documents..."):
            processed = update_knowledge_base()
        if processed:
            st.success("Indexed: " + ", ".join(processed))
        else:
            st.info("No new or changed files to index.")

# Main area: chat interface with persisted history.
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

service = RAGService()

if prompt := st.chat_input("Ask a question about your documents"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        ("human" if message["role"] == "user" else "ai", message["content"])
        for message in st.session_state.messages[:-1]
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = service.answer(prompt, history=history)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
