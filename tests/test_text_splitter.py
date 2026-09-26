from langchain_core.documents import Document

from rag_dialogue.text_splitter import SEPARATORS, split_documents


def test_split_long_document_into_chunks():
    text = " ".join(f"sentence-{i}" for i in range(500))
    document = Document(page_content=text)
    chunks = split_documents([document])
    assert len(chunks) > 1
    assert all(chunk.page_content for chunk in chunks)


def test_separators_include_chinese_sentence_boundaries():
    for punctuation in ("。", "！", "？", "；", "，"):
        assert punctuation in SEPARATORS
