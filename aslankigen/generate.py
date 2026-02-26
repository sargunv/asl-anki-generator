import genanki

from .models import WordsConfig
from .util import download_sign_video


def generate_note(word: str) -> genanki.Note:
    return genanki.Note(
        model=genanki.BASIC_MODEL,
        fields=[word[0].upper() + word[1:], f"[sound:{word}.mp4]"],
    )


def generate_deck(
    config: WordsConfig,
) -> tuple[genanki.Deck, list[str], int]:
    """
    Returns a generated deck, the list of video file paths, and the failure count.
    """
    my_deck = genanki.Deck(1725443770, config.name)

    video_files: list[str] = []
    failures = 0

    for word in config.words:
        video_file = download_sign_video(word)
        if not video_file:
            failures += 1
            continue

        my_deck.add_note(generate_note(word))
        video_files.append(video_file)

    return (my_deck, video_files, failures)
