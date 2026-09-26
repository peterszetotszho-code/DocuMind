"""Streamlit entry point for the RAG knowledge-base assistant."""

import hashlib

import streamlit as st

from rag_dialogue.config import settings
from rag_dialogue.i18n import LANGUAGE_LABELS, SUPPORTED_LANGUAGES, translate
from rag_dialogue.knowledge_base import update_knowledge_base
from rag_dialogue.rag_service import RAGService

st.set_page_config(
    page_title="RAG Knowledge Base Assistant",
    page_icon="📚",
    layout="wide",
)

st.markdown(
    """
    <style>
    h1 span[data-heading-text] {
        background: linear-gradient(90deg, #06B6D4, #6366F1, #A855F7);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        color: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def t(key: str) -> str:
    """Translate a UI string into the currently selected language."""
    return translate(st.session_state.lang, key)


# Language selection, persisted across reruns.
if "lang" not in st.session_state:
    st.session_state.lang = "en"

st.sidebar.selectbox(
    translate(st.session_state.lang, "lang_label"),
    options=list(SUPPORTED_LANGUAGES),
    format_func=lambda code: LANGUAGE_LABELS[code],
    key="lang",
)

st.title(t("title"))

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}
if "show_upload_success" not in st.session_state:
    st.session_state.show_upload_success = False
if "uploader_reset" not in st.session_state:
    st.session_state.uploader_reset = 0

# Sidebar: uploads are stored backend-side and indexed immediately. File names
# are never shown; only a generic "upload successful" confirmation is displayed.
with st.sidebar:
    st.header(t("kb_header"))
    uploaded_files = st.file_uploader(
        t("uploader_label"),
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
        key=f"file_uploader_{st.session_state.uploader_reset}",
    )
    if uploaded_files:
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        new_files = []
        for uploaded in uploaded_files:
            digest = hashlib.md5(uploaded.getvalue()).hexdigest()
            if st.session_state.processed_files.get(uploaded.name) != digest:
                st.session_state.processed_files[uploaded.name] = digest
                new_files.append(uploaded)
        for uploaded in new_files:
            (settings.upload_dir / uploaded.name).write_bytes(uploaded.getvalue())
        if new_files:
            update_knowledge_base()
        # Reset the uploader and confirm, so file names are not shown.
        st.session_state.show_upload_success = True
        st.session_state.uploader_reset += 1
        st.rerun()

    if st.session_state.show_upload_success:
        st.session_state.show_upload_success = False
        st.success(t("upload_success"))

# Main area: chat interface with persisted history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

service = RAGService()

if prompt := st.chat_input(t("chat_placeholder")):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        ("human" if message["role"] == "user" else "ai", message["content"])
        for message in st.session_state.messages[:-1]
    ]

    with st.chat_message("assistant"):
        with st.spinner(t("thinking")):
            answer = service.answer(prompt, history=history)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
