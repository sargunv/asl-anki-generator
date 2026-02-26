import hashlib
import math
from dataclasses import dataclass

import genanki
from rich.progress import MofNCompleteColumn, Progress, ProgressColumn, Task, TextColumn
from rich.style import Style
from rich.text import Text

from . import console
from .models import WordEntry, WordsConfig, resolve_word
from .util import DownloadStatus, download_sign_video

STYLE_CACHED = Style(color="blue")
STYLE_DOWNLOADED = Style(color="green")
STYLE_FAILED = Style(color="red")
STYLE_REMAINING = Style(color="bright_black", dim=True)


@dataclass
class DownloadCounts:
    cached: int = 0
    downloaded: int = 0
    failed: int = 0

    def increment(self, status: DownloadStatus) -> None:
        match status:
            case DownloadStatus.CACHED:
                self.cached += 1
            case DownloadStatus.DOWNLOADED:
                self.downloaded += 1
            case DownloadStatus.FAILED:
                self.failed += 1

    def as_dict(self) -> dict[str, int]:
        return {
            "cached": self.cached,
            "downloaded": self.downloaded,
            "failed": self.failed,
        }


class StatusBarColumn(ProgressColumn):
    """A progress bar with colored segments for cached/downloaded/failed."""

    def __init__(self, bar_width: int = 40) -> None:
        super().__init__()
        self.bar_width = bar_width

    def render(self, task: Task) -> Text:
        total = int(task.total or 0)
        if total == 0:
            return Text("█" * self.bar_width, style=STYLE_REMAINING)

        counts = [
            (task.fields.get("cached", 0), STYLE_CACHED),
            (task.fields.get("downloaded", 0), STYLE_DOWNLOADED),
            (task.fields.get("failed", 0), STYLE_FAILED),
        ]
        done = sum(c for c, _ in counts)
        counts.append((total - done, STYLE_REMAINING))

        # Proportional widths, but guarantee 1 char for any non-zero segment
        raw = [c / total * self.bar_width for c, _ in counts]
        widths = [max(1, math.floor(r)) if c > 0 else 0 for r, (c, _) in zip(raw, counts)]
        # Adjust largest segment so widths sum to exactly bar_width
        diff = self.bar_width - sum(widths)
        largest = max(range(len(counts)), key=lambda i: counts[i][0])
        widths[largest] += diff
        widths[largest] = max(1, widths[largest])

        bar = Text()
        for w, (_, style) in zip(widths, counts):
            bar.append("█" * w, style=style)
        return bar


class StatusCountsColumn(ProgressColumn):
    """Shows cached/downloaded/failed counts with matching colors."""

    def render(self, task: Task) -> Text:
        cached = task.fields.get("cached", 0)
        downloaded = task.fields.get("downloaded", 0)
        failed = task.fields.get("failed", 0)

        parts = Text()
        parts.append(f"{cached} cached", style=STYLE_CACHED)
        parts.append(", ")
        parts.append(f"{downloaded} downloaded", style=STYLE_DOWNLOADED)
        if failed:
            parts.append(", ")
            parts.append(f"{failed} failed", style=STYLE_FAILED)
        return parts


def _deck_id(name: str) -> int:
    """Generate a stable deck ID from a deck name, constrained to genanki's valid range."""
    hash_bytes = hashlib.sha256(name.encode()).digest()
    raw = int.from_bytes(hash_bytes[:4], "big")
    return (raw % (1 << 30)) + (1 << 30)


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

    total_words = sum(len(word_set.words) for group in config.groups for word_set in group.sets)

    counts = DownloadCounts()

    console.print("[bold]Generating ASL Anki Deck[/bold]")

    with Progress(
        StatusBarColumn(bar_width=40),
        MofNCompleteColumn(),
        TextColumn("{task.description}", style="dim"),
        StatusCountsColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "Processing words",
            total=total_words,
            cached=counts.cached,
            downloaded=counts.downloaded,
            failed=counts.failed,
        )

        for group in config.groups:
            deck_name = f"{config.name}::{group.name}"
            deck = genanki.Deck(_deck_id(deck_name), deck_name)

            for word_set in group.sets:
                for raw_entry in word_set.words:
                    entry = resolve_word(raw_entry)
                    progress.update(task, description=f"{entry.word}")
                    video_file, status = download_sign_video(entry.resolved_filename, entry.resolved_url)
                    if not video_file:
                        failures += 1
                    else:
                        deck.add_note(generate_note(entry, word_set.tags))
                        video_files.append(str(video_file))

                    counts.increment(status)
                    progress.update(
                        task,
                        advance=1,
                        cached=counts.cached,
                        downloaded=counts.downloaded,
                        failed=counts.failed,
                    )

            decks.append(deck)

        progress.update(task, description="Done")

    return (decks, video_files, failures)
