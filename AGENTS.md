# Agent Notes

## Project Overview

Generates Anki `.apkg` decks for learning ASL. Downloads sign videos from
HandSpeak.com, packages them into cards (front = English word, back = video).

### Key Files

- `words.json` - Word list organized into groups > sets (with tags)
- `aslankigen/models.py` - Pydantic models (`WordsConfig` > `Group` > `WordSet`)
- `aslankigen/util.py` - Video download + HandSpeak URL construction
- `aslankigen/generate.py` - Anki deck/note generation via `genanki`
- `aslankigen/__main__.py` - Entry point

## HandSpeak Reference

### Default video URL pattern

```
https://www.handspeak.com/word/{first_char}/{first_3_chars}/{word}.mp4
```

Single letters use: `/word/{letter}/{letter}-abc.mp4`

### Word entry format in words.json

- **Plain string** `"hello"` -- path derived automatically
- **WordEntry object** when the video path doesn't match the default pattern:

```json
{ "word": "high school", "path": "/word/h/hig/high-school.mp4" }
{ "word": "how", "path": "/word/h/how/how2.mp4", "hint": "as in 'how are you'" }
```

Use a WordEntry when: multi-word phrases, non-standard paths, specific variant
videos, or when the display text differs from the filename.

### Search API

```
https://www.handspeak.com/word/app/search-dict.php?q={query}&lp=1
```

Returns `{ "word": { "signID": 1067, "url": "/word/1067/" }, ... }`. The page
HTML contains `<video src="...">` tags with all video variants. The API only
indexes single words, not phrases.

## Workflow: Adding Words to words.json

When adding words, **always verify** both dictionary existence and video paths
before writing to `words.json`. Use a subagent to keep the context window small.

### Step 1: Search the dictionary

Batch-fetch the search API for all words in parallel:

```
https://www.handspeak.com/word/app/search-dict.php?q={word}&lp=1
```

Confirm each word exists and note the page URL (sign ID).

### Step 2: Verify video paths via subagent

Launch an `explore` subagent to fetch each word's page HTML and extract the
first `<video src="...mp4">` path. The subagent should return a table of:

- Word
- Actual video `src` path from the page
- Whether it matches the default URL pattern

This keeps the large HTML responses out of the main context window.

### Step 3: Write the entries

- Words matching the default pattern -> plain strings
- Words that don't match (multi-word, variants, non-standard paths) -> WordEntry
  objects with explicit `path`
- Add `hint` when a word has multiple meanings and context helps

### Notes

- Downloads require a `User-Agent` header (code uses `Mozilla/5.0`)
- 3-second rate limit between downloads
- Videos cached in `videos/`; existing files are skipped
