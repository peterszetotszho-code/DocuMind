"""Document loaders for text, Markdown and PDF files."""

from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader

SUPPORTED_SUFFIXES = {".txt", ".md", ".pdf"}


def load_document(path: str | Path) -> list[Document]:
    """Load a single file into a list of LangChain documents."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8")
        return [Document(page_content=text, metadata={"source": str(path)})]
    if suffix == ".pdf":
        return _load_pdf(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _load_pdf(path: Path) -> list[Document]:
    """Extract text page by page from a PDF file."""
    reader = PdfReader(str(path))
    documents: list[Document] = []
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            documents.append(
                Document(page_content=text, metadata={"source": str(path), "page": index})
            )
    return documents
