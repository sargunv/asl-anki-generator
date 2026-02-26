"""Generate words.schema.json from WordsConfig and optionally check if it's up to date."""

import json
import subprocess
import sys

from .models import WordsConfig

SCHEMA_FILE = "words.schema.json"


def generate() -> str:
    raw = json.dumps(WordsConfig.model_json_schema()) + "\n"
    result = subprocess.run(
        ["dprint", "fmt", "--stdin", SCHEMA_FILE],
        input=raw,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def main() -> None:
    check = "--check" in sys.argv
    expected = generate()

    if check:
        with open(SCHEMA_FILE) as f:
            actual = f.read()
        if actual != expected:
            print(f"{SCHEMA_FILE} is out of date. Run: python -m aslankigen.schema")
            sys.exit(1)
    else:
        with open(SCHEMA_FILE, "w") as f:
            f.write(expected)


if __name__ == "__main__":
    main()
