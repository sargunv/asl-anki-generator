from pathlib import Path
from unittest.mock import patch

from aslankigen.generate import _deck_id, generate_decks, generate_note
from aslankigen.models import Group, WordEntry, WordSet, WordsConfig
from aslankigen.util import DownloadStatus


# --- _deck_id ---


def test_deck_id_stable():
    """The same name always produces the same ID."""
    assert _deck_id("foo") == _deck_id("foo")


def test_deck_id_different_inputs():
    """Different names produce different IDs."""
    assert _deck_id("foo") != _deck_id("bar")


def test_deck_id_in_valid_range():
    """The result is in genanki's valid range [1<<30, 1<<31)."""
    for name in ("foo", "bar", "ASL::Basics", "", "z" * 1000):
        result = _deck_id(name)
        assert 1 << 30 <= result < 1 << 31, f"_deck_id({name!r}) = {result} out of range"


# --- generate_note ---


def test_generate_note():
    """generate_note produces a note with the correct fields and tags."""
    entry = WordEntry(word="hello", path="/word/h/hel/hello.mp4")
    note = generate_note(entry, ["basics", "greetings"])

    assert note.fields == ["HELLO", "[sound:hello.mp4]"]
    assert note.tags == ["basics", "greetings"]


# --- generate_decks integration ---


def _make_config(*words: str) -> WordsConfig:
    return WordsConfig(
        name="Test",
        export_filename="test.apkg",
        groups=[Group(name="Basics", sets=[WordSet(tags=["basics"], words=list(words))])],
    )


@patch("aslankigen.generate.download_sign_video")
def test_generate_decks_basic(mock_download):
    """Successful downloads produce decks with notes."""
    mock_download.return_value = (Path("/tmp/hello.mp4"), DownloadStatus.DOWNLOADED)

    decks, video_files, failures = generate_decks(_make_config("hello"))

    assert len(decks) == 1
    assert len(decks[0].notes) == 1
    assert len(video_files) == 1
    assert failures == 0


@patch("aslankigen.generate.download_sign_video")
def test_generate_decks_with_failure(mock_download):
    """Failed downloads produce no notes and increment the failure count."""
    mock_download.return_value = (None, DownloadStatus.FAILED)

    decks, video_files, failures = generate_decks(_make_config("hello"))

    assert len(decks) == 1
    assert len(decks[0].notes) == 0
    assert video_files == []
    assert failures == 1
