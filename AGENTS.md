# Agent Notes

## Project Overview

This project generates Anki flashcard decks (`.apkg` files) for learning ASL
(American Sign Language). It downloads sign videos from HandSpeak.com and
packages them into Anki cards where the front shows the English word and the
back plays the sign video.

### Architecture

- `words.json` - Configuration file listing all words organized into groups and
  sets with tags
- `words.schema.json` - Auto-generated JSON Schema from the Pydantic model (via
  `schema.py`)
- `aslankigen/models.py` - Pydantic models: `WordsConfig` > `Group` > `WordSet`
  > words
- `aslankigen/util.py` - Video download logic and HandSpeak URL construction
- `aslankigen/generate.py` - Anki deck/note generation using `genanki`
- `aslankigen/__main__.py` - Entry point: reads config, generates decks, writes
  `.apkg`

### Flow

1. Read and validate `words.json` against `WordsConfig` Pydantic model
2. For each word, download the `.mp4` video from HandSpeak (with 3s rate
   limiting)
3. Create Anki notes: front = capitalized word, back = `[sound:{word}.mp4]`
4. Package all decks and media into a single `.apkg` file

## HandSpeak Video URL Patterns

HandSpeak (handspeak.com) is an ASL dictionary site. Videos are served as `.mp4`
files with specific URL patterns.

### Standard words (3+ characters)

```
https://www.handspeak.com/word/{first_char}/{first_3_chars}/{word}.mp4
```

Examples:

- `hello` -> `/word/h/hel/hello.mp4`
- `hi` -> `/word/h/hi/hi.mp4` (short words just use what they have)
- `twenty-one` -> `/word/t/twe/twenty-one.mp4` (hyphens preserved)

### Single alphabet letters

Alphabet letter videos use a **different** URL pattern than regular words:

```
https://www.handspeak.com/word/{letter}/{letter}-abc.mp4
```

Examples:

- `a` -> `/word/a/a-abc.mp4`
- `z` -> `/word/z/z-abc.mp4`

These videos are sourced from HandSpeak's manual alphabet chart page
(`/learn/408/`). They show the fingerspelling handshape for each letter.

### Important notes

- Downloads require a `User-Agent` header (the code uses `Mozilla/5.0`)
- There is a 3-second rate limit between downloads (`DOWNLOAD_INTERVAL`)
- Videos are cached locally in `videos/` directory; existing files are skipped
- Not all words may have videos on HandSpeak; failures are logged and skipped
