from rag_dialogue.prompts import SYSTEM_TEMPLATE, build_messages


def test_system_template_encourages_inference():
    lowered = SYSTEM_TEMPLATE.lower()
    assert "infer" in lowered
    assert "not available" in lowered


def test_system_template_distinguishes_facts_from_examples():
    lowered = SYSTEM_TEMPLATE.lower()
    assert "example" in lowered
    assert "over-infer" in lowered


def test_build_messages_injects_context_and_question():
    messages = build_messages(context="ctx text", question="what?")
    assert "ctx text" in messages[0].content
    assert messages[-1].content == "what?"


def test_build_messages_includes_history_turns():
    messages = build_messages(
        context="ctx",
        question="now?",
        history=[("human", "before?"), ("ai", "answer")],
    )
    role_names = [type(message).__name__ for message in messages]
    assert role_names.count("HumanMessage") == 2
    assert role_names.count("AIMessage") == 1
