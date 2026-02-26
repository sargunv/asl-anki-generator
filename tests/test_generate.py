import pytest
from pydantic import ValidationError

from aslankigen.generate import DownloadCounts, _deck_id, generate_note
from aslankigen.models import WordEntry
from aslankigen.util import DownloadStatus


# --- _deck_id ---


def test_deck_id_stable():
    """The same name always produces the same ID."""
    assert _deck_id("foo") == _deck_id("foo")


def test_deck_id_different_inputs():
    """Different names produce different IDs."""
    assert _deck_id("foo") != _deck_id("bar")


def test_deck_id_in_valid_range():
    """The result is in range(1 << 30, (1 << 31)), i.e. [1073741824, 2147483647]."""
    for name in ("foo", "bar", "ASL::Basics", "", "z" * 1000):
        result = _deck_id(name)
        assert 1 << 30 <= result < 1 << 31, f"_deck_id({name!r}) = {result} out of range"


# --- generate_note ---


def test_generate_note():
    """generate_note produces a note with the correct fields and tags."""
    entry = WordEntry(word="hello", path="/word/h/hel/hello.mp4")
    tags = ["basics", "greetings"]

    note = generate_note(entry, tags)

    assert note.fields == ["HELLO", "[sound:hello.mp4]"]
    assert note.tags == ["basics", "greetings"]


# --- DownloadCounts ---


def test_download_counts_increment():
    """increment correctly bumps each status counter."""
    counts = DownloadCounts()

    counts.increment(DownloadStatus.CACHED)
    counts.increment(DownloadStatus.CACHED)
    counts.increment(DownloadStatus.DOWNLOADED)
    counts.increment(DownloadStatus.FAILED)

    assert counts.cached == 2
    assert counts.downloaded == 1
    assert counts.failed == 1


def test_download_counts_as_dict():
    """as_dict returns the expected dictionary."""
    counts = DownloadCounts(cached=3, downloaded=5, failed=1)

    assert counts.as_dict() == {"cached": 3, "downloaded": 5, "failed": 1}


# --- WordEntry validator edge cases ---


def test_empty_word_raises():
    """WordEntry rejects empty and whitespace-only words."""
    with pytest.raises(ValidationError):
        WordEntry(word="", path="/word/a/a.mp4")

    with pytest.raises(ValidationError):
        WordEntry(word="   ", path="/word/a/a.mp4")
