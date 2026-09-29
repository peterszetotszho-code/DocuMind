# DocuMind

A retrieval-augmented generation (RAG) knowledge-base assistant built with
LangChain and LangGraph. Upload documents, index them into a local vector
store, and ask questions — answered using your documents as context. Includes
a ReAct agent, per-user conversation history, and role-based access.

## Features

- Upload `.txt`, `.md`, and `.pdf` documents and index them automatically.
- RAG Q&A with source citations and token-by-token streaming.
- ReAct agent mode with search and file-listing tools (toggle in the sidebar).
- Role-based access: admins upload and delete documents, users only ask.
- Per-user conversation history, persisted to JSON, with new / switch / delete.
- Multi-turn context, bilingual UI (English / Traditional Chinese).
- Incremental indexing with MD5 deduplication.

## Tech stack

| Layer        | Tool                                          |
| ------------ | --------------------------------------------- |
| LLM          | DeepSeek (`deepseek-chat`) via OpenAI API     |
| Embeddings   | Ollama (`bge-m3`, multilingual), local        |
| Vector store | Chroma, persisted locally                     |
| Framework    | LangChain (LCEL) + LangGraph (ReAct agent)    |
| UI           | Streamlit                                     |

## Setup

### 1. Install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Start Ollama and pull the embedding model

```bash
ollama pull bge-m3
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your `DEEPSEEK_API_KEY`.

### 4. Run the app

```bash
streamlit run app.py
```

## Usage

1. Log in (default accounts: `admin / 123456` or `user / 666666`).
2. As an admin, upload documents to index them.
3. Ask questions in the chat box; switch on Agent mode at the bottom of the
   sidebar for a tool-using ReAct agent.

## Project structure

```
app.py                          Streamlit entry point
rag_dialogue/
    agent.py                    ReAct agent (search + list-files tools)
    auth.py                     Login and role-based access
    config.py                   Environment-driven settings
    conversation_store.py       Per-user conversation persistence (JSON)
    document_loaders.py         txt / md / pdf loaders
    embeddings.py               Ollama embedding factory
    i18n.py                     UI translations (English / Traditional Chinese)
    knowledge_base.py           Incremental indexing + document deletion
    llm.py                      DeepSeek chat model factory
    md5_util.py                 File hashing for deduplication
    prompts.py                  RAG prompt templates
    rag_service.py              LCEL retrieval + generation
    text_splitter.py            Document chunking
    vector_store.py             Chroma store, retriever, deletion
tests/                          Unit tests
```

## Tests

```bash
python -m pytest
```

## Notes

- The embedding model runs locally through Ollama and does not require an API
  key. The DeepSeek key is only used for answer generation.
- `bge-m3` is used for embeddings because it supports Chinese well.
- Authentication is demo-grade (salted SHA-256 hashes and hardcoded accounts);
  use a real authentication system for production.
