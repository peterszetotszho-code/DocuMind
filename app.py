"""Streamlit entry point for the RAG knowledge-base assistant."""

import hashlib

import streamlit as st

from rag_dialogue.auth import authenticate
from rag_dialogue.config import settings
from rag_dialogue.i18n import LANGUAGE_LABELS, SUPPORTED_LANGUAGES, translate
from rag_dialogue.knowledge_base import update_knowledge_base
from rag_dialogue.rag_service import RAGService

st.set_page_config(
    page_title="Your AI Assistant",
    page_icon="📚",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stApp"] {
        background-color: #EEF2FF;
    }
    h1 {
        text-align: center;
    }
    h1 span[data-heading-text] {
        background: linear-gradient(90deg, #06B6D4, #6366F1, #A855F7);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        color: transparent;
    }
    /* Compact, centered login card. */
    [data-testid="stForm"] {
        max-width: 400px;
        margin: 1rem auto;
        padding: 2rem;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        background: #FFFFFF;
    }
    /* Full-width login button. */
    [data-testid="stFormSubmitButton"] {
        width: 100%;
    }
    [data-testid="stFormSubmitButton"] button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def t(key: str) -> str:
    """Translate a UI string into the currently selected language."""
    return translate(st.session_state.lang, key)


# Session state initialization.
if "lang" not in st.session_state:
    st.session_state.lang = "zh-Hant"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}
if "show_upload_success" not in st.session_state:
    st.session_state.show_upload_success = False
if "uploader_reset" not in st.session_state:
    st.session_state.uploader_reset = 0


def logout() -> None:
    """Clear the session and return to the login screen."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.messages = []
    st.session_state.processed_files = {}


# Sidebar: logo, language, and (when logged in) role + upload + logout.
with st.sidebar:
    st.markdown(
        '<div style="text-align:center; font-size:3.2rem; line-height:1.1; '
        'padding:0.4rem 0 0.6rem 0;">📚</div>',
        unsafe_allow_html=True,
    )

    st.selectbox(
        t("lang_label"),
        options=list(SUPPORTED_LANGUAGES),
        format_func=lambda code: LANGUAGE_LABELS[code],
        key="lang",
    )

    if st.session_state.authenticated:
        st.caption(f"{t('logged_in_as')}: {t('role_' + st.session_state.role)}")

        # Only administrators may upload documents into the knowledge base.
        if st.session_state.role == "admin":
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

        if st.button(t("logout")):
            logout()
            st.rerun()


# Main area: the title is always shown.
st.title(t("title"))

if not st.session_state.authenticated:
    # Login form.
    with st.form("login_form"):
        username = st.text_input(t("username"), placeholder=t("username_placeholder"))
        password = st.text_input(t("password"), type="password", placeholder=t("password_placeholder"))
        submitted = st.form_submit_button(t("login"), use_container_width=True)
    if submitted:
        user = authenticate(username, password)
        if user is not None:
            st.session_state.authenticated = True
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            st.rerun()
        else:
            st.error(t("login_error"))
    st.stop()


# Chat interface (available to all authenticated users).
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
