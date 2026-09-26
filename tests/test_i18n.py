from rag_dialogue.i18n import SUPPORTED_LANGUAGES, translate


def test_translate_english():
    assert translate("en", "title") == "RAG Knowledge Base Assistant"


def test_translate_traditional_chinese():
    text = translate("zh-Hant", "title")
    assert text
    assert text != "RAG Knowledge Base Assistant"


def test_translate_formats_placeholders():
    assert translate("en", "upload_success", n=3) == "Uploaded and indexed 3 file(s)."


def test_translate_falls_back_to_english_for_unknown_language():
    assert translate("fr", "title") == "RAG Knowledge Base Assistant"


def test_translate_all_supported_languages_resolve():
    for language in SUPPORTED_LANGUAGES:
        assert translate(language, "chat_placeholder")
