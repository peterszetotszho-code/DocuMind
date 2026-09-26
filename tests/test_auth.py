from rag_dialogue.auth import authenticate


def test_authenticate_admin():
    user = authenticate("admin", "123456")
    assert user is not None
    assert user["username"] == "admin"
    assert user["role"] == "admin"


def test_authenticate_user():
    user = authenticate("user", "666666")
    assert user is not None
    assert user["role"] == "user"


def test_authenticate_wrong_password():
    assert authenticate("admin", "wrong") is None


def test_authenticate_unknown_username():
    assert authenticate("nobody", "123456") is None
