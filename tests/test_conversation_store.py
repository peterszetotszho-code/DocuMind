from rag_dialogue import conversation_store


def test_new_conversation_structure():
    conversation = conversation_store.new_conversation()
    assert isinstance(conversation["id"], str)
    assert conversation["title"]
    assert conversation["messages"] == []


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    path = tmp_path / "conversations.json"
    monkeypatch.setattr(conversation_store, "conversations_path", lambda: path)

    conversations = [
        {
            "id": "1",
            "title": "a",
            "messages": [{"role": "user", "content": "hi"}],
        },
    ]
    conversation_store.save_conversations(conversations)
    assert conversation_store.load_conversations() == conversations


def test_load_returns_empty_when_file_missing(tmp_path, monkeypatch):
    path = tmp_path / "missing.json"
    monkeypatch.setattr(conversation_store, "conversations_path", lambda: path)
    assert conversation_store.load_conversations() == []
