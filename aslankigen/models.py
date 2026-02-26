from pathlib import PurePosixPath

from pydantic import BaseModel, field_validator


def _get_handspeak_path(word: str) -> str:
    """Build the HandSpeak URL path for a standard dictionary word.

    This handles the two known URL patterns:
    - Single letters: /word/{letter}/{letter}-abc.mp4
    - Regular words: /word/{first_char}/{first_3_chars}/{word}.mp4
    """
    if len(word) == 1 and word.isalpha():
        return f"/word/{word}/{word}-abc.mp4"
    return f"/word/{word[:1]}/{word[:3]}/{word}.mp4"


class WordEntry(BaseModel):
    """A word entry with an explicit HandSpeak path and optional hint.

    Example: {"word": "how are you", "path": "/word/h/how/how-you.mp4"}
    Example: {"word": "your name what", "path": "/lang/n/name/you-name-what.mp4"}
    """

    word: str
    path: str
    hint: str | None = None

    @field_validator("word")
    @classmethod
    def word_must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("word must be a non-empty string")
        return v

    @field_validator("path")
    @classmethod
    def path_must_be_valid(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("path must be an absolute URL path starting with /")
        if not v.endswith(".mp4"):
            raise ValueError("path must end with .mp4")
        return v

    @property
    def resolved_filename(self) -> str:
        """The local filename (without extension), derived from the path basename."""
        return PurePosixPath(self.path).stem

    @property
    def resolved_url(self) -> str:
        """The full HandSpeak URL."""
        return f"https://www.handspeak.com{self.path}"

    @property
    def display_name(self) -> str:
        """The text to show on the card front, in ASL gloss convention (ALL CAPS)."""
        name = self.word.upper()
        if self.hint:
            return f"{name} ({self.hint})"
        return name


def resolve_word(entry: str | WordEntry) -> WordEntry:
    """Normalize a word list entry to a WordEntry."""
    if isinstance(entry, str):
        return WordEntry(word=entry, path=_get_handspeak_path(entry))
    return entry


class WordSet(BaseModel):
    tags: list[str]
    words: list[str | WordEntry]


class Group(BaseModel):
    name: str
    sets: list[WordSet]


class WordsConfig(BaseModel):
    name: str
    export_filename: str
    groups: list[Group]
