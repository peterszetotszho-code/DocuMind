from rag_dialogue.history import ChatHistory


def test_add_and_iterate():
    history = ChatHistory(max_turns=4)
    history.add_user("hi")
    history.add_assistant("hello")
    assert len(history) == 2
    assert history.turns == [("human", "hi"), ("ai", "hello")]


def test_trims_to_max_turns():
    history = ChatHistory(max_turns=2)
    for i in range(5):
        history.add_user(f"q{i}")
    assert len(history) == 2
    assert history.turns[0][1] == "q3"
    assert history.turns[1][1] == "q4"
