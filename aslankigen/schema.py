"""Generate words.schema.json from WordsConfig and optionally check if it's up to date."""

import json
import sys
from pathlib import Path

from .models import WordsConfig

SCHEMA_FILE = Path("words.schema.json")


def generate() -> str:
    return json.dumps(WordsConfig.model_json_schema(), indent=2) + "\n"


def main() -> None:
    check = "--check" in sys.argv
    expected = generate()

    if check:
        if not SCHEMA_FILE.exists():
            print(f"{SCHEMA_FILE} does not exist. Run: python -m aslankigen.schema")
            sys.exit(1)
        actual = SCHEMA_FILE.read_text()
        if actual != expected:
            print(f"{SCHEMA_FILE} is out of date. Run: python -m aslankigen.schema")
            sys.exit(1)
    else:
        SCHEMA_FILE.write_text(expected)


if __name__ == "__main__":
    main()
