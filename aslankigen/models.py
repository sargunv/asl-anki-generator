from posixpath import basename, splitext

from pydantic import BaseModel


class WordEntry(BaseModel):
    """A word entry with an explicit HandSpeak path and optional hint.

    Example: {"word": "how are you", "path": "/word/h/how/how-you.mp4"}
    Example: {"word": "your name what", "path": "/lang/n/name/you-name-what.mp4"}
    """

    word: str
    path: str
    hint: str | None = None

    @property
    def resolved_filename(self) -> str:
        """The local filename (without extension), derived from the path basename."""
        return splitext(basename(self.path))[0]

    @property
    def resolved_url(self) -> str:
        """The full HandSpeak URL."""
        return f"https://www.handspeak.com{self.path}"

    @property
    def display_name(self) -> str:
        """The text to show on the card front."""
        name = self.word[0].upper() + self.word[1:]
        if self.hint:
            return f"{name} ({self.hint})"
        return name


def resolve_word(entry: str | WordEntry) -> WordEntry:
    """Normalize a word list entry to a WordEntry."""
    if isinstance(entry, str):
        from .util import get_handspeak_path

        return WordEntry(word=entry, path=get_handspeak_path(entry))
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
