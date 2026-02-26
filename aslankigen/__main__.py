"""Generate an Anki ASL deck from words.json."""

import json
import logging

import genanki

from .generate import generate_deck
from .models import WordsConfig

WORD_LIST = "words.json"


def main() -> None:
    with open(WORD_LIST) as f:
        config = WordsConfig.model_validate(json.load(f))

    my_deck, video_files, failures = generate_deck(config)

    my_package = genanki.Package(my_deck)
    my_package.media_files = video_files
    my_package.write_to_file(config.export_filename)

    logging.info(f'Anki deck with {len(video_files)} cards successfully exported to "{config.export_filename}"! {failures} failures were reported.')


if __name__ == "__main__":
    main()
