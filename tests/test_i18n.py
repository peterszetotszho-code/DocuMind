from rag_dialogue.i18n import SUPPORTED_LANGUAGES, translate


def test_translate_english():
    assert translate("en", "title") == "Your AI Assistant"


def test_translate_traditional_chinese():
    # The title is intentionally the same in every language.
    assert translate("zh-Hant", "title") == "Your AI Assistant"


def test_translate_upload_success_english():
    assert translate("en", "upload_success") == "Upload successful."


def test_translate_upload_success_traditional_chinese():
    assert translate("zh-Hant", "upload_success") == "上傳成功。"


def test_translate_falls_back_to_english_for_unknown_language():
    assert translate("fr", "title") == "Your AI Assistant"


def test_translate_all_supported_languages_resolve():
    for language in SUPPORTED_LANGUAGES:
        assert translate(language, "chat_placeholder")


def test_translate_login_keys_resolve():
    for language in SUPPORTED_LANGUAGES:
        assert translate(language, "login")
        assert translate(language, "logout")
        assert translate(language, "username")
        assert translate(language, "password")
