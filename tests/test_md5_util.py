import hashlib

from rag_dialogue.md5_util import get_file_md5


def test_get_file_md5_matches_hashlib(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_bytes(b"hello world")
    assert get_file_md5(path) == hashlib.md5(b"hello world").hexdigest()


def test_get_file_md5_empty_file(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_bytes(b"")
    assert get_file_md5(path) == hashlib.md5(b"").hexdigest()
