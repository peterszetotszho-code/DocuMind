"""Internationalization (i18n) for the web UI.

The user interface supports English and Traditional Chinese. All translatable
strings live here so the rest of the codebase stays language-neutral; code
identifiers, comments and documentation remain in English.
"""

from typing import Any

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "zh-Hant")

LANGUAGE_LABELS = {
    "en": "English",
    "zh-Hant": "繁體中文",
}

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "title": "RAG Knowledge Base Assistant",
        "lang_label": "Language",
        "kb_header": "Knowledge Base",
        "uploader_label": "Upload documents (.txt, .md, .pdf)",
        "upload_success": "Uploaded and indexed {n} file(s).",
        "upload_empty": "No new or changed files to index.",
        "chat_placeholder": "Ask a question about your documents",
        "thinking": "Thinking...",
    },
    "zh-Hant": {
        "title": "RAG 知識庫助理",
        "lang_label": "語言",
        "kb_header": "知識庫",
        "uploader_label": "上傳文件（.txt、.md、.pdf）",
        "upload_success": "已上傳並建立索引 {n} 個文件。",
        "upload_empty": "沒有新的或變更的文件需要索引。",
        "chat_placeholder": "詢問關於文件的問題",
        "thinking": "思考中…",
    },
}


def translate(language: str, key: str, **kwargs: Any) -> str:
    """Return the translated string for ``key`` in ``language``.

    Falls back to English when the language or key is missing, and formats any
    ``{placeholder}`` values from ``kwargs``.
    """
    table = _TRANSLATIONS.get(language) or _TRANSLATIONS[DEFAULT_LANGUAGE]
    template = table.get(key, _TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))
    return template.format(**kwargs) if kwargs else template
