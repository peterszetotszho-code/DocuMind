"""Internationalization (i18n) for the web UI.

The user interface supports English and Traditional Chinese. All translatable
strings live here so the rest of the codebase stays language-neutral; code
identifiers, comments and documentation remain in English.
"""

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "zh-Hant")

LANGUAGE_LABELS = {
    "en": "English",
    "zh-Hant": "繁體中文",
}

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "title": "Your AI Assistant",
        "lang_label": "Language",
        "kb_header": "Knowledge Base",
        "uploader_label": "Upload documents (.txt, .md, .pdf)",
        "upload_success": "Upload successful.",
        "chat_placeholder": "Ask a question about your documents",
        "thinking": "Thinking...",
    },
    "zh-Hant": {
        "title": "Your AI Assistant",
        "lang_label": "語言",
        "kb_header": "知識庫",
        "uploader_label": "上傳文件（.txt、.md、.pdf）",
        "upload_success": "上傳成功。",
        "chat_placeholder": "詢問關於文件的問題",
        "thinking": "思考中…",
    },
}


def translate(language: str, key: str) -> str:
    """Return the translated string for ``key`` in ``language``.

    Falls back to English when the language or key is missing.
    """
    table = _TRANSLATIONS.get(language) or _TRANSLATIONS[DEFAULT_LANGUAGE]
    return table.get(key, _TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))
