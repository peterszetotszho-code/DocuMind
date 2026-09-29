from rag_dialogue.prompts import RAG_PROMPT, SYSTEM_TEMPLATE


def test_system_template_encourages_inference():
    lowered = SYSTEM_TEMPLATE.lower()
    assert "infer" in lowered


def test_system_template_natural_dont_know_tone():
    lowered = SYSTEM_TEMPLATE.lower()
    assert "naturally" in lowered
    assert "unrelated" in lowered


def test_system_template_distinguishes_facts_from_examples():
    lowered = SYSTEM_TEMPLATE.lower()
    assert "example" in lowered
    assert "over-infer" in lowered


def test_system_template_handles_recommendations():
    lowered = SYSTEM_TEMPLATE.lower()
    assert "recommendation" in lowered
    assert "advice" in lowered


def test_rag_prompt_declares_context_question_and_history():
    assert "context" in RAG_PROMPT.input_variables
    assert "question" in RAG_PROMPT.input_variables
    assert "history" in RAG_PROMPT.input_variables
