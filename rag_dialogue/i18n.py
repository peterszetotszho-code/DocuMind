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
        "username": "Username",
        "password": "Password",
        "username_placeholder": "Enter your username",
        "password_placeholder": "Enter your password",
        "login": "Login",
        "login_error": "Invalid username or password.",
        "logout": "Log out",
        "logged_in_as": "Logged in as",
        "role_admin": "Admin",
        "role_user": "User",
        "kb_header": "Knowledge Base",
        "uploader_label": "Upload documents (.txt, .md, .pdf)",
        "upload_success": "Upload successful.",
        "upload_duplicate": "Already-uploaded files were skipped.",
        "delete_file": "Delete file",
        "select_file": "Select a file to delete",
        "delete": "Delete",
        "delete_success": "File deleted.",
        "no_files": "No files yet.",
        "sources": "Sources",
        "chat_placeholder": "Ask a question about your documents",
        "thinking": "Thinking...",
    },
    "zh-Hant": {
        "title": "Your AI Assistant",
        "lang_label": "語言",
        "username": "帳號",
        "password": "密碼",
        "username_placeholder": "請輸入帳號",
        "password_placeholder": "請輸入密碼",
        "login": "登入",
        "login_error": "帳號或密碼錯誤。",
        "logout": "登出",
        "logged_in_as": "已登入",
        "role_admin": "管理員",
        "role_user": "用戶",
        "kb_header": "知識庫",
        "uploader_label": "上傳文件（.txt、.md、.pdf）",
        "upload_success": "上傳成功。",
        "upload_duplicate": "已上傳過的文件已跳過。",
        "delete_file": "刪除文件",
        "select_file": "選擇要刪除的文件",
        "delete": "刪除",
        "delete_success": "文件已刪除。",
        "no_files": "尚無文件。",
        "sources": "參考來源",
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
