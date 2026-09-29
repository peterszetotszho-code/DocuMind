"""Streamlit entry point for the RAG knowledge-base assistant."""

import hashlib

import streamlit as st

from langchain_core.chat_history import InMemoryChatMessageHistory

from rag_dialogue.agent import AgentCallLogger, stream_agent
from rag_dialogue.auth import authenticate
from rag_dialogue.config import settings
from rag_dialogue.conversation_store import (
    load_conversations,
    new_conversation,
    save_conversations,
)
from rag_dialogue.i18n import LANGUAGE_LABELS, SUPPORTED_LANGUAGES, translate
from rag_dialogue.knowledge_base import (
    delete_document,
    list_uploaded_files,
    update_knowledge_base,
)
from rag_dialogue.rag_service import RAGService
from rag_dialogue.vector_store import get_vector_store

# Pre-warm the Chroma client in the main thread. LangGraph runs agent tools in
# worker threads where Chroma's client lifecycle races, so creating the client
# up front avoids that race.
get_vector_store()

st.set_page_config(
    page_title="Your AI Assistant",
    page_icon="📚",
    layout="wide",
)

st.markdown(
    """
    <style>
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
        border: 1px solid #1F2A44;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        background: #131C31;
    }
    /* Colored border on the login input fields (always visible). */
    [data-testid="stTextInput"] div:has(> input) {
        border: 1px solid #0EA5B7;
        border-radius: 8px;
    }
    /* Hide the uploaded file name chips; only the success message shows. */
    [data-testid="stFileChip"] {
        display: none;
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


def _history_from_messages(messages: list[dict]) -> InMemoryChatMessageHistory:
    """Rebuild a chat history from serialized messages."""
    history = InMemoryChatMessageHistory()
    for message in messages:
        if message["role"] == "user":
            history.add_user_message(message["content"])
        else:
            history.add_ai_message(message["content"])
    return history


def _messages_from_history(history: InMemoryChatMessageHistory) -> list[dict]:
    """Serialize a chat history into JSON-friendly messages."""
    return [
        {
            "role": "user" if message.type == "human" else "assistant",
            "content": message.content,
        }
        for message in history.messages
    ]


def _current_conversation() -> dict:
    return next(
        conversation
        for conversation in st.session_state.conversations
        if conversation["id"] == st.session_state.current_id
    )


def _persist_current_conversation() -> None:
    """Save the current conversation (messages + title) to disk."""
    conversation = _current_conversation()
    conversation["messages"] = _messages_from_history(st.session_state.chat_history)
    if conversation["title"] == "新對話" and st.session_state.chat_history.messages:
        conversation["title"] = st.session_state.chat_history.messages[0].content[:20]
    save_conversations(st.session_state.username, st.session_state.conversations)


def _load_user_conversations(username: str) -> None:
    """Load a user's conversations into the session, creating one if empty."""
    conversations = load_conversations(username)
    if not conversations:
        conversations = [new_conversation()]
    st.session_state.conversations = conversations
    st.session_state.current_id = conversations[-1]["id"]
    st.session_state.chat_history = _history_from_messages(conversations[-1]["messages"])


# Session state initialization.
if "lang" not in st.session_state:
    st.session_state.lang = "zh-Hant"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "current_id" not in st.session_state:
    st.session_state.current_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = InMemoryChatMessageHistory()
if "upload_snapshot" not in st.session_state:
    st.session_state.upload_snapshot = ()


def logout() -> None:
    """Clear the session and return to the login screen."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.conversations = []
    st.session_state.current_id = None
    st.session_state.chat_history = InMemoryChatMessageHistory()
    st.session_state.upload_snapshot = ()


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

        # Conversation management: start a new chat or switch to an old one.
        if st.button("➕ " + t("new_chat")):
            conversation = new_conversation()
            st.session_state.conversations.append(conversation)
            st.session_state.current_id = conversation["id"]
            st.session_state.chat_history = InMemoryChatMessageHistory()
            save_conversations(st.session_state.username, st.session_state.conversations)
            st.rerun()

        titles = [conversation["title"] for conversation in st.session_state.conversations]
        if titles:
            current_title = _current_conversation()["title"]
            if current_title not in titles:
                current_title = titles[-1]
            chosen = st.selectbox(t("history"), titles, index=titles.index(current_title))
            chosen_conversation = st.session_state.conversations[titles.index(chosen)]
            if chosen_conversation["id"] != st.session_state.current_id:
                st.session_state.current_id = chosen_conversation["id"]
                st.session_state.chat_history = _history_from_messages(
                    chosen_conversation["messages"]
                )
                st.rerun()

            if st.button(t("delete_chat")):
                st.session_state.conversations = [
                    conversation
                    for conversation in st.session_state.conversations
                    if conversation["id"] != chosen_conversation["id"]
                ]
                if st.session_state.conversations:
                    st.session_state.current_id = st.session_state.conversations[-1]["id"]
                    st.session_state.chat_history = _history_from_messages(
                        st.session_state.conversations[-1]["messages"]
                    )
                else:
                    conversation = new_conversation()
                    st.session_state.conversations = [conversation]
                    st.session_state.current_id = conversation["id"]
                    st.session_state.chat_history = InMemoryChatMessageHistory()
                save_conversations(st.session_state.username, st.session_state.conversations)
                st.rerun()

        # Only administrators may upload documents into the knowledge base.
        if st.session_state.role == "admin":
            st.header(t("kb_header"))
            uploaded_files = st.file_uploader(
                t("uploader_label"),
                type=["txt", "md", "pdf"],
                accept_multiple_files=True,
                key="file_uploader",
            )
            if uploaded_files:
                settings.upload_dir.mkdir(parents=True, exist_ok=True)
                entries = tuple(sorted(
                    (uploaded.name, hashlib.md5(uploaded.getvalue()).hexdigest())
                    for uploaded in uploaded_files
                ))

                is_new_upload = entries != st.session_state.upload_snapshot

                if is_new_upload:
                    for uploaded in uploaded_files:
                        (settings.upload_dir / uploaded.name).write_bytes(uploaded.getvalue())
                    indexed = update_knowledge_base()
                    if indexed:
                        st.success(t("upload_success"))
                    else:
                        st.info(t("upload_duplicate"))

                st.session_state.upload_snapshot = entries

            # Delete a document from the knowledge base.
            st.subheader(t("delete_file"))
            files = list_uploaded_files()
            if files:
                selected = st.selectbox(t("select_file"), [path.name for path in files])
                if st.button(t("delete")):
                    delete_document(selected)
                    st.success(t("delete_success"))
                    st.rerun()
            else:
                st.caption(t("no_files"))

        if st.button(t("logout")):
            logout()
            st.rerun()

        st.checkbox(t("agent_mode"), value=True, key="use_agent")


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
            _load_user_conversations(user["username"])
            st.rerun()
        else:
            st.error(t("login_error"))
    st.stop()


# Chat interface (available to all authenticated users).
for message in st.session_state.chat_history.messages:
    with st.chat_message("user" if message.type == "human" else "assistant"):
        st.markdown(message.content)

service = RAGService()

if prompt := st.chat_input(t("chat_placeholder")):
    st.session_state.chat_history.add_user_message(prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    history = st.session_state.chat_history.messages[:-1]
    language = (
        "繁體中文（Traditional Chinese），不要使用簡體字"
        if st.session_state.lang == "zh-Hant"
        else "the language of the question"
    )

    with st.chat_message("assistant"):
        with st.spinner(t("thinking")):
            if st.session_state.get("use_agent", False):
                logger = AgentCallLogger()
                answer = st.write_stream(stream_agent(prompt, logger, language, history))
                if logger.steps:
                    with st.expander(t("agent_steps")):
                        for step in logger.steps:
                            st.write(step)
            else:
                answer = st.write_stream(service.stream(prompt, history=history, language=language))
                sources = service.sources(prompt)
                if sources:
                    st.caption(f"{t('sources')}: " + ", ".join(sources))

    st.session_state.chat_history.add_ai_message(answer)
    _persist_current_conversation()
