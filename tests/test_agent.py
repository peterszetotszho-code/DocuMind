from rag_dialogue.agent import search_knowledge_base


def test_search_tool_has_name_and_description():
    assert search_knowledge_base.name == "search_knowledge_base"
    assert "search" in search_knowledge_base.description.lower()
