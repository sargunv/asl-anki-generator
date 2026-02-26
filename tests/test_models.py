import pytest
from pydantic import ValidationError

from aslankigen.models import WordEntry, _get_handspeak_path, resolve_word


# --- _get_handspeak_path ---


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("hello", "/word/h/hel/hello.mp4"),
        ("hi", "/word/h/hi/hi.mp4"),
        ("a", "/word/a/a-abc.mp4"),
        ("z", "/word/z/z-abc.mp4"),
    ],
)
def test_handspeak_path(word: str, expected: str):
    assert _get_handspeak_path(word) == expected


# --- resolve_word ---


@pytest.mark.parametrize(
    ("word", "expected_path", "expected_filename"),
    [
        ("hello", "/word/h/hel/hello.mp4", "hello"),
        ("a", "/word/a/a-abc.mp4", "a-abc"),
    ],
)
def test_resolve_word_from_string(word: str, expected_path: str, expected_filename: str):
    entry = resolve_word(word)
    assert entry.word == word
    assert entry.path == expected_path
    assert entry.resolved_filename == expected_filename
    assert entry.resolved_url == f"https://www.handspeak.com{expected_path}"
    assert entry.display_name == word.upper()


# --- WordEntry properties ---


@pytest.mark.parametrize(
    ("word", "path", "expected_filename", "expected_url"),
    [
        (
            "how are you",
            "/word/h/how/how-you.mp4",
            "how-you",
            "https://www.handspeak.com/word/h/how/how-you.mp4",
        ),
        (
            "your name what",
            "/lang/n/name/you-name-what.mp4",
            "you-name-what",
            "https://www.handspeak.com/lang/n/name/you-name-what.mp4",
        ),
    ],
)
def test_word_entry_explicit_path(word: str, path: str, expected_filename: str, expected_url: str):
    entry = WordEntry(word=word, path=path)
    assert entry.resolved_filename == expected_filename
    assert entry.resolved_url == expected_url
    assert entry.display_name == word.upper()


def test_word_entry_with_hint():
    entry = WordEntry(word="how", path="/word/h/how/how.mp4", hint="as in 'how do you know'")
    assert entry.display_name == "HOW (as in 'how do you know')"


# --- WordEntry validation ---


@pytest.mark.parametrize("word", ["", "   "])
def test_empty_word_raises(word: str):
    with pytest.raises(ValidationError):
        WordEntry(word=word, path="/word/a/a.mp4")


@pytest.mark.parametrize("path", ["no-leading-slash.mp4", "/word/h/hel/hello.txt"])
def test_invalid_path_raises(path: str):
    with pytest.raises(ValidationError):
        WordEntry(word="hello", path=path)
