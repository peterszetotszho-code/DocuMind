import pytest

from rag_dialogue.document_loaders import load_document


def test_load_txt(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("line one\nline two", encoding="utf-8")
    documents = load_document(path)
    assert len(documents) == 1
    assert documents[0].page_content == "line one\nline two"
    assert documents[0].metadata["source"] == str(path)


def test_load_markdown(tmp_path):
    path = tmp_path / "notes.md"
    path.write_text("# Title\nbody", encoding="utf-8")
    documents = load_document(path)
    assert documents[0].page_content == "# Title\nbody"


def test_load_unsupported_extension_raises(tmp_path):
    path = tmp_path / "image.png"
    path.write_bytes(b"\x89PNG")
    with pytest.raises(ValueError):
        load_document(path)
