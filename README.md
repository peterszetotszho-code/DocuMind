# RAG Dialogue

A retrieval-augmented generation (RAG) knowledge-base assistant built with
LangChain. Upload documents, index them into a local vector store, and chat
with an LLM that answers using your documents as context.

## Features

- Upload `.txt`, `.md`, and `.pdf` documents through a Streamlit UI.
- Incremental indexing: files are hashed (MD5) so unchanged uploads are skipped.
- Offline flow: load documents, split into chunks, embed, and store in Chroma.
- Online flow: retrieve the most relevant chunks for each question.
- Multi-turn chat with conversation history.

## Tech stack

| Layer        | Tool                                        |
| ------------ | ------------------------------------------- |
| LLM          | DeepSeek (`deepseek-chat`) via OpenAI API   |
| Embeddings   | Ollama (`nomic-embed-text`), local          |
| Vector store | Chroma, persisted locally                   |
| Framework    | LangChain                                   |
| UI           | Streamlit                                   |

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
ollama pull nomic-embed-text
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

1. Use the sidebar to upload one or more documents.
2. Click **Update knowledge base** to index new or changed files.
3. Ask questions in the chat box. Answers are generated from the retrieved
   document chunks.

## Project structure

```
app.py                          Streamlit entry point
rag_dialogue/
    config.py                   Environment-driven settings
    llm.py                      DeepSeek chat model factory
    embeddings.py               Ollama embedding factory
    md5_util.py                 File hashing for deduplication
    document_loaders.py         txt / md / pdf loaders
    text_splitter.py            Document chunking
    vector_store.py             Chroma store and retrieval
    knowledge_base.py           Incremental offline indexing
    prompts.py                  RAG prompt templates
    history.py                  In-memory conversation history
    rag_service.py              Retrieval + generation orchestration
tests/                          Unit tests
```

## Tests

```bash
python -m pytest
```

## Notes

- The embedding model runs locally through Ollama and does not require an API
  key. The DeepSeek key is only used for answer generation.
- When a file changes, its new chunks are appended to the vector store. For
  production use, replace this with a per-source delete-and-reindex step.
