from rag_dialogue.i18n import SUPPORTED_LANGUAGES, translate


def test_translate_english():
    assert translate("en", "title") == "RAG Knowledge Base Assistant"


def test_translate_traditional_chinese():
    text = translate("zh-Hant", "title")
    assert text
    assert text != "RAG Knowledge Base Assistant"


def test_translate_upload_success_english():
    assert translate("en", "upload_success") == "Upload successful."


def test_translate_upload_success_traditional_chinese():
    assert translate("zh-Hant", "upload_success") == "上傳成功。"


def test_translate_falls_back_to_english_for_unknown_language():
    assert translate("fr", "title") == "RAG Knowledge Base Assistant"


def test_translate_all_supported_languages_resolve():
    for language in SUPPORTED_LANGUAGES:
        assert translate(language, "chat_placeholder")
