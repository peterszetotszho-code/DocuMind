from rag_dialogue.agent import (
    AgentCallLogger,
    list_knowledge_base_files,
    search_knowledge_base,
)


def test_search_tool_has_name_and_description():
    assert search_knowledge_base.name == "search_knowledge_base"
    assert "search" in search_knowledge_base.description.lower()


def test_list_files_tool_name():
    assert list_knowledge_base_files.name == "list_knowledge_base_files"


def test_agent_call_logger_records_steps():
    logger = AgentCallLogger()
    logger.on_tool_start({"name": "search_knowledge_base"}, "{}")
    logger.on_tool_end("some result")
    assert len(logger.steps) == 2
