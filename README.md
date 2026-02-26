# ASL Anki Flashcard Deck Generator

Give it a list of words, it'll give you an Anki flashcard deck with the word as a question and a video of the sign as the answer. It'll even find the video for you!

## Usage

1. Clone the repository:
```bash
git clone https://github.com/ji-mmyliu/asl-anki-generator.git
cd asl-anki-generator
```

2. Install dependencies (requires [uv](https://docs.astral.sh/uv/)):
```bash
uv sync
```

3. Copy `words.json.sample` to `words.json` and edit it with your word list.

4. Generate the Anki deck:
```bash
uv run python quick_run.py
```

The generated `.apkg` file can be imported directly into Anki.

## Server

You can also run the FastAPI server to generate decks via API:
```bash
uv run uvicorn server:app --reload
```

## Tests

```bash
uv run pytest
```

## Credits

- Uses kerrickstaley's [genanki](https://github.com/kerrickstaley/genanki) Python library
- Uses the [handspeak](https://www.handspeak.com/) ASL dictionary for signs
