"""Generate an Anki ASL deck from words.json."""

import json
import logging

import genanki

from .generate import generate_decks
from .models import WordsConfig

WORD_LIST = "words.json"


def main() -> None:
    with open(WORD_LIST) as f:
        config = WordsConfig.model_validate(json.load(f))

    decks, video_files, failures = generate_decks(config)

    my_package = genanki.Package(decks)
    my_package.media_files = video_files
    my_package.write_to_file(config.export_filename)

    total_cards = sum(len(deck.notes) for deck in decks)
    logging.info(f'Anki deck with {total_cards} cards across {len(decks)} sub-decks successfully exported to "{config.export_filename}"! {failures} failures were reported.')


if __name__ == "__main__":
    main()
