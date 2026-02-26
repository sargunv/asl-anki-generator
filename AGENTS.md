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

### Word variants

HandSpeak often has multiple videos for a word (e.g., `how.mp4`, `how2.mp4`,
`how-1913.mp4`). Word entries in `words.json` support an optional `filename`
field to select a specific variant:

```json
"words": [
  "hello",
  { "word": "how", "filename": "how2", "hint": "as in 'how are you'" }
]
```

- Plain strings work as before (filename defaults to the word itself)
- `filename` overrides which `.mp4` to fetch from HandSpeak
- `hint` adds context to the card front, e.g. "How (as in 'how are you')"

### Word entry format

Word entries in `words.json` can be either:

- A **plain string** like `"hello"` -- the HandSpeak path is derived
  automatically using `get_handspeak_path()` (standard `/word/` patterns)
- A **WordEntry object** with a required `path` field pointing to the video on
  HandSpeak, plus an optional `hint`:

```json
"words": [
  "hello",
  { "word": "how are you", "path": "/word/h/how/how-you.mp4" },
  { "word": "your name what", "path": "/lang/n/name/you-name-what.mp4" }
]
```

- `word` -- the display text for the card front (capitalized automatically)
- `path` -- the HandSpeak URL path (prepended with `https://www.handspeak.com`);
  the local filename is derived from the basename
- `hint` -- optional context shown on the card front, e.g.
  `"How (as in 'how do you know')"`

Use a WordEntry object when:

- The video is at a non-standard path (e.g. `/lang/` instead of `/word/`)
- You want a specific variant video (e.g. `how-you.mp4` instead of `how.mp4`)
- The card text differs from the HandSpeak filename (e.g. "how are you" using
  `how-you.mp4`)

### Searching HandSpeak

HandSpeak has a JSON search API that can be used to find words and their page
IDs:

```
https://www.handspeak.com/word/app/search-dict.php?q={query}&lp=1
```

The response includes a word list with sign IDs and URLs:

```json
{
  "ok": true,
  "query": "how",
  "wordlist": [
    { "signID": 1067, "signName": "how", "url": "/word/1067/" }
  ],
  "word": { "signID": 1067, "signName": "how", "url": "/word/1067/" },
  "media": [...]
}
```

Once you have the page URL (e.g. `/word/1067/`), you can fetch the HTML and grep
for `.mp4` references to discover all video variants for that word. For example,
the "how" page has `how.mp4`, `how2.mp4`, `how-you.mp4`, `how-many.mp4`,
`how-much.mp4`, `how-1913.mp4`, and `how-oldvar.mp4`.

The search API only indexes individual words, not multi-word phrases. Phrases
like "nice to meet you" won't return results -- you need to search for each word
separately and check their individual pages for phrase variants.

### Important notes

- Downloads require a `User-Agent` header (the code uses `Mozilla/5.0`)
- There is a 3-second rate limit between downloads (`DOWNLOAD_INTERVAL`)
- Videos are cached locally in `videos/` directory; existing files are skipped
- Not all words may have videos on HandSpeak; failures are logged and skipped
