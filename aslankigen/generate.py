import hashlib

import genanki

from .models import WordEntry, WordsConfig, resolve_word
from .util import download_sign_video


def _deck_id(name: str) -> int:
    """Generate a stable deck ID from a deck name."""
    hash_bytes = hashlib.sha256(name.encode()).digest()
    return int.from_bytes(hash_bytes[:4], "big")


def generate_note(entry: WordEntry, tags: list[str]) -> genanki.Note:
    filename = entry.resolved_filename
    return genanki.Note(
        model=genanki.BASIC_MODEL,
        fields=[entry.display_name, f"[sound:{filename}.mp4]"],
        tags=tags,
    )


def generate_decks(
    config: WordsConfig,
) -> tuple[list[genanki.Deck], list[str], int]:
    """
    Returns the generated decks, the list of video file paths, and the failure count.
    """
    decks: list[genanki.Deck] = []
    video_files: list[str] = []
    failures = 0

    for group in config.groups:
        deck_name = f"{config.name}::{group.name}"
        deck = genanki.Deck(_deck_id(deck_name), deck_name)

        for word_set in group.sets:
            for raw_entry in word_set.words:
                entry = resolve_word(raw_entry)
                video_file = download_sign_video(entry.resolved_filename, entry.resolved_url)
                if not video_file:
                    failures += 1
                    continue

                deck.add_note(generate_note(entry, word_set.tags))
                video_files.append(video_file)

        decks.append(deck)

    return (decks, video_files, failures)
